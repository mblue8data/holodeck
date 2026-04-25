# Curriculum: Full Stack — Capstone

**Sequence:** `full_stack`
**Level:** Advanced
**Stack:** Postgres · Dagster · Grafana · Mage

## What You Will Learn
- How all the components of a modern data stack connect end-to-end
- Building a complete pipeline: ingest → transform → model → visualize
- Using Mage for pipeline authoring alongside Dagster for orchestration
- Designing a data product from raw data to a monitored dashboard

## Prerequisites
- Completed `warehouse_stack` and `data_modeling` curricula
- Familiar with Dagster assets and Grafana dashboards
- Basic Python

## Start the Stack
```bash
./holo --load full_stack
```

| Service | URL |
|---------|-----|
| Grafana | http://localhost:3000 |
| Dagster | http://localhost:3010 |
| Mage | http://localhost:6789 |
| Postgres | localhost:5432 |

---

## Module 1 — Map the Full Architecture

Before writing any code, draw the data flow on paper or a whiteboard:

```
[bluefaker_factory]
        ↓ generates parquet
[raw.customers / raw.transactions]  ← Postgres raw layer
        ↓ dbt staging models
[staging.stg_customers / stg_transactions]
        ↓ dbt mart models
[marts.mart_customer_summary / mart_revenue_by_country]
        ↓ Dagster orchestrates
[Grafana dashboards] ← visualization layer
        ↑
[Mage]  ← alternative pipeline authoring / ingestion
```

**Exercise 1.1 — Audit what is already working**
```bash
./holo --status full_stack
./holo --test full_stack
```

Confirm Postgres, Dagster, and Grafana are healthy. If Grafana is not showing data, check the
datasource is connected: **Configuration → Data Sources → Holodeck Postgres → Test**.

---

## Module 2 — Build a Pipeline in Mage

Mage is a modern pipeline tool with a visual block-based interface. It complements Dagster —
Mage excels at authoring individual pipelines quickly; Dagster excels at asset management and scheduling.

Open Mage at **http://localhost:6789**

**Exercise 2.1 — Create a pipeline**
- Click **+ New Pipeline** → **Standard (batch)**
- Name it `customer_ingest`

**Exercise 2.2 — Add a data loader block**
- Click **+** → **Data loader** → **Python**
- Name it `load_customers`

```python
import pandas as pd
import psycopg2

@data_loader
def load_data(*args, **kwargs):
    conn = psycopg2.connect(
        host='postgres', port=5432,
        dbname='mydb', user='user', password='pass'
    )
    df = pd.read_sql("SELECT * FROM raw.customers", conn)
    conn.close()
    return df

@test
def test_output(output, *args):
    assert output is not None, "Output is None"
    assert len(output) > 0, "No rows returned"
```

**Exercise 2.3 — Add a transformer block**
- Click **+** → **Transformer** → **Python**
- Name it `enrich_customers`

```python
@transformer
def transform(df, *args, **kwargs):
    df['email_domain'] = df['email'].str.split('@').str[1]
    df['name_length']  = df['name'].str.len()
    return df

@test
def test_output(output, *args):
    assert 'email_domain' in output.columns
```

**Exercise 2.4 — Add a data exporter block**
- Click **+** → **Data exporter** → **Python**
- Name it `export_to_postgres`

```python
import psycopg2
from psycopg2.extras import execute_values

@data_exporter
def export_data(df, *args, **kwargs):
    conn = psycopg2.connect(
        host='postgres', port=5432,
        dbname='mydb', user='user', password='pass'
    )
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS staging.enriched_customers AS
        SELECT *, NULL::text AS email_domain, NULL::int AS name_length
        FROM staging.stg_customers WHERE FALSE
    """)
    execute_values(
        cur,
        "INSERT INTO staging.enriched_customers VALUES %s ON CONFLICT DO NOTHING",
        df.values.tolist()
    )
    conn.commit()
    conn.close()
```

Run the pipeline from the Mage UI and verify the table appears in Postgres.

---

## Module 3 — Connect Mage to Dagster

Rather than running Mage pipelines manually, trigger them from Dagster.

**Exercise 3.1 — Add a Dagster asset that calls Mage**

