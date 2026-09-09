variable "project_id" {
  type    = string
  default = "project-643d2a1a-b690-4d08-b00"
}
variable "region" {
  type    = string
  default = "us-central1"
}
variable "zone" {
  type    = string
  default = "us-central1-a"
}
variable "machine_type" {
  type    = string
  default = "e2-standard-4"
}
variable "github_repository" {
  type    = string
  default = "SS2-USAC/apache_airflow_dbt"
}
variable "github_repository_id" {
  type    = string
  default = "1362661689"
}
variable "github_owner_id" {
  type    = string
  default = "316211938"
}
variable "resource_prefix" {
  type    = string
  default = "ss2-airflow-dbt"
}
variable "domain" {
  description = "Dominio opcional apuntando a la IP; vacio usa sslip.io."
  type        = string
  default     = ""
}
