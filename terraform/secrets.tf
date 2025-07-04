resource "google_secret_manager_secret" "source_db_password" {
  secret_id = "source-db-password"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret" "target_db_password" {
  secret_id = "target-db-password"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "target_db_password_version" {
  secret       = google_secret_manager_secret.target_db_password.id
  secret_data  = random_password.target_db_password.result
  depends_on   = [google_secret_manager_secret.target_db_password]
}

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  replication {
    automatic = true
  }
}