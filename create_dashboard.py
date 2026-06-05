"""
Create VisionAI Analytics Dashboard on Databricks
Uses Lakeview Dashboard API + Preview SQL Query API
"""
import requests
import json
import sys
import uuid

# === Configuration ===
import os
HOST = os.environ.get('DATABRICKS_HOST', 'https://dbc-5786e2e8-ac9e.cloud.databricks.com')

# Read token securely
TOKEN = os.environ.get('DATABRICKS_TOKEN', '')
if not TOKEN:
    for p in ['tokenvissiondtb.txt', '../tokenvissiondtb.txt', 'tokendtb.txt', '../tokendtb.txt']:
        if os.path.exists(p):
            with open(p, 'r') as f:
                TOKEN = f.read().strip()
                break

WAREHOUSE_ID = os.environ.get('DATABRICKS_WAREHOUSE_ID', 'f82d2d3131c0030a')

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def api(method, endpoint, data=None):
    url = f"{HOST}{endpoint}"
    if method == "GET":
        resp = requests.get(url, headers=HEADERS, timeout=60)
    elif method == "POST":
        resp = requests.post(url, headers=HEADERS, json=data, timeout=60)
    elif method == "PATCH":
        resp = requests.patch(url, headers=HEADERS, json=data, timeout=60)
    if resp.status_code >= 400:
        print(f"  [ERROR] {resp.status_code}: {resp.text[:400]}")
        return None
    return resp.json() if resp.text else {}


def uid():
    return str(uuid.uuid4()).replace("-", "")[:16]


