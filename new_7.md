Yes, you can loop the `table` creation in the `modules/bigquery/main.tf` by using Terraform's `for_each` or `count` feature. This will allow you to pass multiple table configurations as a list or map, and Terraform will create the corresponding number of tables based on the provided data.

Here’s how you can modify the `modules/bigquery/main.tf` to loop over tables:

### Updated `modules/bigquery/main.tf`

```hcl
resource "google_bigquery_dataset" "dataset" {
  dataset_id = var.dataset_id
  project    = var.project_id
  location   = var.location
}

resource "google_bigquery_table" "table" {
  for_each = var.tables

  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = each.value["table_id"]
  schema     = file(each.value["schema_file"])
  description = each.value["description"]
}
```

### Updated `modules/bigquery/variables.tf`

```hcl
variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
}

variable "location" {
  description = "BigQuery Dataset location"
  type        = string
  default     = "US"
}

variable "dataset_id" {
  description = "The BigQuery dataset ID"
  type        = string
}

variable "tables" {
  description = "A list of tables to create"
  type = list(object({
    table_id    = string
    schema_file = string
    description = string
  }))
}
```

### Example Input in `main.tf`

When calling the `bigquery` module in your `main.tf`, you can pass the list of tables dynamically like this:

```hcl
module "bigquery" {
  source     = "./modules/bigquery"
  dataset_id = "my_dataset"
  
  tables = [
    {
      table_id    = "table1"
      schema_file = "${path.module}/schema1.json"
      description = "First table"
    },
    {
      table_id    = "table2"
      schema_file = "${path.module}/schema2.json"
      description = "Second table"
    }
  ]
}
```

### Explanation:
- The `for_each` loop iterates over the list of tables provided in the `tables` variable.
- Each table is created with its corresponding `table_id`, `schema_file`, and `description` values.
- The schema files are provided dynamically, allowing you to specify different schemas for each table.

This method is flexible and allows for easy scaling by adding more table configurations to the `tables` variable without duplicating resources manually.
