# Infrastructure (reference only)

This folder contains **reference Terraform** for a possible AWS deployment. It is **not used** by the current production stack (Render).

- **`main.tf`**: Conceptual AWS layout — S3 (uploads/avatars), RDS (PostgreSQL), security groups. Optional Lambda placeholder for vision/IA at scale.
- **Usage**: Run `terraform plan` / `apply` only in a dedicated AWS account when/if migrating. Set variables via `terraform.tfvars` or CI (never commit secrets).

No `terraform apply` is executed from this repo in production.
