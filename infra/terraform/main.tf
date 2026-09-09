locals {
  root = abspath("${path.module}/../..")
  host = var.domain != "" ? var.domain : "airflow-dbt.${google_compute_address.airflow.address}.sslip.io"
  files = toset(concat(
    ["Dockerfile"],
    tolist(fileset(local.root, "runtime/**")),
    tolist(fileset(local.root, "scripts/runtime/*.py")),
    tolist(fileset(local.root, "dbt_config/*.yml")),
    tolist(fileset(local.root, "dags/*.py")),
    [for f in fileset(local.root, "dbt/**") : f if !can(regex("/(target|logs|dbt_packages|__pycache__)/|/\\.", f))]
  ))
}

resource "google_project_service" "apis" {
  for_each = toset([
    "compute.googleapis.com", "iam.googleapis.com", "iamcredentials.googleapis.com",
    "sts.googleapis.com", "storage.googleapis.com", "secretmanager.googleapis.com",
    "iap.googleapis.com", "cloudresourcemanager.googleapis.com"
  ])
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_storage_bucket" "releases" {
  name                        = "${var.project_id}-s8-airflow-dbt"
  location                    = var.region
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  force_destroy               = false
  versioning { enabled = true }
  lifecycle_rule {
    condition { num_newer_versions = 5 }
    action { type = "Delete" }
  }
  depends_on = [google_project_service.apis]
}

resource "google_service_account" "runtime" {
  account_id   = "${var.resource_prefix}-vm"
  display_name = "SS2 semana 8 runtime"
  depends_on   = [google_project_service.apis]
}
resource "google_service_account" "github" {
  account_id   = "${var.resource_prefix}-gh"
  display_name = "SS2 semana 8 deploy GitHub"
  depends_on   = [google_project_service.apis]
}
resource "google_storage_bucket_iam_member" "reader" {
  bucket = google_storage_bucket.releases.name
  role   = "roles/storage.objectViewer"
  member = google_service_account.runtime.member
}
resource "google_storage_bucket_iam_member" "writer" {
  bucket = google_storage_bucket.releases.name
  role   = "roles/storage.objectAdmin"
  member = google_service_account.github.member
}

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "${var.resource_prefix}-gh"
  display_name              = "SS2 semana 8 GitHub"
  depends_on                = [google_project_service.apis]
}
resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  attribute_mapping = {
    "google.subject"                = "assertion.sub"
    "attribute.repository"          = "assertion.repository"
    "attribute.repository_id"       = "assertion.repository_id"
    "attribute.repository_owner_id" = "assertion.repository_owner_id"
  }
  attribute_condition = "assertion.repository_id == '${var.github_repository_id}' && assertion.repository_owner_id == '${var.github_owner_id}' && assertion.ref == 'refs/heads/main' && assertion.workflow_ref == '${var.github_repository}/.github/workflows/taller.yml@refs/heads/main' && assertion.event_name in ['push', 'workflow_dispatch']"
  oidc { issuer_uri = "https://token.actions.githubusercontent.com" }
}
resource "google_service_account_iam_member" "wif" {
  service_account_id = google_service_account.github.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository_id/${var.github_repository_id}"
}

resource "random_password" "secret" {
  for_each = toset(["admin", "viewer", "warehouse", "metadata", "jwt", "api"])
  length   = 40
  special  = false
}
resource "random_id" "fernet" { byte_length = 32 }
resource "google_secret_manager_secret" "runtime" {
  secret_id = "${var.resource_prefix}-runtime"
  replication {
    auto {}
  }
  depends_on = [google_project_service.apis]
}
resource "google_secret_manager_secret_version" "runtime" {
  secret = google_secret_manager_secret.runtime.id
  secret_data = jsonencode(merge(
    { for name, value in random_password.secret : name => value.result },
    { fernet = "${random_id.fernet.b64_url}=" }
  ))
}
resource "google_secret_manager_secret_iam_member" "runtime" {
  secret_id = google_secret_manager_secret.runtime.id
  role      = "roles/secretmanager.secretAccessor"
  member    = google_service_account.runtime.member
}

resource "google_compute_network" "lab" {
  name                    = "${var.resource_prefix}-vpc"
  auto_create_subnetworks = false
  depends_on              = [google_project_service.apis]
}
resource "google_compute_subnetwork" "lab" {
  name          = "${var.resource_prefix}-subnet"
  ip_cidr_range = "10.88.0.0/24"
  region        = var.region
  network       = google_compute_network.lab.id
}
resource "google_compute_firewall" "web" {
  name          = "${var.resource_prefix}-web"
  network       = google_compute_network.lab.id
  source_ranges = ["0.0.0.0/0"]
  target_tags   = [var.resource_prefix]
  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }
}
resource "google_compute_firewall" "iap" {
  name          = "${var.resource_prefix}-iap-ssh"
  network       = google_compute_network.lab.id
  source_ranges = ["35.235.240.0/20"]
  target_tags   = [var.resource_prefix]
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}
resource "google_compute_address" "airflow" {
  name       = "${var.resource_prefix}-ip"
  region     = var.region
  depends_on = [google_project_service.apis]
}

data "archive_file" "bootstrap" {
  type        = "zip"
  output_path = "${path.module}/.generated/bootstrap.zip"
  dynamic "source" {
    for_each = local.files
    content {
      content  = file("${local.root}/${source.value}")
      filename = source.value
    }
  }
}
resource "google_storage_bucket_object" "bootstrap" {
  bucket = google_storage_bucket.releases.name
  name   = "bootstrap/${data.archive_file.bootstrap.output_sha256}.zip"
  source = data.archive_file.bootstrap.output_path
}
resource "google_compute_instance" "airflow" {
  name         = var.resource_prefix
  zone         = var.zone
  machine_type = var.machine_type
  tags         = [var.resource_prefix]
  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2404-lts-amd64"
      size  = 50
      type  = "pd-balanced"
    }
  }
  network_interface {
    subnetwork = google_compute_subnetwork.lab.id
    access_config { nat_ip = google_compute_address.airflow.address }
  }
  service_account {
    email  = google_service_account.runtime.email
    scopes = ["cloud-platform"]
  }
  metadata = {
    enable-oslogin = "TRUE"
    startup-script = templatefile("${path.module}/startup.sh.tftpl", {
      bucket  = google_storage_bucket.releases.name
      object  = google_storage_bucket_object.bootstrap.name
      secret  = google_secret_manager_secret.runtime.secret_id
      project = var.project_id
      host    = local.host
    })
  }
  labels     = { course = "ss2", week = "8", tool = "airflow-dbt" }
  depends_on = [google_storage_bucket_iam_member.reader, google_secret_manager_secret_iam_member.runtime, google_secret_manager_secret_version.runtime]
}
