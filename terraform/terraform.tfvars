aws_region = "us-east-1"

# aws_buckets = {
#   bronze_accounts         = { name = "fdp-bronze-accounts" }
#   bronze_customers        = { name = "fdp-bronze-customers" }
#   bronze_loan_payments    = { name = "fdp-bronze-loan-payments" }
#   bronze_loans            = { name = "fdp-bronze-loans" }
#   bronze_transactions     = { name = "fdp-bronze-transactions" }

#   silver_accounts         = { name = "fdp-silver-accounts" }
#   silver_customers        = { name = "fdp-silver-customers" }
#   silver_loan_payments    = { name = "fdp-silver-loan-payments" }
#   silver_loans            = { name = "fdp-silver-loans" }
#   silver_transactions     = { name = "fdp-silver-transactions" }

#   gold_accounts           = { name = "fdp-gold-accounts" }
#   gold_customers          = { name = "fdp-gold-customers" }
#   gold_loan_payments      = { name = "fdp-gold-loan-payments" }
#   gold_loans              = { name = "fdp-gold-loans" }
#   gold_transactions       = { name = "fdp-gold-transactions" }
#   gold_data_quality       = { name = "fdp-gold-data-quality" }
# }

aws_buckets = {
  bronze_layer = { name = "fdp-bronze-data-v5" }
  silver_layer = { name = "fdp-silver-data-v5" }
  gold_layer   = { name = "fdp-gold-data-v5" }
  athena_results = { name = "fdp-athena-query-results-v5" }
  scripts = { name = "fdp-glue-scripts-v5" }
}

# silver_public_bucket_name = "fdp-silver-public-data-v5"
# gold_public_bucket_name   = "fdp-gold-public-data-v5"


aws_glue_databases = {
  bronze = {
    name        = "bronze_db"
    description = "Raw ingested banking data"
  }
  silver = {
    name        = "silver_db"
    description = "Cleaned and validated banking data"
  }
  gold = {
    name        = "gold_db"
    description = "Business-ready aggregated banking data"
  }
}

athena_role_name = "fdp-athena-role-v5"
glue_crawler_role_name = "fdp-glue-crawler-role-v5"
glue_job_role_name = "fdp-glue-job-role-v5"


tags = {
  Project     = "Financial Data Platform"
  Environment = "Development"
  Owner       = "donofthegame"
}

athena_output_path = "s3://fdp-athena-query-results-v5/"
