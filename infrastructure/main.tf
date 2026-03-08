# =============================================================================
# VINO PRO IA — Reference infrastructure (documentation only)
# =============================================================================
# This file describes how the application could be deployed on AWS at scale.
# It is NOT executed in production (Render is used for the current MVP).
# Use: terraform plan / apply only in a dedicated AWS account for future migration.
# =============================================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# -----------------------------------------------------------------------------
# S3 — User uploads (avatars, scanned labels, static assets)
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "uploads" {
  bucket = "${var.project_name}-uploads-${var.environment}"

  tags = {
    Project = var.project_name
    Env     = var.environment
  }
}

resource "aws_s3_bucket_versioning" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_cors_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST"]
    allowed_origins = [var.app_origin]
    expose_headers  = ["ETag"]
  }
}

# -----------------------------------------------------------------------------
# RDS — Relational database (users, sessions, future: wines catalog)
# -----------------------------------------------------------------------------
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet"
  subnet_ids = var.private_subnet_ids

  tags = {
    Project = var.project_name
  }
}

resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-${var.environment}"
  engine         = "postgres"
  engine_version = "15"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  storage_encrypted     = true
  db_name               = var.db_name
  username              = var.db_username
  password              = var.db_password
  db_subnet_group_name  = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible   = false
  multi_az              = var.environment == "prod"

  tags = {
    Project = var.project_name
    Env     = var.environment
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "${var.project_name}-rds-"
  vpc_id      = var.vpc_id
  description = "Allow app to RDS"

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = {
    Project = var.project_name
  }
}

# -----------------------------------------------------------------------------
# Application layer — ECS Fargate (API) or Lambda for event-driven scaling
# -----------------------------------------------------------------------------
resource "aws_security_group" "app" {
  name_prefix = "${var.project_name}-app-"
  vpc_id      = var.vpc_id
  description = "VINO PRO API / workers"

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project = var.project_name
  }
}

# Optional: Lambda for async tasks (e.g. vision/IA processing, notifications)
# Uncomment when moving heavy workloads off the main API.
# resource "aws_lambda_function" "vision_processor" {
#   function_name = "${var.project_name}-vision-${var.environment}"
#   runtime       = "python3.11"
#   handler       = "handler.lambda_handler"
#   filename      = "${path.module}/../dist/vision_processor.zip"
#   role          = aws_iam_role.lambda_vision.arn
#   timeout       = 60
#   environment {
#     variables = {
#       GOOGLE_API_KEY = var.google_api_key
#       S3_BUCKET      = aws_s3_bucket.uploads.id
#     }
#   }
# }

# -----------------------------------------------------------------------------
# Variables (to be set in .tfvars or CI)
# -----------------------------------------------------------------------------
variable "aws_region" {
  type    = string
  default = "eu-west-1"
}

variable "project_name" {
  type    = string
  default = "vinopro"
}

variable "environment" {
  type    = string
  default = "staging"
}

variable "app_origin" {
  type        = string
  description = "CORS allowed origin (e.g. https://vinoproia.com)"
  default     = "https://vinoproia.com"
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "db_instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "db_allocated_storage" {
  type    = number
  default = 20
}

variable "db_name" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

# variable "google_api_key" {
#   type      = string
#   sensitive = true
# }

# -----------------------------------------------------------------------------
# Outputs (for CI or other modules)
# -----------------------------------------------------------------------------
output "s3_uploads_bucket" {
  value = aws_s3_bucket.uploads.id
}

output "rds_endpoint" {
  value     = aws_db_instance.main.endpoint
  sensitive  = true
}

output "rds_port" {
  value = aws_db_instance.main.port
}
