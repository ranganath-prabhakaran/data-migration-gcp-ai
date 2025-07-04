resource "google_compute_network" "vpc_network" {
  name                    = "agentic-migration-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "vpc_subnetwork" {
  name          = "agentic-migration-subnet"
  ip_cidr_range = "10.10.0.0/24"
  region        = var.region
  network       = google_compute_network.vpc_network.id
}

# Reserve an IP range for the Private Services Access connection.
# This is required for services like Cloud SQL with private IPs.
resource "google_compute_global_address" "private_ip_address" {
  name          = "private-ip-for-google-services"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc_network.id
}

# Establish the Private Services Access connection.
resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.vpc_network.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]

  # This depends_on is crucial to ensure the network is ready.
  depends_on = [google_compute_network.vpc_network]
}

resource "google_compute_firewall" "allow_ssh" {
  name    = "allow-ssh-from-admin"
  network = google_compute_network.vpc_network.name
  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
  source_ranges = [var.admin_ssh_ip_range]
  target_tags   = ["ssh"]
}

resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal-traffic"
  network = google_compute_network.vpc_network.name
  allow {
    protocol = "all"
  }
  source_ranges = [google_compute_subnetwork.vpc_subnetwork.ip_cidr_range]
}