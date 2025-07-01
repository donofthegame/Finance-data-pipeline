# modules/s3_buckets/variables.tf

variable "bucket_name" {
  description = "The name of the S3 bucket to create"
  type        = string
  
}

variable "tags" {
  description = "Tags to set for the bucket"
  type        = map(string)
}

