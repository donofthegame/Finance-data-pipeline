# terraform/outputs.tf

output "s3_buckets_names" {
  description = "List of S3 bucket names created"
  value       = { for k, v in module.s3_buckets : k => v.bucket_name }
  
}

output "s3_buckets_arns" {
  description = "List of S3 bucket ARNs created"
  value       = { for k, v in module.s3_buckets : k => v.bucket_arn }
}


output "glue_databases" {
  value = module.glue.aws_glue_databases
}


#### below output are optional and can be removed if not needed
output "glue_job_role_arn" {
  value = module.iam.glue_job_role_arn
}

output "athena_role_arn" {
  value = module.iam.athena_role_arn
}
output "glue_crawler_role_arn" {
  value = module.iam.glue_crawler_role_arn
}


# output "silver_public_bucket_name" {
#   description = "Public Silver S3 bucket name"
#   value       = module.silver_public_bucket.bucket_name
# }

# output "silver_public_bucket_arn" {
#   description = "Public Silver S3 bucket ARN"
#   value       = module.silver_public_bucket.bucket_arn
# }

# output "gold_public_bucket_name" {
#   description = "Public Gold S3 bucket name"
#   value       = module.gold_public_bucket.bucket_name
# }

# output "gold_public_bucket_arn" {
#   description = "Public Gold S3 bucket ARN"
#   value       = module.gold_public_bucket.bucket_arn
# }
