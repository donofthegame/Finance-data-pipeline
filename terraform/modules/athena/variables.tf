variable "athena_output_path" {
  description = "S3 path for Athena query results"
  type        = string
}

variable "tags" {
  description = "Tags to apply to Athena resources"
  type        = map(string)
}
