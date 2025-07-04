resource "google_service_account" "vm_service_account" {
  account_id   = "migration-vm-sa"
  display_name = "Service Account for Migration VMs"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.vm_service_account.email}"
}

resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.vm_service_account.email}"
}

resource "google_project_iam_member" "dms_admin" {
  project = var.project_id
  role    = "roles/datamigration.admin"
  member  = "serviceAccount:${google_service_account.vm_service_account.email}"
}

resource "google_project_iam_member" "sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.vm_service_account.email}"
}

resource "google_compute_instance" "agent_host" {
  project      = var.project_id
  zone         = var.zone
  name         = var.agent_host_vm_name
  machine_type = var.vm_machine_type
  tags         = ["agent-host", "ssh"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.vpc_subnetwork.id
    access_config {
      // Ephemeral public IP for SSH access
    }
  }

  service_account {
    email  = google_service_account.vm_service_account.email
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y python3-pip git docker.io
    pip3 install --upgrade pip
    pip3 install autogen-agentchat==0.6.1 google-cloud-secret-manager pyyaml PyMySQL
  EOF

  depends_on = [google_project_iam_member.sql_client]
}

resource "google_compute_instance" "mcp_bridge" {
  project      = var.project_id
  zone         = var.zone
  name         = var.mcp_bridge_vm_name
  machine_type = var.vm_machine_type
  tags         = ["mcp-bridge", "ssh"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network    = google_compute_network.vpc_network.id
    subnetwork = google_compute_subnetwork.vpc_subnetwork.id
    access_config {
      // Ephemeral public IP for SSH access
    }
  }
  
  service_account {
    email  = google_service_account.vm_service_account.email
    scopes = ["cloud-platform"]
  }

  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y python3-pip git mydumper
    pip3 install --upgrade pip
    pip3 install mcp==1.0.6 pymysql pyyaml google-cloud-secret-manager
  EOF

  depends_on = [google_project_iam_member.sql_client]
}