from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
import sys

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

print("spark.sql.extensions =", spark.conf.get("spark.sql.extensions", "MISSING"))
print("spark.sql.catalog.spark_catalog =", spark.conf.get("spark.sql.catalog.spark_catalog", "MISSING"))


print("[INFO] Registering Delta table...")

spark.sql("""
    CREATE TABLE IF NOT EXISTS silver_db.accounts
    USING DELTA
    LOCATION 's3://fdp-silver-data-v5/accounts/'
""")

print("[SUCCESS] Table registered!")

job.commit()
