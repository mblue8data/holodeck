# Curriculum: Warehouse Stack

**Sequence:** `warehouse_stack`
**Level:** Beginner
**Stack:** Postgres · Dagster · Grafana

## What You Will Learn
- How a data warehouse is structured (raw → staging → marts)
- Writing SQL against a live Postgres database
- Navigating Dagster to understand asset-based orchestration
- Building a dashboard in Grafana connected to Postgres

## Prerequisites
- Basic SQL (SELECT, WHERE, GROUP BY)
- Docker running

## Start the Stack
```bash
./holo --load warehouse_stack
```

---

## Module 1 — Explore the Database

Connect to Postgres with any SQL client (TablePlus, DBeaver, psql) or use the Docker container directly:

```bash
docker exec -it holodeck-postgres-1 psql -U user -d mydb
```

**Exercise 1.1 — Inspect the schema**
```sql
\dn                             -- list schemas
\dt raw.*                       -- list tables in raw schema
SELECT * FROM raw.customers LIMIT 5;
SELECT * FROM raw.transactions LIMIT 10;
```

**Exercise 1.2 — Answer basic business questions with SQL**
```sql
-- How many customers per country?
SELECT country, COUNT(*) AS customers
FROM raw.customers
GROUP BY country
ORDER BY customers DESC;

-- What is the total revenue by currency?
SELECT currency, SUM(amount) AS total
FROM raw.transactions
WHERE status = 'completed'
GROUP BY currency;

-- Which customers have never completed a transaction?
SELECT c.name, c.email
FROM raw.customers c
LEFT JOIN raw.transactions t
  ON c.id = t.user_id AND t.status = 'completed'
WHERE t.id IS NULL;
```

**Exercise 1.3 — Add your own data**
```sql
INSERT INTO raw.customers (name, email, country)
VALUES ('Test User', 'test@example.com', 'US');

INSERT INTO raw.transactions (user_id, amount, currency, status)
VALUES (6, 500.00, 'USD', 'completed');
```

---

## Module 2 — Understand Warehouse Layers

A warehouse is organized in layers. Each layer has a different job:

| Layer | Schema | What it contains |
|-------|--------|-----------------|
| Raw | `raw` | Data exactly as it arrived — never transform this |
| Staging | `staging` | Cleaned, renamed, typed — one model per source table |
| Marts | `marts` | Business-ready aggregates — what analysts query |

**Exercise 2.1 — Create a staging view by hand**
```sql
CREATE OR REPLACE VIEW staging.stg_transactions AS
SELECT
    id             AS transaction_id,
    user_id        AS customer_id,
    amount,
    currency,
    status,
    created_at
FROM raw.transactions;

SELECT * FROM staging.stg_transactions LIMIT 5;
```

**Exercise 2.2 — Build a mart**
```sql
CREATE TABLE marts.daily_revenue AS
SELECT
    DATE(created_at)    AS day,
    currency,
    SUM(amount)         AS revenue,
    COUNT(*)            AS transaction_count
FROM raw.transactions
WHERE status = 'completed'
GROUP BY 1, 2
ORDER BY 1;

SELECT * FROM marts.daily_revenue;
```

> In production you would use dbt to manage these transformations — see the `data_modeling` curriculum.

---

## Module 3 — Dagster Orchestration

Open Dagster at **http://localhost:3010**

**Exercise 3.1 — Explore the UI**
- Navigate to **Assets** — you should see `raw_customers`, `raw_transactions`, and `customer_summary`
- Click an asset to see its description, dependencies, and run history
- Notice the lineage graph: `raw_customers` and `raw_transactions` feed into `customer_summary`

**Exercise 3.2 — Run the pipeline**
- Click **Materialize All** to execute all assets
- Watch the run log — each asset executes in dependency order
- Navigate to **Runs** to see the completed run and its output

**Exercise 3.3 — Understand the code**

The pipeline is defined in `dagster/definitions.py`. Open it and read through it.

Key concepts:
- `@asset` — a unit of data with a name, dependencies, and code that produces it
- `Definitions` — the registry that tells Dagster what exists
- `ScheduleDefinition` — runs the job on a cron schedule (currently `0 6 * * *` — 6am daily)

**Exercise 3.4 — Add your own asset**

Edit `dagster/definitions.py` and add:
```python
@asset(deps=[raw_transactions])
def failed_transactions():
    """Tracks transactions with failed status for alerting."""
    return {"status": "ready"}
```

Restart Dagster and verify the new asset appears in the UI:
```bash
./holo --stop warehouse_stack
./holo --load warehouse_stack
```

---

## Module 4 — Grafana Dashboards

Open Grafana at **http://localhost:3000** (admin / see `.env`)

The Postgres datasource is already connected — no setup needed.

**Exercise 4.1 — Run an ad-hoc query**
- Go to **Explore** (compass icon)
- Select **Holodeck Postgres** as the datasource
- Switch to **Code** mode and run:
```sql
SELECT country, COUNT(*) AS customers
FROM raw.customers
GROUP BY country;
```

**Exercise 4.2 — Build a dashboard**
- Click **+** → **New Dashboard** → **Add visualization**
- Select **Holodeck Postgres**
- Build a **Bar chart** of revenue by currency:
```sql
SELECT currency, SUM(amount) AS revenue
FROM raw.transactions
WHERE status = 'completed'
GROUP BY currency;
```
- Add a second panel: **Stat** showing total completed transactions:
```sql
SELECT COUNT(*) AS total
FROM raw.transactions
WHERE status = 'completed';
```
- Save the dashboard as **Holodeck Overview**

**Exercise 4.3 — Time series panel**
```sql
SELECT
    DATE(created_at) AS time,
    SUM(amount)      AS revenue
FROM raw.transactions
WHERE status = 'completed'
GROUP BY 1
ORDER BY 1;
```
Set visualization to **Time series** and observe the trend.

---

## Checkpoint

Before moving on, you should be able to:
- [ ] Connect to Postgres and query all three schema layers
- [ ] Explain the purpose of raw, staging, and marts
- [ ] Run the Dagster pipeline and read the asset graph
- [ ] Build a basic Grafana dashboard with at least two panels

## Next Steps
- **`data_modeling`** — automate your staging and mart models with dbt
- **`devops_stack`** — manage schema changes with Atlas
