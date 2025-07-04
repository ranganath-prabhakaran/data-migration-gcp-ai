variable "project_id" {
  description = "The GCP project ID to deploy resources into."
  type        = string
}

variable "region" {
  description = "The GCP region for deployment."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone for deployment."
  type        = string
  default     = "us-central1-a"
}

variable "agent_host_vm_name" {
  description = "Name for the GCE instance hosting the AutoGen agents."
  type        = string
  default     = "agent-host-vm"
}

variable "mcp_bridge_vm_name" {
  description = "Name for the GCE instance hosting the MCP server."
  type        = string
  default     = "mcp-bridge-vm"
}

variable "vm_machine_type" {
  description = "Machine type for the GCE instances."
  type        = string
  default     = "e2-medium"
}

variable "target_sql_instance_name" {
  description = "Name for the target Cloud SQL instance."
  type        = string
  default     = "migrated-mysql-instance"
}

variable "target_sql_tier" {
  description = "Machine tier for the Cloud SQL instance."
  type        = string
  default     = "db-n1-standard-1"
}

variable "gcs_bucket_name_prefix" {
  description = "Prefix for the GCS migration bucket name."
  type        = string
  default     = "mysql-migration-bucket"
}

variable "admin_ssh_ip_range" {
  description = "CIDR IP range allowed to SSH into the VMs. Example: 'your_ip/32'."
  type        = string
}