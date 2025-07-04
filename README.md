Agentic Framework for MySQL to GCP Migration via MCP

This repository contains a production-ready, end-to-end solution for migrating a legacy MySQL database to Google Cloud SQL for MySQL. The migration is fully automated by a team of AI agents built with Microsoft AutoGen v0.6.1.
A core and non-negotiable principle of this architecture is the use of the Model Context Protocol (MCP) as the sole, secure interface to the legacy database.

Architecture Overview

The solution operates on a secure, multi-component architecture within a custom GCP VPC:
Agent Host: A GCE VM running the AutoGen multi-agent application. This is the "brain" of the operation.
MCP Bridge: A hardened GCE VM running a custom Python MCP server. This is the secure "gateway" to the legacy database.
GCP Services:
Cloud SQL for MySQL: The target managed database.
Cloud Storage: Staging for database dumps.
Database Migration Service (DMS): Leveraged for medium-sized migrations.
Secret Manager: Securely stores all credentials.
Agent Team: A team of six specialized agents orchestrates the entire workflow:
Environment Setup Agent: Verifies GCP resource readiness.
Schema Conversion Agent: Analyzes the source schema for compatibility.
Data Migration Agent: Dynamically selects and executes the best migration strategy based on DB size.
Data Validation Agent: Ensures data integrity post-migration using row counts and checksums.
Anomaly Detection Agent: Scans logs for errors and performance issues.
Performance Optimization Agent: Provides post-migration recommendations for GCP cost and performance tuning.

Prerequisites

A Google Cloud Platform project with billing enabled.
(https://cloud.google.com/sdk/docs/install) installed and configured locally.
(https://developer.hashicorp.com/terraform/install) installed locally.
Required APIs enabled in your GCP project (Compute, SQL Admin, Storage, Secret Manager, DMS).

Quick Start Guide

Clone the Repository
git clone <git url>


Configure Terraform
Create a file at terraform/terraform.tfvars.
Add your project ID: project_id = "your-gcp-project-id"
Deploy Infrastructure
Bash
cd terraform
terraform init
terraform apply --auto-approve


Add Secrets
Go to the GCP Secret Manager console.
Add new versions with your actual values for:
source-db-host, source-db-user, source-db-password, source-db-name
target-db-password (get the generated value from terraform output target_db_password)
gemini-api-key
Run the Migration
SSH into the newly created agent-host-vm.
Bash
gcloud compute ssh agent-host-vm --zone=us-central1-a


Inside the VM, clone the repo and run the main script.
Bash
git clone <this_repo_url>
cd gcp-agentic-migration
python3 main.py --task "Migrate the 'employees' database."


Testing

To run the included unit tests:

Bash


# Inside the agent-host-vm
cd gcp-agentic-migration/
pip3 install pytest
pytest tests/



Cleanup

IMPORTANT: To avoid incurring costs, destroy all resources when you are finished.

Bash


# From your local machine
cd terraform/
terraform destroy --auto-approve