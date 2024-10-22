provider "google" {
  credentials = file(var.google_credentials_file)
  project     = var.project_id
  region      = "us-central1"  # Replace with your region
}

variable "project_id" {}
variable "google_credentials_file" {}
