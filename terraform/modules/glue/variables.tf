variable "databases" {
  description = "Map of AWS Glue database names to create"
  type = map(object({
    name        = string
    description = string
  }))
}

variable "tags" {
  description = "Tags to assign to Glue resources"
  type        = map(string)
}
variable "crawlers" {
  description = "Map of Glue crawler configurations"
  type = map(object({
    name      = string
    s3_target = string
    database  = string
    role_arn  = string
    table_prefix  = string
  }))
  default = {}
}
