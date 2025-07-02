import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import (
    sum as spark_sum,
    avg as spark_avg,
    count as spark_count,
    expr
)

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


# Load silver layer tables
df_customers = spark.table("silver_db.silver_customers")
df_loans = spark.table("silver_db.silver_loans")
df_accounts = spark.table("silver_db.silver_accounts")
df_payments = spark.table("silver_db.silver_loan_payments")
df_transactions = spark.table("silver_db.silver_transactions")

# Aggregate loans per customer
df_loans_agg = df_loans.groupBy("customer_id").agg(
    spark_count("loan_id").alias("num_loans"),
    spark_sum("principal").alias("total_principal"),
    spark_avg("interest_rate").alias("avg_interest_rate")
)

# Aggregate payments per customer
df_payments_joined = df_payments.join(df_loans.select("loan_id", "customer_id"), on="loan_id", how="left")
df_payments_agg = df_payments_joined.groupBy("customer_id").agg(
    spark_sum("amount").alias("total_paid"),
    spark_count("*").alias("num_payments"),
    expr("sum(case when status = 'Failed' then 1 else 0 end)").alias("failed_payments")
)

# Aggregate accounts per customer
df_accounts_agg = df_accounts.groupBy("customer_id").agg(
    spark_count("account_id").alias("num_accounts"),
    spark_sum("balance").alias("total_balance"),
    spark_avg("balance").alias("avg_balance"),
    expr("sum(case when status = 'Suspended' then 1 else 0 end)").alias("suspended_accounts")
)

# Aggregate transactions per customer (assuming account_id == customer_id)
df_txn_agg = df_transactions.groupBy("account_id").agg(
    spark_sum("amount").alias("total_txn_amount"),
    spark_count("*").alias("txn_count")
).withColumnRenamed("account_id", "customer_id")

# Final 360 View
df_customer_360 = df_customers \
    .join(df_loans_agg, on="customer_id", how="left") \
    .join(df_payments_agg, on="customer_id", how="left") \
    .join(df_accounts_agg, on="customer_id", how="left") \
    .join(df_txn_agg, on="customer_id", how="left")

df_clean = df_customer_360.drop(
    "silver_customer_ingestion_time", "bronze_file_name", "row_hash"
)

# Write to gold
df_clean.write \
    .format("delta") \
    .mode("overwrite") \
    .option("path", "s3://fdp-gold-data-v5/customer_360/") \
    .saveAsTable("gold_db.customer_360")

job.commit()