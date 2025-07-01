# terraform/main.tf

module "s3_buckets" {
    for_each = var.aws_buckets
    source = "./modules/s3_buckets"
    bucket_name = each.value.name
    tags = var.tags
}


# module "silver_public_bucket" {
#   source      = "./modules/s3_public"
#   bucket_name = var.silver_public_bucket_name
#   tags        = var.tags
# }

# module "gold_public_bucket" {
#   source      = "./modules/s3_public"
#   bucket_name = var.gold_public_bucket_name
#   tags        = var.tags
# }


module "glue" {
    source = "./modules/glue"
    databases = var.aws_glue_databases
    tags = var.tags
  #   crawlers = {
  #       accounts = {
  #       name      = "bronze_accounts_crawler"
  #       s3_target = "s3://fdp-bronze-data-v5/accounts/"
  #       database  = "bronze_db"
  #       role_arn  = module.iam.glue_crawler_role_arn
  #       }
  #       customers = {
  #       name      = "bronze_customers_crawler"
  #       s3_target = "s3://fdp-bronze-data-v5/customers/"
  #       database  = "bronze_db"
  #       role_arn  = module.iam.glue_crawler_role_arn
  #       }
  #       loans = {
  #       name      = "bronze_loans_crawler"
  #       s3_target = "s3://fdp-bronze-data-v5/loans/"
  #       database  = "bronze_db"
  #       role_arn  = module.iam.glue_crawler_role_arn
  #       }
  #       loan_payments = {
  #       name      = "bronze_loan_payments_crawler"
  #       s3_target = "s3://fdp-bronze-data-v5/loan_payments/"
  #       database  = "bronze_db"
  #       role_arn  = module.iam.glue_crawler_role_arn
  #       }
  #       transactions = {
  #       name      = "bronze_transactions_crawler"
  #       s3_target = "s3://fdp-bronze-data-v5/transactions/"
  #       database  = "bronze_db"
  #       role_arn  = module.iam.glue_crawler_role_arn
  #       }
  # }

  crawlers = merge({
    accounts = {
      name      = "bronze_accounts_crawler"
      s3_target = "s3://fdp-bronze-data-v5/accounts/"
      database  = "bronze_db"
      role_arn  = module.iam.glue_crawler_role_arn
      table_prefix  = "bronze_"
    },
    customers = {
      name      = "bronze_customers_crawler"
      s3_target = "s3://fdp-bronze-data-v5/customers/"
      database  = "bronze_db"
      role_arn  = module.iam.glue_crawler_role_arn
      table_prefix  = "bronze_"
    },
    loans = {
      name      = "bronze_loans_crawler"
      s3_target = "s3://fdp-bronze-data-v5/loans/"
      database  = "bronze_db"
      role_arn  = module.iam.glue_crawler_role_arn
      table_prefix  = "bronze_"
    },
    loan_payments = {
      name      = "bronze_loan_payments_crawler"
      s3_target = "s3://fdp-bronze-data-v5/loan_payments/"
      database  = "bronze_db"
      role_arn  = module.iam.glue_crawler_role_arn
      table_prefix  = "bronze_"
    },
    transactions = {
      name      = "bronze_transactions_crawler"
      s3_target = "s3://fdp-bronze-data-v5/transactions/"
      database  = "bronze_db"
      role_arn  = module.iam.glue_crawler_role_arn
      table_prefix  = "bronze_"
    }
  }, {
    silver_accounts = {
      name      = "silver_accounts_crawler"
      s3_target = "s3://fdp-silver-data-v5/accounts/"
      database  = "silver_db"
      role_arn  = module.iam.glue_crawler_role_arn
      table_prefix  = "silver_"
    },
    silver_customers = {
      name      = "silver_customers_crawler"
      s3_target = "s3://fdp-silver-data-v5/customers/"
      database  = "silver_db"
      role_arn  = module.iam.glue_crawler_role_arn
      table_prefix  = "silver_"
    },
    silver_loans = {
      name      = "silver_loans_crawler"
      s3_target = "s3://fdp-silver-data-v5/loans/"
      database  = "silver_db"
      role_arn  = module.iam.glue_crawler_role_arn
      table_prefix  = "silver_"
    },
    silver_loan_payments = {
      name      = "silver_loan_payments_crawler"
      s3_target = "s3://fdp-silver-data-v5/loan_payments/"
      database  = "silver_db"
      role_arn  = module.iam.glue_crawler_role_arn
      table_prefix  = "silver_"
    },
    silver_transactions = {
      name      = "silver_transactions_crawler"
      s3_target = "s3://fdp-silver-data-v5/transactions/"
      database  = "silver_db"
      role_arn  = module.iam.glue_crawler_role_arn
      table_prefix  = "silver_"
    }
  })
}


module "iam" {
  source = "./modules/iam"
  glue_crawler_role_name = var.glue_crawler_role_name
  glue_job_role_name     = var.glue_job_role_name
  athena_role_name       = var.athena_role_name
  tags = var.tags
}

module "athena" {
  source             = "./modules/athena"
  athena_output_path = var.athena_output_path
  tags               = var.tags
}
