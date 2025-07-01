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

df_raw = spark.table("bronze_db.bronze_customers")

# Convert dob string to DateType
df = df_raw.withColumn("dob", to_date(col("dob"), "yyyy-MM-dd"))

# Fill optional fields
df_filled = df.fillna({
    "first_name": "Unknown",
    "last_name": "Unknown",
    "email": "unknown@example.com",
    "phone": "0000000000",
    "address": "Not Provided",
    "city": "Unknown",
    "state": "NA",
    "zip": "00000"
})

df_cleaned = df_filled.dropna(subset=["customer_id","dob"])


# Add data lineage columns
df_lineage = df_cleaned.withColumn("silver_customers_ingestion_time", current_timestamp()) \
                       .withColumn("bronze_file_name", input_file_name())

# Add hash to detect duplicates
df_hashed = df_lineage.withColumn("row_hash", sha2(concat_ws("|", *df_lineage.columns), 256))

# Deduplicate: Keep latest by ingestion time
window_spec = Window.partitionBy("customer_id", "row_hash").orderBy(col("silver_customers_ingestion_time").desc())
df_deduped = df_hashed.withColumn("row_number", row_number().over(window_spec)) \
                      .filter(col("row_number") == 1) \
                      .drop("row_number")


# Write to Silver Layer in Delta Format
# silver_table = "silver_db.transactions"
silver_path = "s3://fdp-silver-data-v5/customers/"
df_deduped.write.format("delta").mode("overwrite").partitionBy("state").save(silver_path)

                      
job.commit()