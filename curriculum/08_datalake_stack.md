# Curriculum: Data Lake

**Sequence:** `datalake_stack`
**Level:** Intermediate
**Stack:** MinIO · DuckDB (with Iceberg extension) · Marimo

## What You Will Learn
- What a data lake is and how it differs from a data warehouse
- Object storage concepts — buckets, prefixes, objects
- The medallion architecture — bronze, silver, gold layers
- Apache Iceberg — why open table formats exist and what they give you
- Writing and querying Iceberg tables from DuckDB against local S3 (MinIO)
- Time travel and schema evolution with Iceberg

## Prerequisites
- Comfortable with Python and SQL
- Completed `warehouse_stack` helpful but not required

## Start the Stack
```bash
./holo --load datalake_stack
```

| Service | URL | Credentials |
|---------|-----|-------------|
| MinIO Console | http://localhost:9002 | see `.env` |
| MinIO S3 API | http://localhost:9001 | — |
| Marimo | http://localhost:8888 | — |

---

## Module 1 — Object Storage and the Data Lake Concept

### Warehouse vs Lake

| | Data Warehouse | Data Lake |
|-|---------------|-----------|
| Storage | Database engine manages files | Raw files on object storage (S3/MinIO) |
| Format | Proprietary (Postgres pages, etc.) | Open (Parquet, Iceberg, CSV) |
| Schema | Enforced on write | Applied on read (or with table formats) |
| Cost | Higher (compute bundled with storage) | Lower (separate compute and storage) |
| Best for | Structured, modeled data | Raw + structured + semi-structured |

In practice, most modern data platforms use **both** — a lake for raw storage, a warehouse
for modeled marts. The lake is the source of truth; the warehouse is optimized for queries.

### Medallion Architecture

The lake is organized in three layers:

```
bronze/   ← raw data exactly as received — never modified
silver/   ← cleaned, validated, deduplicated
gold/     ← aggregated, business-ready (same as warehouse marts)
```

**Exercise 1.1 — Create the three buckets in MinIO**

Open the MinIO Console at **http://localhost:9002** and log in (credentials in `.env`).

- Click **Create Bucket** → name it `bronze` → Create
- Repeat for `silver` and `gold`

You now have three logical lake zones, each backed by independent object storage.

---

## Module 2 — Connect DuckDB to MinIO

DuckDB can read and write files on S3-compatible storage using the `httpfs` extension.

```bash
docker exec -it duckdb-lake python3
```

```python
import duckdb

con = duckdb.connect()

# Install and load the S3 extension
con.execute("INSTALL httpfs; LOAD httpfs;")

# Point DuckDB at MinIO instead of AWS
con.execute("""
    SET s3_endpoint      = 'minio:9000';
    SET s3_access_key_id = 'minioadmin';
    SET s3_secret_access_key = 'minioadmin123';
    SET s3_use_ssl       = false;
    SET s3_url_style     = 'path';
""")

# Verify the connection — list the bronze bucket
result = con.execute("SELECT * FROM glob('s3://bronze/**')").fetchall()
print("Files in bronze:", result)
```

**Exercise 2.1 — Write your first file to the lake**

```python
import pandas as pd

# Create a sample dataframe
df = pd.DataFrame({
    'id':      [1, 2, 3, 4, 5],
    'name':    ['Alice', 'Bob', 'Clara', 'David', 'Eva'],
    'country': ['US', 'NG', 'DE', 'KR', 'RU'],
    'amount':  [120.50, 45.00, 300.00, 15.99, 89.00],
})

# Write it as parquet directly to MinIO bronze layer
con.execute("COPY (SELECT * FROM df) TO 's3://bronze/customers/customers_001.parquet' (FORMAT PARQUET)")
print("Written to bronze.")
```

**Exercise 2.2 — Read it back**

```python
df_back = con.execute("SELECT * FROM 's3://bronze/customers/customers_001.parquet'").df()
print(df_back)
```

You just wrote and read a file in object storage — this is the foundation of a data lake.

**Exercise 2.3 — Understand partitioning**

A flat bucket becomes slow at scale. Partitioning organizes files by a key:

