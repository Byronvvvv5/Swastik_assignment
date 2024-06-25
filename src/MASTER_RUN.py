# Databricks notebook source
# This notebook as a centralized entry will be integrated in the GitHub workflow, and be called in the jobs

# COMMAND ----------

# MAGIC %run UTILS/DB_CONF

# COMMAND ----------

# we have mounted our storages and we will read retailsales file from Landing Zone
csv_file_path = "/mnt/landing_blob/retailsales.csv"
df = spark.read.option("header", "true").csv(csv_file_path)

# COMMAND ----------

# we will run quality check here for retailsales df
retailsales_columns = ["TransactionId"]
print(dbutils.notebook.run("UNITTESTS/QUALITY_CHECK", f"df={df}; columns={columns}", result=True))

# COMMAND ----------

# MAGIC %run PROCESSING/TRANSFORM

# COMMAND ----------

# after transformation we will load customer_df to Data Hub
customer_path = f"{output_base_path}/customers"
df.write.format("parquet").mode("overwrite").save(output_base_path)
