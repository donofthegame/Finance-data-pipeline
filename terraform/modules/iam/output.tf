output "athena_role_arn" {
  value = aws_iam_role.athena.arn
}

output "glue_crawler_role_arn" {
  value = aws_iam_role.glue_crawler.arn
}

output "glue_job_role_arn" {
  value = aws_iam_role.glue_job.arn
}

