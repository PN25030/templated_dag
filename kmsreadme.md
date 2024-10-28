Here’s a setup to modularize the Terraform code for creating a KMS keyring and key, outputting the key, and applying it to BigQuery. This structure assumes you have a `terraform-scripts` folder where each module is organized.

### Folder Structure

```
terraform-scripts/
├── main.tf
├── variables.tf
├── outputs.tf
├── locals.tf
├── modules/
│   ├── kms/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   └── locals.tf
│   └── bigquery/
│       ├── main.tf
│       ├── variables.tf
│       ├── outputs.tf
│       └── locals.tf
```

### 1. **Main Root Files**

These files at the root level define the overall structure and connect the modules.

#### `terraform-scripts/main.tf`

```hcl
provider "google" {
  project = var.project_id
  region  = var.region
}

module "kms" {
  source         = "./modules/kms"
  keyring_name   = var.kms_keyring_name
  location       = var.kms_location
  key_name       = var.kms_key_name
  purpose        = var.kms_purpose
}

module "bigquery" {
  source       = "./modules/bigquery"
  dataset_name = var.bq_dataset_name
  kms_key_name = module.kms.kms_key_self_link
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

#### `terraform-scripts/locals.tf`

Define any reusable local variables if necessary. For now, you can skip it or use it for further modularization.

### 2. **KMS Module**

The KMS module creates the keyring and key.

#### `terraform-scripts/modules/kms/main.tf`

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

#### `terraform-scripts/modules/kms/variables.tf`

```hcl
variable "keyring_name" {
  type = string
}

variable "location" {
  type = string
}

variable "key_name" {
  type = string
}

variable "purpose" {
  type = string
}
```

#### `terraform-scripts/modules/kms/outputs.tf`

```hcl
output "kms_key_self_link" {
  value = google_kms_crypto_key.key.self_link
}
```

### 3. **BigQuery Module**

The BigQuery module will create a dataset and apply the KMS key to it.

#### `terraform-scripts/modules/bigquery/main.tf`

```hcl
resource "google_bigquery_dataset" "dataset" {
  dataset_id   = var.dataset_name
  location     = var.region
  default_encryption_configuration {
    kms_key_name = var.kms_key_name
  }
}
```

#### `terraform-scripts/modules/bigquery/variables.tf`

```hcl
variable "dataset_name" {
  type = string
}

variable "kms_key_name" {
  type = string
}

variable "region" {
  type = string
  default = "us-central1"
}
```

#### `terraform-scripts/modules/bigquery/outputs.tf`

```hcl
output "dataset_id" {
  value = google_bigquery_dataset.dataset.dataset_id
}
```

### Usage

1. Update `terraform-scripts/variables.tf` or pass the variables when running Terraform.
2. Run the commands:

   ```bash
   cd terraform-scripts
   terraform init
   terraform apply -var="project_id=<YOUR_PROJECT_ID>" -var="bq_dataset_name=<YOUR_DATASET_NAME>" -var="kms_keyring_name=<YOUR_KEYRING_NAME>" -var="kms_key_name=<YOUR_KEY_NAME>"
   ```

This structure ensures that your KMS keyring and key creation, as well as BigQuery configurations, are modular, and the outputs are ready to use for integration across services.
