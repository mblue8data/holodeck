# Holodeck — Data Engineering Training Platform

A local, Docker-based sandbox for building real data engineering skills without a cloud account.
Spin up pre-wired stacks covering warehousing, data modeling, orchestration, ML tracking,
analytics, and DevOps/DataOps — all from a single CLI.

```
./holo --load warehouse_stack
```

---

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Docker Desktop | Latest | Must be running before `./holo` |
| Python | 3.11+ | For the `holo` CLI and `bluefaker_factory` |
| pip | Latest | `pip install -r requirements.txt` |

---

## Getting Started

**1. Install CLI dependencies**
```bash
pip install -r requirements.txt
```

**2. Set up your environment file**
```bash
cp .env.example .env
# Edit .env and fill in any credentials you want to change
# The defaults work out of the box for local development
```

**3. List available stacks**
```bash
./holo --list
```

**4. Load a stack**
```bash
./holo --load warehouse_stack
```

---

## CLI Reference

```
./holo --list                    List all available sequences
./holo --load <sequence>         Start a sequence (builds images if needed)
./holo --stop <sequence>         Stop containers without removing them
./holo --reset <sequence>        Stop and remove containers (clean slate)
./holo --status                  Show status of all running containers
./holo --status <sequence>       Show status for a specific sequence
./holo --test <sequence>         Run smoke tests against a running sequence
./holo --dry-run <sequence>      Preview what would be started
```

---

## Stacks

### `warehouse_stack`
**Services:** Postgres · Dagster · Grafana

The core data warehouse stack. Postgres holds raw and modeled data, Dagster orchestrates
pipelines, and Grafana provides dashboards connected directly to Postgres.

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | http://localhost:3000 | admin / *(see .env)* |
| Dagster | http://localhost:3010 | — |
| Postgres | localhost:5432 | *(see .env)* |

On first boot, Postgres is seeded with `raw.customers` and `raw.transactions` tables
and a handful of sample rows so you have data to work with immediately.

---

### `data_modeling`
**Services:** Postgres · dbt-postgres

Runs dbt against the Postgres warehouse. Models live in `data_modeling/dbt/models/`.
The project ships with a working staging and marts layer out of the box.

```
data_modeling/dbt/
├── dbt_project.yml
├── profiles.yml
└── models/
    ├── staging/
    │   ├── sources.yml
    │   ├── stg_customers.sql
    │   └── stg_transactions.sql
    └── marts/
        └── mart_customer_summary.sql
```

**Run dbt manually inside the container:**
```bash
docker exec -it holodeck-dbt-postgres-1 dbt run
docker exec -it holodeck-dbt-postgres-1 dbt test
docker exec -it holodeck-dbt-postgres-1 dbt docs generate
```

---

### `dbt_test`
**Services:** Postgres · Grafana

Lightweight stack for testing dbt output in Grafana without running the full warehouse stack.

---

### `devops_stack`
**Services:** Postgres · LocalStack · Terraform · Atlas

Practice DevOps and DataOps workflows entirely locally — no cloud account required.

| Service | URL | Purpose |
|---------|-----|---------|
| LocalStack | http://localhost:4566 | AWS emulation (S3, IAM, STS) |
| Terraform | — | IaC against LocalStack |
| Atlas | — | Declarative schema migrations for Postgres |

**Terraform — provision the data lake:**
```bash
docker exec -it terraform sh
terraform init
terraform plan
terraform apply
```
This creates three S3 buckets (`holodeck-raw`, `holodeck-staging`, `holodeck-marts`) and an
IAM role in LocalStack — the same pattern you would use against real AWS.

**Atlas — manage schema changes:**
```bash
docker exec -it atlas sh

# See what Atlas would change to match schema.hcl
atlas schema diff --env local

# Apply the schema to Postgres
atlas schema apply --env local
```

To practice a migration: edit `devops/atlas/schema.hcl` (add a column, a table, an index),
then run `atlas schema apply`. Atlas generates the SQL and applies it — the same workflow
used in production data orgs.

Schema and Terraform configs live in:
```
devops/
├── terraform/
│   ├── main.tf        # S3 buckets + IAM role
│   ├── variables.tf
│   └── outputs.tf
└── atlas/
    ├── schema.hcl     # Desired database state — edit this to practice migrations
    └── atlas.hcl      # Connection config
```

---

### `duckdb_lab`
**Services:** DuckLake · DuckDB · Marimo

Analytical lab using DuckDB for in-process queries and Marimo for interactive Python notebooks.
Seed data (fraud dataset) is generated automatically via `bluefaker_factory` on first load.

| Service | URL |
|---------|-----|
| Marimo notebooks | http://localhost:8888 |
| DuckLake data server | http://localhost:9000 |

---

### `basic_ml_stack`
**Services:** MLflow · Dagster

Track experiments and model runs locally with MLflow backed by Dagster orchestration.

| Service | URL |
|---------|-----|
| MLflow | http://localhost:5000 |
| Dagster | http://localhost:3010 |

---

### `datalake_stack`
**Services:** MinIO · DuckDB-Lake · Marimo

Local data lake built on S3-compatible object storage with Apache Iceberg as the table format.
Teaches the medallion architecture (bronze → silver → gold), Iceberg time travel, schema
evolution, and querying lake data interactively via Marimo notebooks.

| Service | URL | Credentials |
|---------|-----|-------------|
| MinIO Console | http://localhost:9002 | see `.env` |
| MinIO S3 API | http://localhost:9001 | — |
| Marimo | http://localhost:8888 | — |

