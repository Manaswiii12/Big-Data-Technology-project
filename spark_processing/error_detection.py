from pyspark.sql.functions import col

def detect_errors(df):
    errors = df.filter((col("status") == 404) | (col("status") == 500))
    errors.show(20)
    
    errors.toPandas().to_csv("results/error_logs.csv", index=False)

