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
    datediff,
    when,
    col,
    expr
)
## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Load silver tables
df_loans = spark.table("silver_db.silver_loans")
df_payments = spark.table("silver_db.silver_loan_payments")
df_accounts = spark.table("silver_db.silver_accounts")

# Clean + feature engineering
df_loans_clean = df_loans.withColumn("duration_years", (datediff("end_date", "start_date") / 365).cast("int")) \
    .withColumn("is_defaulted", when(col("status") == "Defaulted", 1).otherwise(0))

# Payments aggregates
df_payments_joined = df_payments.join(df_loans.select("loan_id", "customer_id"), on="loan_id", how="left")
df_payments_agg = df_payments_joined.groupBy("loan_id").agg(
    spark_sum("amount").alias("total_paid"),
    spark_count("*").alias("num_payments"),
    expr("sum(case when status = 'Failed' then 1 else 0 end)").alias("failed_payments")
)

# Account-level aggregates per customer
df_account_agg = df_accounts.groupBy("customer_id").agg(
    spark_avg("balance").alias("avg_balance"),
    spark_count("account_id").alias("num_accounts")
)

# Final risk dataset
df_risk = df_loans_clean \
    .join(df_payments_agg, on="loan_id", how="left") \
    .join(df_account_agg, on="customer_id", how="left") \
    .select(
        "loan_id", "customer_id", "loan_type", "principal", "interest_rate",
        "duration_years", "total_paid", "num_payments", "failed_payments",
        "avg_balance", "num_accounts", "is_defaulted"
    )

# Write to gold
df_risk.write \
    .format("parquet") \
    .mode("overwrite") \
    .save("s3://fdp-gold-data-v5/loan_risk_scoring/")

job.commit()