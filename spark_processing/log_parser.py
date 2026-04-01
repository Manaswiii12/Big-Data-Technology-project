import pyspark.sql.functions as F

def parse_logs(log_df):
    parsed_df = log_df.select(
        F.regexp_extract('value', r'(^\S+)', 1).alias('ip'),
        F.regexp_extract('value', r'\[(.*?)\]', 1).alias('timestamp'),
        F.regexp_extract('value', r'\"(GET|POST)', 1).alias('method'),
        F.regexp_extract('value', r'\"(?:GET|POST) (.*?) HTTP', 1).alias('url'),
        F.regexp_extract('value', r'HTTP/\d\.\d\" (\d+)', 1).alias('status'),
        F.regexp_extract('value', r'\s(\d+)$', 1).alias('response_size')
    )
    return parsed_df