```python
# Write multiple files simulating partitioned ingestion
for country in ['US', 'NG', 'DE']:
    subset = df[df['country'] == country]
    path = f's3://bronze/customers/country={country}/data.parquet'
    con.execute(f"COPY (SELECT * FROM subset) TO '{path}' (FORMAT PARQUET)")

# Query across all partitions with a wildcard
result = con.execute("""
    SELECT country, COUNT(*) AS rows
    FROM 's3://bronze/customers/**/*.parquet'
    GROUP BY country
""").df()
print(result)
```

---

## Module 3 — Apache Iceberg

Parquet files are great but they have no transaction support, no schema history, and no
way to update or delete rows without rewriting whole files. **Iceberg** solves this.

Iceberg adds a metadata layer on top of Parquet files that gives you:
- **ACID transactions** — concurrent reads and writes are safe
- **Schema evolution** — add/rename/drop columns without rewriting data
- **Time travel** — query the table as it looked at any point in the past
- **Hidden partitioning** — partition the data without embedding it in the query

### Install the Iceberg extension

```python
con.execute("INSTALL iceberg; LOAD iceberg;")
```

**Exercise 3.1 — Create an Iceberg table on MinIO**

```python
# Create an Iceberg table in the silver layer
con.execute("""
    CREATE TABLE delta_customers (
        customer_id  INTEGER,
        name         VARCHAR,
        country      VARCHAR,
        email        VARCHAR,
        created_at   TIMESTAMP DEFAULT now()
    )
""")

# For Iceberg on S3, configure the catalog
# DuckDB writes Iceberg metadata alongside data files
con.execute("""
    CREATE SECRET minio_secret (
        TYPE S3,
        KEY_ID       'minioadmin',
        SECRET       'minioadmin123',
        ENDPOINT     'minio:9000',
        USE_SSL      false,
        URL_STYLE    'path'
    )
""")

# Create the Iceberg table on MinIO
con.execute("""
    CREATE TABLE iceberg_customers
    USING ICEBERG
    LOCATION 's3://silver/customers/'
    AS SELECT * FROM 's3://bronze/customers/customers_001.parquet'
""")

print("Iceberg table created in silver.")
```

**Exercise 3.2 — Insert and update rows**

```python
# Insert new rows
con.execute("""
    INSERT INTO iceberg_customers VALUES
    (6, 'Frank Chen', 'SG', 'frank@example.com', now()),
    (7, 'Grace Obi',  'NG', 'grace@example.com', now())
""")

# Verify
con.execute("SELECT * FROM iceberg_customers ORDER BY customer_id").show()
```

Unlike plain Parquet, this works as a proper ACID insert — no file rewriting needed.

---

## Module 4 — Time Travel

One of Iceberg's most powerful features: query any previous snapshot of a table.

**Exercise 4.1 — Build up some history**

```python
# Snapshot 1 — baseline
con.execute("INSERT INTO iceberg_customers VALUES (8, 'Henry Wu', 'TW', 'henry@example.com', now())")

# Snapshot 2 — more inserts
con.execute("INSERT INTO iceberg_customers VALUES (9, 'Iris Patel', 'IN', 'iris@example.com', now())")
con.execute("INSERT INTO iceberg_customers VALUES (10, 'Jack Müller', 'DE', 'jack@example.com', now())")
```

**Exercise 4.2 — List snapshots**

```python
snapshots = con.execute("""
    SELECT snapshot_id, committed_at, operation
    FROM iceberg_snapshots('s3://silver/customers/')
    ORDER BY committed_at
""").df()
print(snapshots)
```

**Exercise 4.3 — Query a past snapshot**

```python
# Grab the first snapshot ID from the output above
first_snapshot_id = snapshots['snapshot_id'].iloc[0]

# Query the table as it existed at that snapshot
old_state = con.execute(f"""
    SELECT * FROM iceberg_scan(
        's3://silver/customers/',
        snapshot_id = {first_snapshot_id}
    )
""").df()

print(f"Rows at snapshot {first_snapshot_id}: {len(old_state)}")
print(f"Rows now: {con.execute('SELECT COUNT(*) FROM iceberg_customers').fetchone()[0]}")
```

This is how data teams audit pipelines, roll back bad loads, and reproduce historical reports.

---

## Module 5 — Schema Evolution

**Exercise 5.1 — Add a column to a live Iceberg table**