Edit `dagster/definitions.py`:
```python
import requests
from dagster import asset, Definitions

MAGE_URL = "http://mage:6789"

@asset
def customer_ingest():
    """Triggers the customer_ingest pipeline in Mage."""
    resp = requests.post(
        f"{MAGE_URL}/api/pipeline_schedules/1/pipeline_runs",
        json={"pipeline_run": {"variables": {}}},
        headers={"Content-Type": "application/json"},
    )
    resp.raise_for_status()
    return {"status": "triggered"}
```

> Note: adjust the pipeline schedule ID to match what Mage assigns your pipeline.

**Exercise 3.2 — Run the full asset graph in Dagster**
- Open Dagster at **http://localhost:3010** → **Assets**
- Materialize all — observe `customer_ingest` triggering Mage, then downstream dbt assets running

---

## Module 4 — End-to-End Dashboard

Build the final monitoring dashboard in Grafana that consumes everything.

**Exercise 4.1 — Create an Operations Dashboard**

Open Grafana → **+** → **New Dashboard** → name it **Holodeck Operations**

**Panel 1 — Pipeline health (Table)**
```sql
SELECT
    'raw.customers'              AS table_name,
    COUNT(*)                     AS row_count,
    MAX(created_at)              AS last_updated
FROM raw.customers
UNION ALL
SELECT 'raw.transactions', COUNT(*), MAX(created_at) FROM raw.transactions
UNION ALL
SELECT 'marts.mart_customer_summary', COUNT(*), NULL FROM marts.mart_customer_summary;
```

**Panel 2 — Revenue trend (Time series)**
```sql
SELECT
    DATE(created_at)  AS time,
    SUM(amount)       AS revenue
FROM raw.transactions
WHERE status = 'completed'
GROUP BY 1
ORDER BY 1;
```

**Panel 3 — Customer by country (Geomap or Bar chart)**
```sql
SELECT country, COUNT(*) AS customers
FROM raw.customers
GROUP BY country
ORDER BY customers DESC;
```

**Panel 4 — Fraud flag rate (Stat)**
```sql
SELECT
    ROUND(
        COUNT(*) FILTER (WHERE status = 'failed') * 100.0 / COUNT(*),
        2
    ) AS failure_rate_pct
FROM raw.transactions;
```

**Exercise 4.2 — Set a dashboard refresh interval**
- In dashboard settings, set **Auto refresh** to `30s`
- Insert a new transaction in Postgres and watch the panels update live

---

## Module 5 — Design Challenge

Now that you understand all the pieces, build something original.

**Challenge: Customer Lifetime Value Pipeline**

Design and build a pipeline that answers:
> *"Which customers are most valuable to the business, and are they growing or declining?"*

Requirements:
1. Raw data lives in `raw.customers` and `raw.transactions`
2. A new dbt mart: `mart_customer_ltv` with columns: `customer_id`, `name`, `country`, `total_revenue`, `transaction_count`, `avg_order_value`, `days_since_last_purchase`
3. A Dagster asset that materializes the mart on a schedule
4. A Grafana panel showing the top 10 customers by LTV
5. An alert threshold: flag any customer with `days_since_last_purchase > 30` in red

---

## Checkpoint

Before considering this sequence complete, you should be able to:
- [ ] Describe the full data flow from raw source to dashboard panel
- [ ] Build and run a Mage pipeline with loader, transformer, and exporter blocks
- [ ] Trigger a Mage pipeline from a Dagster asset
- [ ] Build an operations dashboard in Grafana with 4+ panels from different layers
- [ ] Complete the design challenge end-to-end

## Congratulations

You have worked through the complete Holodeck curriculum:

| Sequence | Skill |
|----------|-------|
| `warehouse_stack` | SQL, schema layers, orchestration basics, dashboards |
| `data_modeling` | dbt — sources, staging, marts, tests, docs |
| `dbt_test` | Data quality validation and reconciliation |
| `devops_stack` | Terraform IaC, Atlas schema migrations, DataOps workflow |
| `duckdb_lab` | Analytical SQL, parquet, reactive notebooks |
| `basic_ml_stack` | Experiment tracking, model registry, ML orchestration |
| `full_stack` | End-to-end pipeline design and delivery |

The skills here map directly to real data engineering roles. The only difference between
this sandbox and production is the scale of data and the cloud provider — the tools,
patterns, and workflows are identical.
