output "raw_bucket" {
  value = aws_s3_bucket.raw.bucket
}

output "staging_bucket" {
  value = aws_s3_bucket.staging.bucket
}

output "marts_bucket" {
  value = aws_s3_bucket.marts.bucket
}

output "pipeline_role_arn" {
  value = aws_iam_role.pipeline_role.arn
}
