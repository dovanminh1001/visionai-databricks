# VisionAI — Azure Databricks + GitHub CI/CD

This repository contains the data engineering and machine learning pipelines for the **VisionAI** Object Detection System, targeting **Azure Databricks** with Medallion Architecture (Bronze/Silver/Gold).

## Architecture
1. **Bronze Layer**: Raw camera feeds ingestion via Databricks Auto Loader.
2. **Silver Layer**: Data cleansing and enrichment.
3. **Gold Layer**: Aggregations for BI dashboards and YOLOv8 ML model training via MLflow.

## CI/CD Pipeline
GitHub Actions workflow runs on every push:
1. `pytest` unit testing.
2. `databricks bundle validate` to verify deployment configuration.
