To use the KMS keys created in `terraform-scripts/kms` within the BigQuery tables in `terraform-scripts/bigquery`, we can modify the Terraform setup to output the KMS key’s resource identifier (`self_link` or `name`) from the `kms` module and pass it to the BigQuery module. Here’s how to structure this:

### Folder Structure Update

```
terraform-scripts/
├── main.tf
├── variables.tf
├── outputs.tf
├── locals.tf
├── kms/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── locals.tf
└── bigquery/
    ├── main.tf
    ├── variables.tf
    ├── outputs.tf
    └── locals.tf
```

### 1. **KMS Module**

The `kms` module will output the KMS key’s `self_link` or `name`, which BigQuery needs for encryption.

#### `terraform-scripts/kms/main.tf`

```hcl
resource "google_kms_key_ring" "keyring" {
  name     = var.keyring_name
  location = var.location
}

resource "google_kms_crypto_key" "key" {
  name     = var.key_name
  key_ring = google_kms_key_ring.keyring.id
  purpose  = var.purpose
}

output "kms_key_self_link" {
  value = google_kms_crypto_key.key.self_link
}
```

#### `terraform-scripts/kms/outputs.tf`

```hcl
output "kms_key_self_link" {
  value = google_kms_crypto_key.key.self_link
}
```

### 2. **BigQuery Module**

In the BigQuery module, add a variable to accept the KMS key `self_link` from the `kms` module. Then, use this key for table-level encryption.

#### `terraform-scripts/bigquery/variables.tf`

```hcl
variable "dataset_name" {
  type = string
}

variable "kms_key_self_link" {
  type = string
}

variable "region" {
  type = string
  default = "us-central1"
}
```

#### `terraform-scripts/bigquery/main.tf`

```hcl
resource "google_bigquery_dataset" "dataset" {
  dataset_id   = var.dataset_name
  location     = var.region
  default_encryption_configuration {
    kms_key_name = var.kms_key_self_link
  }
}
```

#### `terraform-scripts/bigquery/outputs.tf`

```hcl
output "dataset_id" {
  value = google_bigquery_dataset.dataset.dataset_id
}
```

### 3. **Root Module Setup**

At the root level, link the `kms` and `bigquery` modules so the output from `kms` flows into `bigquery`.

#### `terraform-scripts/main.tf`

```hcl
provider "google" {
  project = var.project_id
  region  = var.region
}

module "kms" {
  source         = "./kms"
  keyring_name   = var.kms_keyring_name
  location       = var.kms_location
  key_name       = var.kms_key_name
  purpose        = var.kms_purpose
}

module "bigquery" {
  source         = "./bigquery"
  dataset_name   = var.bq_dataset_name
  kms_key_self_link = module.kms.kms_key_self_link
}
```

#### `terraform-scripts/variables.tf`

```hcl
variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "us-central1"
}

# KMS Variables
variable "kms_keyring_name" {
  type = string
}

variable "kms_location" {
  type = string
  default = "global"
}

variable "kms_key_name" {
  type = string
}

variable "kms_purpose" {
  type    = string
  default = "ENCRYPT_DECRYPT"
}

# BigQuery Variables
variable "bq_dataset_name" {
  type = string
}
```

#### `terraform-scripts/outputs.tf`

```hcl
output "kms_key_self_link" {
  value = module.kms.kms_key_self_link
}

output "bigquery_dataset_id" {
  value = module.bigquery.dataset_id
}
```

### Usage

After configuring the variables, run:

```bash
cd terraform-scripts
terraform init
terraform apply -var="project_id=<YOUR_PROJECT_ID>" -var="bq_dataset_name=<YOUR_DATASET_NAME>" -var="kms_keyring_name=<YOUR_KEYRING_NAME>" -var="kms_key_name=<YOUR_KEY_NAME>"
```

This setup allows the KMS key created in the `kms` module to be automatically referenced in the BigQuery dataset configuration in the `bigquery` module.