**First run:** open the MinIO console and create three buckets: `bronze`, `silver`, `gold`.

---

### `full_stack`
**Services:** Postgres · Dagster · Grafana · Mage

Everything in `warehouse_stack` plus Mage for additional pipeline authoring.

| Service | URL |
|---------|-----|
| Grafana | http://localhost:3000 |
| Dagster | http://localhost:3010 |
| Mage | http://localhost:6789 |

---

## Synthetic Data

`tools/bluefaker_factory` generates realistic fake datasets from YAML schemas.
Pre-built schemas are available for fraud, churn, transactions, support tickets, and ML features.

```bash
# Install
pip install -e tools/bluefaker_factory

# Generate 100k rows of fraud data as parquet
python tools/bluefaker_factory/bluefaker.py \
  --schema tools/bluefaker_factory/schemas/fraud_schema.yaml \
  --records 100000 \
  --format parquet \
  --file data/raw/fraud_data01
```

---

## Environment Variables

All credentials are loaded from `.env`. Never commit this file.

```bash
cp .env.example .env
```

See `.env.example` for all required variables. The defaults work for local development.

---

## Project Structure

```
holodeck/
├── holo                      CLI entry point
├── docker-compose.yml        All service definitions
├── .env                      Local credentials (git-ignored)
├── .env.example              Template — commit this, not .env
├── docker/                   One Dockerfile per service
├── init/postgres/            SQL scripts run on first Postgres boot
├── data_modeling/dbt/        dbt project (models, profiles, project config)
├── devops/
│   ├── terraform/            Terraform configs targeting LocalStack
│   └── atlas/                Atlas schema HCL and migration config
├── dagster/                  Dagster workspace, definitions, and home dir
├── grafana/provisioning/     Auto-provisioned Grafana datasources
├── tools/
│   ├── bluefaker_factory/    Synthetic data generator
│   └── ascii/                Banner utilities used by the CLI
└── data/                     Runtime data directory (git-ignored)
```

---

## Curriculum

Each sequence has a dedicated curriculum with modules, exercises, and checkpoints.
Work through them in order — each one builds on the last.

| # | Sequence | Level | Curriculum |
|---|----------|-------|------------|
| 1 | `warehouse_stack` | Beginner | [01_warehouse_stack.md](curriculum/01_warehouse_stack.md) |
| 2 | `data_modeling` | Intermediate | [02_data_modeling.md](curriculum/02_data_modeling.md) |
| 3 | `dbt_test` | Beginner | [03_dbt_test.md](curriculum/03_dbt_test.md) |
| 4 | `devops_stack` | Intermediate | [04_devops_stack.md](curriculum/04_devops_stack.md) |
| 5 | `duckdb_lab` | Beginner–Intermediate | [05_duckdb_lab.md](curriculum/05_duckdb_lab.md) |
| 6 | `basic_ml_stack` | Intermediate | [06_basic_ml_stack.md](curriculum/06_basic_ml_stack.md) |
| 7 | `full_stack` | Advanced | [07_full_stack.md](curriculum/07_full_stack.md) |
| 8 | `datalake_stack` | Intermediate | [08_datalake_stack.md](curriculum/08_datalake_stack.md) |

---

## Component Documentation

| Component | Docs | Description |
|-----------|------|-------------|
| **PostgreSQL** | https://www.postgresql.org/docs/ | Relational database — primary warehouse store |
| **MySQL** | https://dev.mysql.com/doc/ | Relational database — available as a source DB |
| **Redis** | https://redis.io/docs/ | In-memory data store — caching and queuing |
| **MongoDB** | https://www.mongodb.com/docs/ | Document database — unstructured data source |
| **dbt** | https://docs.getdbt.com/ | SQL-based data transformation and modeling |
| **Dagster** | https://docs.dagster.io/ | Data pipeline orchestration and asset management |
| **Grafana** | https://grafana.com/docs/grafana/latest/ | Dashboards and data visualization |
| **MLflow** | https://mlflow.org/docs/latest/index.html | ML experiment tracking and model registry |
| **Mage AI** | https://docs.mage.ai/ | Modern data pipeline and ETL authoring |
| **DuckDB** | https://duckdb.org/docs/ | In-process analytical SQL engine |
| **Marimo** | https://docs.marimo.io/ | Reactive Python notebooks for data exploration |
| **LocalStack** | https://docs.localstack.cloud/ | Local AWS cloud emulation for Terraform practice |
| **Terraform** | https://developer.hashicorp.com/terraform/docs | Infrastructure as Code — provisions cloud resources |
| **Atlas** | https://atlasgo.io/docs | Declarative database schema management and migrations |
| **MinIO** | https://min.io/docs/minio/container/index.html | S3-compatible local object storage — data lake foundation |
| **Apache Iceberg** | https://iceberg.apache.org/docs/latest/ | Open table format for data lakes — ACID, time travel, schema evolution |

---

## Tips

- **Port conflicts** — each sequence uses fixed ports. Stop one sequence before starting another
  if they share services (e.g. both use port 5432 for Postgres).
- **Clean slate** — `./holo --reset <sequence>` removes containers. Add `-v` manually to
  `docker-compose` if you also want to wipe named volumes.
- **First boot is slow** — images are built on first `--load`. Subsequent starts are fast.
- **Grafana datasource** — Postgres is provisioned automatically. Open Explore and start querying.
