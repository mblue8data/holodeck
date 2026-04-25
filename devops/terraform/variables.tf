variable "project" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "holodeck"
}

variable "aws_region" {
  description = "AWS region (LocalStack ignores this but it must be set)"
  type        = string
  default     = "us-east-1"
}
