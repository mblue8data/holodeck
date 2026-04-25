# Curriculum: DuckDB Lab

**Sequence:** `duckdb_lab`
**Level:** Beginner – Intermediate
**Stack:** DuckLake · DuckDB · Marimo

## What You Will Learn
- Querying parquet files directly with DuckDB — no loading required
- Analytical SQL patterns: window functions, aggregations, CTEs
- Building interactive, reactive notebooks in Marimo
- The difference between OLTP (Postgres) and OLAP (DuckDB) query patterns

## Prerequisites
- Basic SQL (SELECT, WHERE, GROUP BY)
- Python basics helpful but not required for early modules

## Start the Stack
```bash
./holo --load duckdb_lab
```

On first load, `holodeck` auto-generates a 100,000-row fraud dataset in `data/raw/fraud_data01.parquet`
using `bluefaker_factory`. This is your training data.

---

## Module 1 — Query Parquet with DuckDB

DuckDB can query parquet files directly on disk — no database, no loading, no schema setup.

```bash
docker exec -it duckdb python3 -c "import duckdb; duckdb.sql(\"SELECT 1\").show()"
```

Or start an interactive Python session:
```bash
docker exec -it duckdb python3
```

```python
import duckdb

# Query the parquet file directly
duckdb.sql("SELECT * FROM '/data/raw/fraud_data01.parquet' LIMIT 5").show()
```

**Exercise 1.1 — Inspect the schema**
```python
duckdb.sql("DESCRIBE SELECT * FROM '/data/raw/fraud_data01.parquet'").show()
```

**Exercise 1.2 — Count and profile**
```python
# Row count
duckdb.sql("SELECT COUNT(*) FROM '/data/raw/fraud_data01.parquet'").show()

# Value distribution
duckdb.sql("""
    SELECT is_fraud, COUNT(*) AS count, ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
    FROM '/data/raw/fraud_data01.parquet'
    GROUP BY is_fraud
""").show()
```

**Exercise 1.3 — Persist to a DuckDB database file**
```python
con = duckdb.connect('/data/holodeck.duckdb')
con.execute("""
    CREATE TABLE IF NOT EXISTS fraud AS
    SELECT * FROM '/data/raw/fraud_data01.parquet'
""")
con.sql("SELECT COUNT(*) FROM fraud").show()
```

Now you have a persistent database. Subsequent sessions can reconnect:
```python
con = duckdb.connect('/data/holodeck.duckdb')
con.sql("SHOW TABLES").show()
```

---

## Module 2 — Analytical SQL Patterns

DuckDB shines at OLAP queries. These patterns come up constantly in data engineering.

**Exercise 2.1 — Window functions**
```python
con.sql("""
    SELECT
        user_id,
        transaction_amount,
        AVG(transaction_amount) OVER (PARTITION BY user_id) AS user_avg,
        transaction_amount - AVG(transaction_amount) OVER (PARTITION BY user_id) AS deviation_from_avg
    FROM fraud
    ORDER BY deviation_from_avg DESC
    LIMIT 20
""").show()
```

**Exercise 2.2 — Running totals**
```python
con.sql("""
    SELECT
        transaction_date,
        SUM(transaction_amount) AS daily_total,
        SUM(SUM(transaction_amount)) OVER (ORDER BY transaction_date) AS running_total
    FROM fraud
    GROUP BY transaction_date
    ORDER BY transaction_date
    LIMIT 30
""").show()
```

**Exercise 2.3 — Fraud rate by merchant category**
```python
con.sql("""
    WITH stats AS (
        SELECT
            merchant_category,
            COUNT(*) AS total,
            SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) AS fraud_count
        FROM fraud
        GROUP BY merchant_category
    )
    SELECT
        merchant_category,
        total,
        fraud_count,
        ROUND(fraud_count * 100.0 / total, 2) AS fraud_rate_pct
    FROM stats
    ORDER BY fraud_rate_pct DESC
""").show()
```

**Exercise 2.4 — Percentiles**
```python
con.sql("""
    SELECT
        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY transaction_amount) AS median,
        PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY transaction_amount) AS p90,
        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY transaction_amount) AS p99,
        MAX(transaction_amount) AS max
    FROM fraud
""").show()
```

