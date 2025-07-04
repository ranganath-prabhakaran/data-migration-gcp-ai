resource "google_sql_database_instance" "target_instance" {
  name             = var.target_sql_instance_name
  database_version = "MYSQL_8_0"
  region           = var.region

  settings {
    tier = var.target_sql_tier
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc_network.id
    }
    disk_size = 20
    disk_type = "PD_SSD"
  }

  deletion_protection = false
  depends_on = [
    google_service_networking_connection.private_vpc_connection
  ]
}

resource "random_password" "target_db_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+{}<>:?"
}

resource "google_sql_user" "root_user" {
  name     = "root"
  instance = google_sql_database_instance.target_instance.name
  password = random_password.target_db_password.result
}

output "target_db_password_value" {
  value     = random_password.target_db_password.result
  sensitive = true
}