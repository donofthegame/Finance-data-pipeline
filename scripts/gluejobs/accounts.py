import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, row_number, input_file_name, current_timestamp, to_date, sha2, concat_ws
from pyspark.sql.window import Window
from pyspark.sql.functions import year, month

# Job args
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# Glue & Spark setup
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# 1. Read from Glue Catalog (bronze layer)
df_raw = spark.table("bronze_db.bronze_accounts")

# 2. Clean & Transform
df = df_raw.withColumn("open_date", to_date(col("open_date"), "yyyy-MM-dd"))

df_filled = df.fillna({
    "account_type": "Unknown",
    "status": "active",
    "balance": 0.0
})

df_cleaned = df_filled.dropna(subset=["account_id", "customer_id", "open_date"])

df_lineage = df_cleaned.withColumn("silver_accounts_ingestion_time", current_timestamp()) \
    .withColumn("bronze_file_name", input_file_name())

df_hash = df_lineage.withColumn("row_hash", sha2(concat_ws("|", *df_lineage.columns), 256))

# 3. Deduplicate
window_spec = Window.partitionBy("account_id", "row_hash").orderBy(col("silver_accounts_ingestion_time").desc())
df_deduped = df_hash.withColumn("row_number", row_number().over(window_spec)) \
    .filter(col("row_number") == 1) \
    .drop("row_number")
    
df_partitioned = df_deduped \
    .withColumn("year", year(col("open_date"))) \
    .withColumn("month", month(col("open_date")))

# 4. Write to Delta S3 (silver layer)
# silver_table = "silver_db.accounts"
silver_path = "s3://fdp-silver-data-v5/accounts/"
print(f"[DEBUG] Writing Delta to: '{silver_path}'")

df_partitioned.write.format("delta").mode("overwrite").partitionBy("year", "month").save(silver_path)

job.commit()
