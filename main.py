import os
os.environ["HADOOP_HOME"] = "C:\\hadoop"
os.environ["hadoop.home.dir"] = "C:\\hadoop"
os.environ["PATH"] += ";C:\\hadoop\\bin"

from spark_processing.load_data import create_spark_session, load_log_file
from spark_processing.log_parser import parse_logs
from spark_processing.traffic_analysis import traffic_analysis
from spark_processing.error_detection import detect_errors

spark = create_spark_session()

log_df = load_log_file(spark, "data/access_log_Jul95.log")
parsed_df = parse_logs(log_df)

parsed_df.show(20)

parsed_df.toPandas().to_csv("results/parsed_logs.csv", index=False)
traffic_analysis(parsed_df)
detect_errors(parsed_df)