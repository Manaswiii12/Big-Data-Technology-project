from pyspark.sql.functions import col

def traffic_analysis(df):
    url_counts = df.groupBy("url").count().orderBy(col("count").desc())
    ip_counts = df.groupBy("ip").count().orderBy(col("count").desc())
    status_counts = df.groupBy("status").count()

    url_counts.show(10)
    ip_counts.show(10)
    status_counts.show()

    # Save results
    url_counts.toPandas().to_csv("results/top_urls.csv", index=False)
    ip_counts.toPandas().to_csv("results/top_ips.csv", index=False)
    status_counts.toPandas().to_csv("results/status_counts.csv", index=False)