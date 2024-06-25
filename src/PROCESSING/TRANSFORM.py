# Databricks notebook source
from pyspark.sql.functions import desc

# Group the DataFrame by customer id and count the number of transactions
df_agg = df.groupBy("customer id").count()

# Sort the DataFrame in descending order based on the count column
df_agg = df_agg.orderBy(desc("count"))

# Join the aggregated DataFrame with the original DataFrame to get the additional columns
customer_df = = df.join(df_agg, "customer id", "inner").select("customer id", "age", "gender", "total amount", col("count").alias("transactions"))


# COMMAND ----------

from delta.tables import DeltaTable

delta_table_path = "/mnt/landing_blob/delta_table"

# Write the customer_df to the Delta table for later updates
delta_table = DeltaTable.convertToDelta(customer_df, delta_table_path)

# COMMAND ----------

delta_table = DeltaTable.forPath(spark, delta_table_path)
snapshot_path = "/mnt/landing_blob/snapshots"
delta_table.generate(snapshot_path)
