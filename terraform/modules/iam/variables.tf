variable "glue_crawler_role_name" {
  description = "IAM role name for AWS Glue crawler"
  type        = string
}

variable "glue_job_role_name" {
  description = "IAM role name for AWS Glue job"
  type        = string
}

variable "tags" {
  description = "Tags to apply to all IAM roles"
  type        = map(string)
}

variable "athena_role_name" {
  description = "IAM role name for Athena"
  type        = string
}

