# terraform/variables.tf


variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  
}

variable "aws_buckets" {
  description = "List of S3 bucket names to create"
  type        = map(object({
    name = string
  }))
}

# variable "silver_public_bucket_name" {
#   description = "Public S3 bucket for Silver layer"
#   type        = string
# }

# variable "gold_public_bucket_name" {
#   description = "Public S3 bucket for Gold layer"
#   type        = string
# }

variable "aws_glue_databases" {
  description = "Glue databases to create for each layer"
  type = map(object({
    name        = string
    description = string
  }))
}


variable "tags" {
  description = "A map of tags to assign to resources"
  type        = map(string)
}

variable "glue_crawler_role_name" {
  description = "IAM role for Glue crawler"
  type        = string
}

variable "glue_job_role_name" {
  description = "IAM role for Glue jobs"
  type        = string
}

variable "athena_role_name" {
  description = "IAM role for Athena"
  type        = string
}

variable "athena_output_path" {
  description = "S3 path for Athena query results"
  type        = string
}
