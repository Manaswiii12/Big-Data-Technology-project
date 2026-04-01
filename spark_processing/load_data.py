from pyspark.sql import SparkSession

def create_spark_session():
    spark = SparkSession.builder \
        .appName("Web Server Log Analysis") \
        .getOrCreate()
    return spark

def load_log_file(spark, file_path):
    log_df = spark.read.text(file_path)
    return log_df