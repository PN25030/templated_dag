# Step 1: Get the project number dynamically
data "google_project" "my_project" {
  project_id = var.project_id
}

# Step 2: Create the service email using the project number
locals {
  service_email = "${data.google_project.my_project.number}@serviceemail.com"
}

# Step 3: Assign the IAM role to the service email
resource "google_project_iam_member" "service_email_role" {
  project = data.google_project.my_project.project_id
  role    = "roles/editor"  # Replace with the role you want
  member  = "serviceAccount:${local.service_email}"
}

# Optional: Define the project ID as a variable
variable "project_id" {
  description = "The project ID where resources will be created"
  type        = string
}