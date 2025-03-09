provider "google" {
  project = var.project_id
  region  = var.region
}

# Create Dataplex Lake
resource "google_dataplex_lake" "lake" {
  name     = var.lake_name
  location = var.region
  labels   = var.labels

  display_name = "Dataplex Lake - ${var.lake_name}"
  description  = "This is a Dataplex lake for managing data."

  lifecycle {
    prevent_destroy = false
  }
}

# Create Dataplex Zone
resource "google_dataplex_zone" "zone" {
  name     = var.zone_name
  lake     = google_dataplex_lake.lake.name
  location = var.region
  type     = var.zone_type

  discovery_spec {
    enabled             = var.discovery_enabled
    include_patterns    = var.include_patterns
    exclude_patterns    = var.exclude_patterns
    schedule            = var.discovery_schedule
  }

  labels        = var.labels
  display_name  = "Dataplex Zone - ${var.zone_name}"
  description   = "Managed zone for structured/unstructured data."
}

# Create Dataplex Asset
resource "google_dataplex_asset" "asset" {
  name     = var.asset_name
  lake     = google_dataplex_lake.lake.name
  zone     = google_dataplex_zone.zone.name
  location = var.region

  resource_spec {
    name = var.asset_resource_name
    type = var.asset_resource_type
  }

  labels        = var.labels
  display_name  = "Dataplex Asset - ${var.asset_name}"
  description   = "An asset associated with the Dataplex zone."
}