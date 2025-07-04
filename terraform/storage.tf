resource "random_id" "bucket_suffix" {
  byte_length = 8
}

resource "google_storage_bucket" "migration_bucket" {
  name          = "${var.gcs_bucket_name_prefix}-${random_id.bucket_suffix.hex}"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}