import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, row_number, input_file_name, current_timestamp, to_date, sha2, concat_ws
from pyspark.sql.window import Window
from pyspark.sql.functions import year, month

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)



# 1. Read from Glue Catalog (bronze layer)
df_raw = spark.table("bronze_db.bronze_transactions")

# 2. Clean & Transform
df = df_raw.withColumn("txn_date", to_date(col("txn_date"), "yyyy-MM-dd"))

df_filled = df.fillna({
    "txn_type": "Unknown",
    "merchant": "Unknown",
    "amount": 0.0,
    "location": "Unknown"
})

df_cleaned = df_filled.dropna(subset=["txn_id", "account_id", "txn_date"])

df_lineage = df_cleaned.withColumn("silver_transactions_ingestion_time", current_timestamp()) \
    .withColumn("bronze_file_name", input_file_name())

df_hash = df_lineage.withColumn("row_hash", sha2(concat_ws("|", *df_lineage.columns), 256))

# 3. Deduplicate
window_spec = Window.partitionBy("account_id", "row_hash").orderBy(col("silver_transactions_ingestion_time").desc())
df_deduped = df_hash.withColumn("row_number", row_number().over(window_spec)) \
    .filter(col("row_number") == 1) \
    .drop("row_number")

# 4. Add partition columns: txn_year and txn_month
df_final = df_deduped.withColumn("txn_year", year("txn_date")) \
                     .withColumn("txn_month", month("txn_date"))

# 5. Write to Delta (silver layer)
silver_path = "s3://fdp-silver-data-v5/transactions/"
# silver_table = "silver_db.transactions"

df_final.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .partitionBy("txn_year", "txn_month") \
    .save(silver_path)

job.commit()