# Databricks notebook source
from pyspark.sql import functions as F

def test_nulls(df, columns):
    for col in columns:
        assert df.agg(F.sum(F.col(col).isNull().cast('int'))).collect()[0][0] == 0

def test_uniqueness(df, columns):
    for col in columns:
        assert df.select(col).distinct().count() == df.count()

# COMMAND ----------

try:
    test_no_nulls(df, columns)
    test_uniqueness(df, columns)
    print("Quality check passed.")
except AssertionError as e:
    print(f"Quality check failed: {e}")
except Exception as e:
    print(f"Unknown error occurred: {e}")