```python
# Add a column — no data rewrite required
con.execute("ALTER TABLE iceberg_customers ADD COLUMN loyalty_tier VARCHAR DEFAULT 'standard'")

# New rows pick it up automatically
con.execute("""
    INSERT INTO iceberg_customers VALUES
    (11, 'Karen Santos', 'BR', 'karen@example.com', now(), 'gold')
""")

# Old rows have the default value
con.execute("SELECT customer_id, name, loyalty_tier FROM iceberg_customers ORDER BY customer_id").show()
```

With plain Parquet you would need to rewrite every file to add a column.

---

## Module 6 — Build the Full Medallion Pipeline

Now wire together all three layers for the fraud dataset.

**Exercise 6.1 — Land raw data in bronze**

```python
# Copy fraud parquet to bronze as-is — no transformation
con.execute("""
    COPY (SELECT * FROM '/workspace/data/raw/fraud_data01.parquet')
    TO 's3://bronze/fraud/fraud_data01.parquet'
    (FORMAT PARQUET)
""")
print("Bronze: raw fraud data landed.")
```

**Exercise 6.2 — Clean and validate into silver**

```python
# Silver: remove nulls, standardize types, add ingestion timestamp
con.execute("""
    CREATE TABLE iceberg_fraud_silver
    USING ICEBERG
    LOCATION 's3://silver/fraud/'
    AS
    SELECT
        *,
        now() AS ingested_at
    FROM 's3://bronze/fraud/fraud_data01.parquet'
    WHERE transaction_amount IS NOT NULL
      AND user_id IS NOT NULL
""")
print("Silver: cleaned fraud data written as Iceberg.")
```

**Exercise 6.3 — Aggregate into gold**

```python
# Gold: business-ready aggregation
con.execute("""
    CREATE TABLE iceberg_fraud_gold
    USING ICEBERG
    LOCATION 's3://gold/fraud_summary/'
    AS
    SELECT
        merchant_category,
        COUNT(*)                                          AS total_transactions,
        SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END)        AS fraud_count,
        ROUND(AVG(transaction_amount), 2)                AS avg_amount,
        ROUND(
            SUM(CASE WHEN is_fraud THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
            2
        )                                                AS fraud_rate_pct
    FROM iceberg_fraud_silver
    GROUP BY merchant_category
    ORDER BY fraud_rate_pct DESC
""")

con.execute("SELECT * FROM iceberg_fraud_gold").show()
print("Gold: fraud summary written as Iceberg.")
```

---

## Module 7 — Explore in Marimo

Open Marimo at **http://localhost:8888** and create a notebook called `lake_explorer.py`.

**Cell 1 — Connect**
```python
import duckdb
import marimo as mo

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL iceberg; LOAD iceberg;")
con.execute("""
    SET s3_endpoint='minio:9000';
    SET s3_access_key_id='minioadmin';
    SET s3_secret_access_key='minioadmin123';
    SET s3_use_ssl=false;
    SET s3_url_style='path';
""")
```

**Cell 2 — Reactive layer selector**
```python
layer = mo.ui.dropdown(
    options=['bronze', 'silver', 'gold'],
    value='gold',
    label='Lake layer'
)
layer
```

**Cell 3 — Browse files in the selected layer**
```python
files = con.execute(f"SELECT * FROM glob('s3://{layer.value}/**')").df()
mo.table(files)
```

**Cell 4 — Query gold fraud summary**
```python
df = con.execute("""
    SELECT * FROM iceberg_scan('s3://gold/fraud_summary/')
    ORDER BY fraud_rate_pct DESC
""").df()

mo.table(df)
```

**Cell 5 — Visualize fraud rate by category**
```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(df['merchant_category'], df['fraud_rate_pct'])
ax.set_xlabel('Fraud Rate %')
ax.set_title('Fraud Rate by Merchant Category (Gold Layer)')
plt.tight_layout()
mo.pyplot(fig)
```

---

## Checkpoint

Before moving on, you should be able to:
- [ ] Explain the difference between a data lake and a data warehouse
- [ ] Create buckets in MinIO and write Parquet files from DuckDB
- [ ] Create an Iceberg table on object storage and insert rows
- [ ] Query a past snapshot using Iceberg time travel
- [ ] Evolve an Iceberg table schema without rewriting data
- [ ] Build a bronze → silver → gold medallion pipeline for a real dataset

## Next Steps
- **`full_stack`** — feed gold-layer Iceberg tables into Grafana dashboards
- **`devops_stack`** — use Terraform to provision MinIO buckets as code
