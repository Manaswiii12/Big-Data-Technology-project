# Big Data Web Server Log Analysis Project

## Project Description

This project analyzes web server log data using Big Data technologies and machine learning techniques. The system processes web logs, detects errors, analyzes traffic patterns, and identifies anomalies in server activity.

## Technologies Used

* Python
* Apache Spark
* Flask
* Machine Learning (Scikit-learn)
* SQLite Database
* Pandas & Matplotlib
* GitHub

## Project Modules

1. **Data Processing (Spark Processing)**
   Cleans log data, performs feature engineering, and processes large log datasets using Apache Spark.

2. **Machine Learning Models**
   Trains models for anomaly detection and error prediction.

3. **Database Module**
   Stores processed log data and analysis results.

4. **Dashboard (Flask Web App)**
   Displays log analysis results, error statistics, top URLs, and traffic insights.

## Features

* Log file parsing
* Error detection
* Traffic analysis
* Top IP and URL analysis
* Anomaly detection
* Web dashboard visualization

## How to Run the Project

```bash
pip install -r requirements.txt
python dashboard/app.py
```

Then open:

```
http://127.0.0.1:5000
```

## Note

Large dataset files are compressed due to GitHub file size limitations.
