output "aws_glue_databases" {
  value = {
    for db_key, db in aws_glue_catalog_database.this :
    db_key => db.name
  }
}

output "crawler_names" {
  value = keys(var.crawlers)
}

output "crawler_arns" {
  value = {
    for k, v in aws_glue_crawler.this : k => v.arn
  }
}