---

## Module 3 — Marimo Notebooks

Open Marimo at **http://localhost:8888**

Marimo is a reactive Python notebook — when you change a cell, every cell that depends on it
re-runs automatically. This makes it great for interactive data exploration.

**Exercise 3.1 — Create your first notebook**
- Click **+** to create a new notebook
- Name it `fraud_analysis.py`

**Exercise 3.2 — Connect to DuckDB in Marimo**

Add a cell:
```python
import duckdb
import marimo as mo

con = duckdb.connect('/workspace/data/holodeck.duckdb')
```

Add a second cell:
```python
df = con.execute("SELECT * FROM fraud LIMIT 1000").df()
df.head()
```

**Exercise 3.3 — Add a reactive slider**

```python
sample_size = mo.ui.slider(1000, 50000, step=1000, label="Sample size")
sample_size
```

In the next cell, reference it — it re-runs automatically when the slider moves:
```python
df = con.execute(f"SELECT * FROM fraud LIMIT {sample_size.value}").df()
mo.stat(label="Rows loaded", value=str(len(df)))
```

**Exercise 3.4 — Build a fraud analysis notebook**

Add cells progressively:

```python
# Fraud rate
fraud_rate = con.execute("""
    SELECT ROUND(AVG(CAST(is_fraud AS INT)) * 100, 2) AS fraud_rate_pct
    FROM fraud
""").df()
mo.stat(label="Fraud rate %", value=str(fraud_rate['fraud_rate_pct'][0]))
```

```python
# Top fraud categories
top_categories = con.execute("""
    SELECT merchant_category, COUNT(*) AS fraud_count
    FROM fraud
    WHERE is_fraud = true
    GROUP BY merchant_category
    ORDER BY fraud_count DESC
    LIMIT 10
""").df()
top_categories
```

```python
# Amount distribution for fraud vs legit
import matplotlib.pyplot as plt

fraud_amounts = con.execute("SELECT transaction_amount FROM fraud WHERE is_fraud = true LIMIT 5000").df()
legit_amounts = con.execute("SELECT transaction_amount FROM fraud WHERE is_fraud = false LIMIT 5000").df()

fig, ax = plt.subplots()
ax.hist(legit_amounts['transaction_amount'], bins=50, alpha=0.5, label='Legit')
ax.hist(fraud_amounts['transaction_amount'], bins=50, alpha=0.5, label='Fraud')
ax.legend()
ax.set_title('Transaction Amount: Fraud vs Legit')
mo.pyplot(fig)
```

---

## Module 4 — Generate Your Own Dataset

The `bluefaker_factory` tool lets you create custom datasets for any scenario.

**Exercise 4.1 — Generate a new schema**

Explore the existing schemas in `tools/bluefaker_factory/schemas/`. Then generate a churn dataset:
```bash
python tools/bluefaker_factory/bluefaker.py \
  --schema tools/bluefaker_factory/schemas/churn_schema.yml \
  --records 50000 \
  --format parquet \
  --file data/raw/churn_data01
```

**Exercise 4.2 — Query the new dataset in DuckDB**
```python
churn = con.execute("SELECT * FROM '/data/raw/churn_data01.parquet' LIMIT 5").df()
churn
```

**Exercise 4.3 — Join two datasets**
```python
# If both datasets share a user_id field, you can join them
con.execute("""
    SELECT
        f.user_id,
        f.transaction_amount,
        c.churn_risk
    FROM '/data/raw/fraud_data01.parquet' f
    JOIN '/data/raw/churn_data01.parquet' c USING (user_id)
    LIMIT 10
""").show()
```

---

## Checkpoint

Before moving on, you should be able to:
- [ ] Query a parquet file directly with DuckDB without loading it first
- [ ] Write window functions and aggregate analytical queries
- [ ] Build a Marimo notebook with at least one reactive UI element
- [ ] Generate a custom dataset with `bluefaker_factory`

## Next Steps
- **`basic_ml_stack`** — use DuckDB-processed features to train and track ML models
- **`warehouse_stack`** — move DuckDB insights into Postgres for dashboard consumption
