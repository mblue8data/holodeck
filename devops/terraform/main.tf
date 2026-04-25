terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3  = "http://localstack:4566"
    iam = "http://localstack:4566"
    sts = "http://localstack:4566"
  }
}

# --- Data Lake Buckets ---

resource "aws_s3_bucket" "raw" {
  bucket = "${var.project}-raw"
}

resource "aws_s3_bucket" "staging" {
  bucket = "${var.project}-staging"
}

resource "aws_s3_bucket" "marts" {
  bucket = "${var.project}-marts"
}

# --- Bucket versioning (good practice to learn) ---

resource "aws_s3_bucket_versioning" "raw" {
  bucket = aws_s3_bucket.raw.id
  versioning_configuration {
    status = "Enabled"
  }
}

# --- IAM role for a pipeline service account ---

resource "aws_iam_role" "pipeline_role" {
  name = "${var.project}-pipeline-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "pipeline_s3" {
  name = "s3-access"
  role = aws_iam_role.pipeline_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
      Resource = [
        aws_s3_bucket.raw.arn,
        "${aws_s3_bucket.raw.arn}/*",
        aws_s3_bucket.staging.arn,
        "${aws_s3_bucket.staging.arn}/*",
        aws_s3_bucket.marts.arn,
        "${aws_s3_bucket.marts.arn}/*",
      ]
    }]
  })
}
