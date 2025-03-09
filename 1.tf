variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region (e.g., us-central1)"
  type        = string
}

variable "lake_name" {
  description = "Name of the Dataplex Lake"
  type        = string
}

variable "zone_name" {
  description = "Name of the Dataplex Zone"
  type        = string
}

variable "zone_type" {
  description = "Type of the Dataplex Zone (RAW or CURATED)"
  type        = string
  default     = "RAW"
}

variable "asset_name" {
  description = "Name of the Dataplex Asset"
  type        = string
}

variable "asset_resource_name" {
  description = "Resource Name (GCS Bucket or BigQuery Dataset)"
  type        = string
}

variable "asset_resource_type" {
  description = "Resource Type (STORAGE_BUCKET or BIGQUERY_DATASET)"
  type        = string
}

variable "labels" {
  description = "Labels to apply"
  type        = map(string)
  default     = {}
}

variable "discovery_enabled" {
  description = "Enable automatic discovery"
  type        = bool
  default     = true
}

variable "discovery_schedule" {
  description = "Discovery schedule (e.g., every 24h)"
  type        = string
  default     = "every 24h"
}

variable "include_patterns" {
  description = "List of include patterns for discovery"
  type        = list(string)
  default     = []
}

variable "exclude_patterns" {
  description = "List of exclude patterns for discovery"
  type        = list(string)
  default     = []
}