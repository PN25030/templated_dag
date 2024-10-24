To pass **encryption configuration** for BigQuery tables, you can add the `encryption_configuration` block in the module for the BigQuery tables. BigQuery allows you to specify **Customer-Managed Encryption Keys (CMEK)** using a Google Cloud KMS key. 

Here’s how you can modify your **`dev.tfvars`** and **`main.tf`** to support encryption configuration.

### Updated `dev.tfvars` with Encryption Configuration

```hcl
# dev.tfvars

# GCP Project ID
project_id  = "dev-project-id"

# BigQuery Dataset ID
dataset_id  = "dev_dataset"

# Location for the dataset
location    = "US"

# Define multiple tables with respective table IDs, schema files, and encryption config
tables = [
  {
    table_id               = "dev_table_1"
    schema_file            = "schema/dev_table_1_schema.json"
    kms_key_name           = "projects/my-project/locations/us/keyRings/my-keyring/cryptoKeys/my-key-1"
  },
  {
    table_id               = "dev_table_2"
    schema_file            = "schema/dev_table_2_schema.json"
    kms_key_name           = "projects/my-project/locations/us/keyRings/my-keyring/cryptoKeys/my-key-2"
  },
  {
    table_id               = "dev_table_3"
    schema_file            = "schema/dev_table_3_schema.json"
    kms_key_name           = "projects/my-project/locations/us/keyRings/my-keyring/cryptoKeys/my-key-3"
  }
]

# Labels for resources
labels = {
  environment = "dev"
  owner       = "team-dev"
}
```

### Explanation of the Update:
- **`kms_key_name`**: For each table, you can specify the Cloud KMS key to use for encryption. This is the resource name of the Cloud KMS key in the format: `projects/[PROJECT_ID]/locations/[LOCATION]/keyRings/[KEY_RING]/cryptoKeys/[KEY_NAME]`.
  
### Update `main.tf` to Pass Encryption Configuration

You need to modify your `main.tf` to pass the encryption configuration to the BigQuery table resources. Here’s how to update it:

```hcl
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

# Loop through the tables and create each one
resource "null_resource" "create_tables" {
  count = length(var.tables)

  # Using a module to create each table
  module "bigquery_table" {
    source      = "./modules/bigquery_table"
    project_id  = var.project_id
    dataset_id  = var.dataset_id
    table_id    = var.tables[count.index].table_id
    schema_file = var.tables[count.index].schema_file

    # Pass encryption configuration if provided
    encryption_configuration = {
      kms_key_name = var.tables[count.index].kms_key_name
    }
  }
}
```

### Variables for Encryption Configuration (`variables.tf`)

In your `variables.tf`, ensure you include the encryption configuration for the table:

```hcl
# variables.tf

variable "project_id" {
  type        = string
  description = "The GCP Project ID to create resources in."
}

variable "dataset_id" {
  type        = string
  description = "The BigQuery Dataset ID."
}

variable "location" {
  type        = string
  description = "BigQuery dataset location."
  default     = "US"
}

variable "labels" {
  type        = map(string)
  description = "A map of labels to assign to resources."
  default     = {}
}

variable "tables" {
  type = list(object({
    table_id        = string
    schema_file     = string
    kms_key_name    = string
  }))
  description = "List of BigQuery tables with their schema files and encryption keys"
}
```

### Modify the BigQuery Module (`modules/bigquery_table`)

In the **`bigquery_table` module**, add the encryption configuration block for the BigQuery table resource. 

Example `main.tf` inside the `bigquery_table` module:

```hcl
# modules/bigquery_table/main.tf

resource "google_bigquery_table" "table" {
  dataset_id = var.dataset_id
  table_id   = var.table_id
  schema     = file(var.schema_file)

  encryption_configuration {
    kms_key_name = var.encryption_configuration.kms_key_name
  }
}
```

### Variables for the BigQuery Table Module (`modules/bigquery_table/variables.tf`)

Add a variable for the encryption configuration:

```hcl
# modules/bigquery_table/variables.tf

variable "dataset_id" {
  type        = string
  description = "The BigQuery Dataset ID."
}

variable "table_id" {
  type        = string
  description = "The BigQuery Table ID."
}

variable "schema_file" {
  type        = string
  description = "The path to the BigQuery table schema file."
}

variable "encryption_configuration" {
  type = object({
    kms_key_name = string
  })
  description = "Customer-managed encryption key for the BigQuery table."
}
```

---

### Summary

1. **Update `dev.tfvars`** to include the `kms_key_name` for each table.
2. **Modify `main.tf`** to pass encryption configuration (CMEK) when creating the tables.
3. **Update the BigQuery table module** to handle encryption configuration via the `kms_key_name`.

This allows you to apply customer-managed encryption (CMEK) for BigQuery tables across multiple environments (e.g., dev, uat, prod) with the same modular approach.

Would you like help with setting up KMS keys, or anything else related to BigQuery encryption?
