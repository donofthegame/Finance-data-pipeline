resource "aws_glue_catalog_database" "this" {
  for_each    = var.databases
  name        = each.value.name
  description = each.value.description
  tags        = var.tags
}

resource "aws_glue_crawler" "this" {
  for_each     = var.crawlers
  name         = each.value.name
  role         = each.value.role_arn
  database_name = each.value.database
  table_prefix = each.value.table_prefix

  s3_target {
    path = each.value.s3_target
  }

  # schedule = "cron(0 12 * * ? *)"  # optional: daily at noon UTC

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  tags = var.tags
}
