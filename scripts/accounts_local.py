from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, row_number , input_file_name, current_timestamp, to_date, sha2, concat_ws
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DoubleType, TimestampType, DateType

spark = SparkSession.builder \
    .appName("Accounts") \
    .getOrCreate()

#bronze_path = "/Users/mynu/Desktop/DE_Projects/Finance-data-pipeline/bronze_data/accounts"
#silver_path = "/Users/mynu/Desktop/DE_Projects/Finance-data-pipeline/bronze_data"

bronze_path = "s3://fdp-bronze-data/accounts/"
silver_path = "s3://fdp-silver-data/accounts/"

schema = StructType([
    StructField("account_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("account_type", StringType(), True),
    StructField("balance", DoubleType(), True),
    StructField("open_date", StringType(), True), # will be converted to date later
    StructField("status", StringType(), True)
])

df_raw = spark.read.option("header", "true").schema(schema).csv(bronze_path)
df_cleaned = df_raw.withColumn("open_date", to_date(col("open_date"), "yyyy-MM-dd")) \
    .dropna(subset=["account_id", "customer_id"]) \
    .fillna({
        "account_type": "Unknown",
        "status": "active",
        "balance": 0.0
    })

df_lineage = df_cleaned.withColumn("bronze_ingestion_time", current_timestamp()) \
    .withColumn("bronze_file_name", input_file_name())

df_hash = df_lineage.withColumn("row_hash", sha2(concat_ws("|", *df_lineage.columns), 256))


window_spec = Window.partitionBy("account_id", "row_hash").orderBy(col("bronze_ingestion_time").desc())
df_deduped = df_hash.withColumn("row_number", row_number().over(window_spec)) \
    .filter(col("row_number") == 1) \
    .drop("row_number")


df_deduped.write.format("parquet").mode("overwrite").save(silver_path)