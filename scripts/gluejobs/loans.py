import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col, regexp_replace, to_date, current_timestamp, input_file_name, sha2, concat_ws, row_number
from pyspark.sql.window import Window
from pyspark.sql.functions import year, month

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# 1. Read from Bronze Table
df_raw = spark.table("bronze_db.bronze_loans")

# 2. Clean & Transform
df = df_raw \
    .withColumn("start_date", to_date("start_date", "yyyy-MM-dd")) \
    .withColumn("end_date", to_date("end_date", "yyyy-MM-dd")) \
    .withColumn("interest_rate", regexp_replace("interest_rate", "%", "").cast("double"))

df_filled = df.fillna({
    "status": "Unknown",
    "loan_type": "Unknown",
    "interest_rate": 0.0,
    "principal": 0
})

df_cleaned = df_filled.dropna(subset=["loan_id", "customer_id", "start_date"])

df_lineage = df_cleaned.withColumn("silver_loans_ingestion_time", current_timestamp()) \
    .withColumn("bronze_file_name", input_file_name())

df_hash = df_lineage.withColumn("row_hash", sha2(concat_ws("|", *df_lineage.columns), 256))

# 3. Deduplicate
window_spec = Window.partitionBy("loan_id", "row_hash").orderBy(col("silver_loans_ingestion_time").desc())
df_deduped = df_hash.withColumn("row_number", row_number().over(window_spec)) \
    .filter(col("row_number") == 1) \
    .drop("row_number")

# 4. Add partition column
df_final = df_deduped.withColumn("start_year", year("start_date"))

# 5. Write to Delta and register in Glue Catalog
silver_path = "s3://fdp-silver-data-v5/loans/"
silver_table = "silver_db.loans"

df_final.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .partitionBy("loan_type", "start_year") \
    .save(silver_path)

job.commit()