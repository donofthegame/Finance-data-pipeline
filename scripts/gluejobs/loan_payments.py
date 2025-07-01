import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, when, to_date, current_timestamp, input_file_name, sha2, concat_ws, row_number
from pyspark.sql.window import Window
from pyspark.sql.functions import year, month

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read from Glue Catalog (bronze)
df_raw = spark.table("bronze_db.bronze_loan_payments")

df = df_raw.withColumn("payment_date", to_date(col("payment_date"), "yyyy-MM-dd"))

df_filled = df.fillna({
    "method": "Unknown",
    "status": "Unknown",
    "amount": 0.0
})
df_cleaned = df_filled.dropna(subset=["payment_id", "loan_id", "payment_date"])

df_cleaned = df_filled.dropna(subset=["payment_id", "loan_id", "payment_date"])

df_lineage = df_cleaned.withColumn("silver_payments_ingestion_time", current_timestamp()) \
    .withColumn("bronze_file_name", input_file_name())

df_hash = df_lineage.withColumn("row_hash", sha2(concat_ws("|", *df_lineage.columns), 256))

# 3. Deduplicate
window_spec = Window.partitionBy("loan_id", "row_hash").orderBy(col("silver_payments_ingestion_time").desc())
df_deduped = df_hash.withColumn("row_number", row_number().over(window_spec)) \
    .filter(col("row_number") == 1) \
    .drop("row_number")

# 4. Add partition columns
df_final = df_deduped.withColumn("payment_year", year("payment_date")) \
                     .withColumn("payment_month", month("payment_date"))


# Write to Silver S3 path (Delta format)
# silver_table = "silver_db.loans_payments"
silver_path = "s3://fdp-silver-data-v5/loan_payments/"
df_final.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .partitionBy("payment_year", "payment_month") \
    .save(silver_path)


job.commit()