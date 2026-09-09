output "airflow_url" { value = "https://${local.host}" }
output "vm_name" { value = google_compute_instance.airflow.name }
output "vm_zone" { value = google_compute_instance.airflow.zone }
output "dag_bucket" { value = google_storage_bucket.releases.name }
output "github_service_account" { value = google_service_account.github.email }
output "workload_identity_provider" { value = google_iam_workload_identity_pool_provider.github.name }
output "runtime_secret" { value = google_secret_manager_secret.runtime.secret_id }
output "admin_password" {
  value     = random_password.secret["admin"].result
  sensitive = true
}
output "viewer_password" {
  value     = random_password.secret["viewer"].result
  sensitive = true
}
