from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)

RESULTS_PATH = "../results/"
STATIC_PATH = "static/"

os.makedirs(STATIC_PATH, exist_ok=True)

# ── Helper: safe CSV read ──────────────────────────────────────────────────────
def read_csv_safe(filename, fallback_cols):
    path = os.path.join(RESULTS_PATH, filename)
    if os.path.exists(path):
        return pd.read_csv(path)
    # Return empty dataframe with expected columns for demo
    return pd.DataFrame(columns=fallback_cols)


# ── Crash / anomaly detection ─────────────────────────────────────────────────
def detect_crashes(errors_df):
    """Flag time windows with > 10 errors/minute as potential crashes."""
    alerts = []
    if errors_df.empty or 'timestamp' not in errors_df.columns:
        # Demo alerts when no real data
        return [
            {"time": "14:32:01", "type": "5xx Spike", "severity": "critical",
             "message": "23 server errors in 60 seconds — possible crash loop"},
            {"time": "11:08:44", "type": "Memory OOM", "severity": "warning",
             "message": "Response time > 2000ms across 15 consecutive requests"},
            {"time": "09:55:12", "type": "DB Timeout", "severity": "warning",
             "message": "12 connection timeouts on /api/v1/query"},
        ]
    try:
        errors_df['timestamp'] = pd.to_datetime(errors_df['timestamp'])
        server_errs = errors_df[errors_df['status'] >= 500].copy()
        server_errs['minute'] = server_errs['timestamp'].dt.floor('min')
        counts = server_errs.groupby('minute').size()
        crash_windows = counts[counts > 10]
        for ts, cnt in crash_windows.items():
            alerts.append({
                "time": ts.strftime("%H:%M:%S"),
                "type": "5xx Spike",
                "severity": "critical" if cnt > 20 else "warning",
                "message": f"{cnt} server errors in 60 seconds"
            })
    except Exception:
        pass
    return alerts


def detect_uploads(logs_df):
    """Detect POST requests with large payloads or to upload endpoints."""
    uploads = []
    if logs_df.empty:
        return [
            {"time": "15:01:22", "ip": "192.168.1.22",  "url": "/api/upload/dataset.csv",  "size": "14.2 MB", "status": 200},
            {"time": "13:47:09", "ip": "10.0.0.88",     "url": "/api/upload/model_v2.pkl",  "size": "88.6 MB", "status": 200},
            {"time": "11:30:55", "ip": "203.0.113.5",   "url": "/api/upload/logs_bulk.zip", "size": "4.1 MB",  "status": 413},
            {"time": "08:12:34", "ip": "172.16.0.14",   "url": "/ingest/events",            "size": "2.8 MB",  "status": 200},
        ]
    try:
        upload_mask = (
            (logs_df.get('method', pd.Series()) == 'POST') |
            (logs_df.get('url', pd.Series([''])).str.contains('upload|ingest|import', case=False, na=False))
        )
        for _, row in logs_df[upload_mask].head(10).iterrows():
            uploads.append({
                "time":   str(row.get('timestamp', '')),
                "ip":     str(row.get('ip', '')),
                "url":    str(row.get('url', '')),
                "size":   str(row.get('bytes', 'N/A')),
                "status": int(row.get('status', 0)),
            })
    except Exception:
        pass
    return uploads


# ── Hourly traffic simulation (replace with real parsed log data) ──────────────
def get_hourly_traffic(logs_df):
    if not logs_df.empty and 'timestamp' in logs_df.columns:
        try:
            logs_df['hour'] = pd.to_datetime(logs_df['timestamp']).dt.hour
            return logs_df.groupby('hour').size().reindex(range(24), fill_value=0).tolist()
        except Exception:
            pass
    # Synthetic demo data
    base = [180,140,110,90,75,85,220,580,870,940,1010,1080,
            1020,890,960,1120,1090,960,870,790,640,520,390,280]
    return [v + random.randint(-30, 30) for v in base]


def get_response_time_series():
    """Simulated response-time trend (ms) for last 12 hours."""
    hours = [(datetime.now() - timedelta(hours=i)).strftime("%H:00") for i in range(11, -1, -1)]
    times = [142, 138, 155, 390, 162, 148, 175, 195, 141, 138, 152, 142]
    return hours, times


def get_geo_data(top_ips):
    """Mock geo breakdown – replace with real GeoIP lookup."""
    return [
        {"country": "India",         "requests": 18420, "pct": 38},
        {"country": "United States", "requests": 11280, "pct": 23},
        {"country": "Germany",       "requests":  5810, "pct": 12},
        {"country": "Singapore",     "requests":  4620, "pct":  9},
        {"country": "Brazil",        "requests":  3190, "pct":  7},
        {"country": "Other",         "requests":  4992, "pct": 11},
    ]


# ── Main dashboard route ───────────────────────────────────────────────────────
@app.route("/")
def dashboard():
    top_ips      = read_csv_safe("top_ips.csv",      ["ip", "count"])
    top_urls     = read_csv_safe("top_urls.csv",     ["url", "count"])
    status_counts= read_csv_safe("status_counts.csv",["status", "count"])
    errors       = read_csv_safe("error_logs.csv",   ["ip", "url", "status", "timestamp"])
    logs_df      = read_csv_safe("access_logs.csv",  ["ip", "url", "status", "method", "bytes", "timestamp"])

    # Derived metrics
    total_requests = int(top_ips['count'].sum()) if not top_ips.empty else 48312
    error_count    = int(errors.shape[0])
    success_rate   = round((1 - error_count / max(total_requests, 1)) * 100, 1)

    hourly   = get_hourly_traffic(logs_df)
    rt_hours, rt_vals = get_response_time_series()
    geo_data = get_geo_data(top_ips)
    alerts   = detect_crashes(errors)
    uploads  = detect_uploads(logs_df)

    # Status distribution for chart
    if status_counts.empty:
        status_json = json.dumps([
            {"status": "2xx", "count": 44157},
            {"status": "3xx", "count": 2180},
            {"status": "4xx", "count": 1620},
            {"status": "5xx", "count": 355},
        ])
    else:
        status_json = status_counts.to_json(orient="records")

    return render_template(
        "dashboard.html",
        top_ips        = top_ips.head(10).to_dict(orient="records"),
        top_urls       = top_urls.head(10).to_dict(orient="records"),
        errors         = errors.head(15).to_dict(orient="records"),
        status_json    = status_json,
        hourly_json    = json.dumps(hourly),
        rt_hours_json  = json.dumps(rt_hours),
        rt_vals_json   = json.dumps(rt_vals),
        geo_data       = geo_data,
        alerts         = alerts,
        uploads        = uploads,
        total_requests = total_requests,
        error_count    = error_count,
        success_rate   = success_rate,
        generated_at   = datetime.now().strftime("%d %b %Y, %H:%M:%S"),
    )


# ── Live metrics API (used by auto-refresh JS) ────────────────────────────────
@app.route("/api/live")
def live_metrics():
    """Returns JSON snapshot for front-end polling."""
    return jsonify({
        "requests_last_min": random.randint(180, 420),
        "errors_last_min":   random.randint(0, 18),
        "avg_response_ms":   random.randint(120, 280),
        "active_connections":random.randint(40, 210),
        "timestamp":         datetime.now().strftime("%H:%M:%S"),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)