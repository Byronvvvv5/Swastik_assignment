# Databricks notebook source
from pyspark.sql import SparkSession

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Read from DBFS") \
    .getOrCreate()
    
# Connect to blob storage(LANDING ZONE)
account_key = dbutils.secrets.get(scope="blob-scope-landing", key="Landing-Blob")

spark.conf.set(f"fs.azure.account.key.mllandingdevelopment.blob.core.windows.net", account_key)

# COMMAND ----------

# Mount blob storage to DBFS
mount_point = "/mnt/landing_blob"
container_name = "landingzone"
storage_account_name = "mllandingdevelopment"
# Check if the mount point already exists
if not dbutils.fs.ls(mount_point):
    dbutils.fs.mount(
        source=f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net",
        mount_point=mount_point,
        extra_configs={
            f"fs.azure.sas.{container_name}.{storage_account_name}.blob.core.windows.net": account_key
        }
    )
else:
    print(f"Mount point {mount_point} already exists.")

# COMMAND ----------

# Connect to datalake storage(DATA HUB)
storage_account_name = "mlsendingdevelopment"
container_name = "consumption"
storage_access_key = dbutils.secrets.get(scope="datalake-scope-sending", key="Consump")

# Set the output path in the datalake storage
output_base_path = f"wasbs://{container_name}@{storage_account_name}.dfs.core.windows.net/training"

