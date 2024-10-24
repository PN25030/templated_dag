# main.tf

provider "google" {
  project = var.project_id
  region  = "us-central1"
}

# Create BigQuery Dataset
module "bigquery" {
  source      = "./modules/bigquery"
  project_id  = var.project_id
  dataset_id  = var.dataset_id
  location    = var.location
  labels      = var.labels
}

# Loop through the tables using `for_each` and create each one
module "bigquery_table" {
  source      = "./modules/bigquery_table"
  
  for_each    = { for table in var.tables : table.table_id => table }

  project_id  = var.project_id
  dataset_id  = var.dataset_id
  table_id    = each.value.table_id
  schema_file = each.value.schema_file

  # Pass encryption configuration if provided
  encryption_configuration = {
    kms_key_name = each.value.kms_key_name
  }
}
