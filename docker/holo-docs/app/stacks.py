SEQUENCES = {
    "warehouse_stack": {
        "title": "Warehouse Stack",
        "level": "Beginner",
        "services": ["postgres", "dagster", "grafana"],
        "curriculum": "01_warehouse_stack.md",
        "endpoints": [
            {"name": "Grafana", "url": "http://localhost:3001", "note": "admin / see .env"},
            {"name": "Dagster", "url": "http://localhost:3010"},
            {"name": "Postgres", "url": "localhost:5432", "note": "see .env"},
        ],
    },
    "data_modeling": {
        "title": "Data Modeling (dbt)",
        "level": "Intermediate",
        "services": ["postgres", "dbt-postgres"],
        "curriculum": "02_data_modeling.md",
        "endpoints": [
            {"name": "Postgres", "url": "localhost:5432", "note": "see .env"},
        ],
    },
    "dataops_quality_stack": {
        "title": "DataOps — Quality & Observability",
        "level": "Intermediate",
        "services": ["postgres", "dbt-postgres", "soda", "grafana"],
        "curriculum": "03_dataops_quality_stack.md",
        "endpoints": [
            {"name": "Grafana", "url": "http://localhost:3001", "note": "data quality dashboards"},
            {"name": "Postgres", "url": "localhost:5432"},
        ],
    },
    "dataops_infra_stack": {
        "title": "DataOps — Infrastructure & Schema",
        "level": "Intermediate",
        "services": ["postgres", "localstack", "terraform", "atlas", "grafana"],
        "curriculum": "04_dataops_infra_stack.md",
        "endpoints": [
            {"name": "LocalStack", "url": "http://localhost:4566", "note": "AWS emulation"},
            {"name": "Grafana", "url": "http://localhost:3001"},
            {"name": "Postgres", "url": "localhost:5432"},
        ],
    },
    "duckdb_lab": {
        "title": "DuckDB Lab",
        "level": "Beginner–Intermediate",
        "services": ["ducklake", "duckdb", "marimo"],
        "curriculum": "05_duckdb_lab.md",
        "endpoints": [
            {"name": "Marimo", "url": "http://localhost:8888"},
            {"name": "DuckLake", "url": "http://localhost:9000"},
        ],
    },
    "basic_ml_stack": {
        "title": "Basic ML Stack",
        "level": "Intermediate",
        "services": ["mlflow", "dagster"],
        "curriculum": "06_basic_ml_stack.md",
        "endpoints": [
            {"name": "MLflow", "url": "http://localhost:5000"},
            {"name": "Dagster", "url": "http://localhost:3010"},
        ],
    },
    "full_stack": {
        "title": "Full Stack",
        "level": "Advanced",
        "services": ["postgres", "dagster", "grafana", "mage"],
        "curriculum": "07_full_stack.md",
        "endpoints": [
            {"name": "Grafana", "url": "http://localhost:3001"},
            {"name": "Dagster", "url": "http://localhost:3010"},
            {"name": "Mage", "url": "http://localhost:6789"},
            {"name": "Postgres", "url": "localhost:5432"},
        ],
    },
    "datalake_stack": {
        "title": "Data Lake Stack",
        "level": "Intermediate",
        "services": ["minio", "duckdb-lake", "marimo"],
        "curriculum": "08_datalake_stack.md",
        "endpoints": [
            {"name": "MinIO Console", "url": "http://localhost:9002", "note": "see .env"},
            {"name": "MinIO S3 API", "url": "http://localhost:9001"},
            {"name": "Marimo", "url": "http://localhost:8888"},
        ],
    },
}