def main():
    print("=" * 60)
    print("  VISIONAI LAKEVIEW DASHBOARD CREATOR")
    print("=" * 60)

    # Build the serialized dashboard definition
    # Lakeview dashboard JSON format
    datasets = [
        {
            "name": "detection_by_feature",
            "displayName": "Detection by AI Feature",
            "query": "SELECT ai_feature, total_detections, avg_processing_sec, unique_users FROM visionai_catalog.gold.detection_by_feature ORDER BY total_detections DESC"
        },
        {
            "name": "detection_by_shift",
            "displayName": "Detection by Time Shift",
            "query": "SELECT time_shift, total_detections, active_users, avg_processing_sec FROM visionai_catalog.gold.detection_by_shift"
        },
        {
            "name": "hourly_activity",
            "displayName": "Hourly Activity",
            "query": "SELECT hour_of_day, total_detections, active_users FROM visionai_catalog.gold.hourly_activity ORDER BY hour_of_day"
        },
        {
            "name": "speed_analysis",
            "displayName": "Speed Analysis",
            "query": "SELECT speed_grade, ai_feature, total_detections, avg_time_sec, fastest_sec, slowest_sec FROM visionai_catalog.gold.speed_analysis ORDER BY avg_time_sec"
        },
        {
            "name": "ml_experiment",
            "displayName": "ML Experiment Log",
            "query": """SELECT 
    run_id, model_name, model_version,
    learning_rate, batch_size, epochs, img_size,
    ROUND(precision_score * 100, 1) AS precision_pct,
    ROUND(recall_score * 100, 1) AS recall_pct,
    ROUND(map50 * 100, 1) AS map50_pct,
    ROUND(map50_95 * 100, 1) AS map50_95_pct,
    training_time, status
FROM visionai_catalog.gold.ml_experiment_log 
ORDER BY map50_95 DESC"""
        }
    ]

    # Build the Lakeview dashboard JSON
    dashboard_def = {
        "pages": [
            {
                "name": "main_page",
                "displayName": "VisionAI Analytics",
                "layout": [
                    # Row 1: Detection by Feature (bar) + Detection by Shift (pie)
                    {
                        "widget": {
                            "name": "widget_feature",
                            "queries": [
                                {
                                    "name": "main_query",
                                    "query": {
                                        "datasetName": "detection_by_feature",
                                        "fields": [
                                            {"name": "ai_feature", "expression": "`ai_feature`"},
                                            {"name": "total_detections", "expression": "`total_detections`"}
                                        ],
                                        "disaggregated": True
                                    }
                                }
                            ],
                            "spec": {
                                "version": 3,
                                "widgetType": "bar",
                                "encodings": {
                                    "x": {"fieldName": "ai_feature", "scale": {"type": "categorical"}, "displayName": "AI Feature"},
                                    "y": {"fieldName": "total_detections", "scale": {"type": "quantitative"}, "displayName": "Total Detections"}
                                }
                            },
                            "overrides": {}
                        },
                        "position": {"x": 0, "y": 0, "width": 3, "height": 3}
                    },
                    {
                        "widget": {
                            "name": "widget_shift",
                            "queries": [
                                {
                                    "name": "main_query",
                                    "query": {
                                        "datasetName": "detection_by_shift",
                                        "fields": [
                                            {"name": "time_shift", "expression": "`time_shift`"},
                                            {"name": "total_detections", "expression": "`total_detections`"}
                                        ],
                                        "disaggregated": True
                                    }
                                }
                            ],
                            "spec": {
                                "version": 3,
                                "widgetType": "pie",
                                "encodings": {
                                    "theta": {"fieldName": "total_detections", "displayName": "Total Detections"},
                                    "color": {"fieldName": "time_shift", "scale": {"type": "categorical"}, "displayName": "Time Shift"}
                                }
                            },
                            "overrides": {}
                        },
                        "position": {"x": 3, "y": 0, "width": 3, "height": 3}
                    },
                    # Row 2: Hourly Activity (line chart, full width)
                    {
                        "widget": {
                            "name": "widget_hourly",
                            "queries": [
                                {
                                    "name": "main_query",
                                    "query": {
                                        "datasetName": "hourly_activity",
                                        "fields": [
                                            {"name": "hour_of_day", "expression": "`hour_of_day`"},
                                            {"name": "total_detections", "expression": "`total_detections`"},
                                            {"name": "active_users", "expression": "`active_users`"}
                                        ],
                                        "disaggregated": True
                                    }
                                }
                            ],
                            "spec": {
                                "version": 3,
                                "widgetType": "line",
                                "encodings": {
                                    "x": {"fieldName": "hour_of_day", "scale": {"type": "categorical"}, "displayName": "Hour of Day"},
                                    "y": {"fieldName": "total_detections", "scale": {"type": "quantitative"}, "displayName": "Total Detections"}
                                }
                            },
                            "overrides": {}
                        },
                        "position": {"x": 0, "y": 3, "width": 6, "height": 3}
                    },
                    # Row 3: Speed Analysis (bar) + ML Performance (bar)
                    {
                        "widget": {
                            "name": "widget_speed",
                            "queries": [
                                {
                                    "name": "main_query",
                                    "query": {
                                        "datasetName": "speed_analysis",
                                        "fields": [
                                            {"name": "ai_feature", "expression": "`ai_feature`"},
                                            {"name": "avg_time_sec", "expression": "`avg_time_sec`"},
                                            {"name": "speed_grade", "expression": "`speed_grade`"}
                                        ],
                                        "disaggregated": True
                                    }
                                }
                            ],
                            "spec": {
                                "version": 3,
                                "widgetType": "bar",
                                "encodings": {
                                    "x": {"fieldName": "ai_feature", "scale": {"type": "categorical"}, "displayName": "AI Feature"},
                                    "y": {"fieldName": "avg_time_sec", "scale": {"type": "quantitative"}, "displayName": "Avg Time (sec)"},
                                    "color": {"fieldName": "speed_grade", "scale": {"type": "categorical"}, "displayName": "Speed Grade"}
                                }
                            },
                            "overrides": {}
                        },
                        "position": {"x": 0, "y": 6, "width": 3, "height": 3}
                    },
                    {
                        "widget": {
                            "name": "widget_ml",
                            "queries": [
                                {
                                    "name": "main_query",
                                    "query": {
                                        "datasetName": "ml_experiment",
                                        "fields": [
                                            {"name": "model_name", "expression": "`model_name`"},
                                            {"name": "model_version", "expression": "`model_version`"},
                                            {"name": "map50_95_pct", "expression": "`map50_95_pct`"}
                                        ],
                                        "disaggregated": True
                                    }
                                }
                            ],
                            "spec": {
                                "version": 3,
                                "widgetType": "bar",
                                "encodings": {
                                    "x": {"fieldName": "model_version", "scale": {"type": "categorical"}, "displayName": "Model Version"},
                                    "y": {"fieldName": "map50_95_pct", "scale": {"type": "quantitative"}, "displayName": "mAP@50-95 (%)"},
                                    "color": {"fieldName": "model_name", "scale": {"type": "categorical"}, "displayName": "Model"}
                                }
                            },
                            "overrides": {}
                        },
                        "position": {"x": 3, "y": 6, "width": 3, "height": 3}
                    },
                    # Row 4: ML Experiment Table (full width)
                    {
                        "widget": {
                            "name": "widget_ml_table",
                            "queries": [
                                {
                                    "name": "main_query",
                                    "query": {
                                        "datasetName": "ml_experiment",
                                        "fields": [
                                            {"name": "run_id", "expression": "`run_id`"},
                                            {"name": "model_name", "expression": "`model_name`"},
                                            {"name": "model_version", "expression": "`model_version`"},
                                            {"name": "precision_pct", "expression": "`precision_pct`"},
                                            {"name": "recall_pct", "expression": "`recall_pct`"},
                                            {"name": "map50_pct", "expression": "`map50_pct`"},
                                            {"name": "map50_95_pct", "expression": "`map50_95_pct`"},
                                            {"name": "training_time", "expression": "`training_time`"},
                                            {"name": "status", "expression": "`status`"}
                                        ],
                                        "disaggregated": True
                                    }
                                }
                            ],
                            "spec": {
                                "version": 3,
                                "widgetType": "table",
                                "encodings": {
                                    "columns": [
                                        {"fieldName": "run_id", "displayName": "Run ID"},
                                        {"fieldName": "model_name", "displayName": "Model"},
                                        {"fieldName": "model_version", "displayName": "Version"},
                                        {"fieldName": "precision_pct", "displayName": "Precision (%)"},
                                        {"fieldName": "recall_pct", "displayName": "Recall (%)"},
                                        {"fieldName": "map50_pct", "displayName": "mAP@50 (%)"},
                                        {"fieldName": "map50_95_pct", "displayName": "mAP@50-95 (%)"},
                                        {"fieldName": "training_time", "displayName": "Training Time"},
                                        {"fieldName": "status", "displayName": "Status"}
                                    ]
                                }
                            },
                            "overrides": {}
                        },
                        "position": {"x": 0, "y": 9, "width": 6, "height": 4}
                    }
                ]
            }
        ],
        "datasets": [
            {
                "name": ds["name"],
                "displayName": ds["displayName"],
                "query": ds["query"]
            }
            for ds in datasets
        ]
    }

    serialized = json.dumps(dashboard_def)

    # ==========================================
    # Create the Lakeview Dashboard
    # ==========================================
    print("\n[1/2] Creating Lakeview Dashboard...")
    result = api("POST", "/api/2.0/lakeview/dashboards", {
        "display_name": "VisionAI Analytics Dashboard",
        "warehouse_id": WAREHOUSE_ID,
        "serialized_dashboard": serialized
    })

    if not result:
        print("  FAILED to create dashboard!")
        sys.exit(1)

    dashboard_id = result["dashboard_id"]
    dash_path = result.get("path", "")
    print(f"  Dashboard ID: {dashboard_id}")
    print(f"  Path: {dash_path}")

    # ==========================================
    # Publish the dashboard
    # ==========================================
    print("\n[2/2] Publishing dashboard...")
    pub = api("POST", f"/api/2.0/lakeview/dashboards/{dashboard_id}/published", {
        "warehouse_id": WAREHOUSE_ID,
        "embed_credentials": True
    })
    if pub:
        print("  [OK] Dashboard published!")
    else:
        print("  [WARN] Publish failed - dashboard is still in draft mode")

    # ==========================================
    # Summary
    # ==========================================
    dashboard_url = f"{HOST}/sql/lakeview/{dashboard_id}"
    dashboard_url2 = f"{HOST}/dashboardsv3/{dashboard_id}"

    print("\n" + "=" * 60)
    print("  VISIONAI DASHBOARD CREATED!")
    print("=" * 60)
    print(f"\n  Dashboard ID: {dashboard_id}")
    print(f"\n  Charts included:")
    print(f"    1. Detections by AI Feature (Bar Chart)")
    print(f"    2. Detection by Time Shift (Pie Chart)")
    print(f"    3. Hourly Detection Activity (Line Chart)")
    print(f"    4. AI Processing Speed (Bar Chart)")
    print(f"    5. ML Model Performance (Bar Chart)")
    print(f"    6. ML Experiment Log (Table)")
    print(f"\n  >> Open your dashboard:")
    print(f"     {dashboard_url}")
    print(f"     {dashboard_url2}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
