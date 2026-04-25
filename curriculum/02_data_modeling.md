# Curriculum: Data Modeling with dbt

**Sequence:** `data_modeling`
**Level:** Intermediate
**Stack:** Postgres · dbt-postgres

## What You Will Learn
- How dbt projects are structured
- Running, testing, and documenting dbt models
- The difference between sources, staging models, and mart models
- Writing dbt tests and reading test output
- Generating and navigating dbt docs

## Prerequisites
- Completed `warehouse_stack` curriculum or familiar with SQL and warehouse layers
- Understanding of SELECT, JOIN, GROUP BY

## Start the Stack
```bash
./holo --load data_modeling
```

---

## Module 1 — dbt Project Structure

The dbt project lives in `data_modeling/dbt/`. Take a few minutes to read through the files:

```
data_modeling/dbt/
├── dbt_project.yml       # Project name, model paths, materialization defaults
├── profiles.yml          # Database connection (points to local Postgres)
└── models/
    ├── staging/
    │   ├── sources.yml           # Declares raw tables as dbt sources
    │   ├── stg_customers.sql     # Staging model: cleans raw.customers
    │   └── stg_transactions.sql  # Staging model: cleans raw.transactions
    └── marts/
        └── mart_customer_summary.sql  # Mart: aggregates customers + transactions
```

**Key concepts:**
- **Sources** — raw tables dbt reads from but does not own
- **Models** — SQL SELECT statements that dbt materializes as views or tables
- **refs** — `{{ ref('model_name') }}` links models together, building the DAG
- **Materializations** — staging defaults to `view`, marts default to `table`

---

## Module 2 — Run Your First dbt Build

```bash
docker exec -it holodeck-dbt-postgres-1 dbt run
```

Read the output carefully:
- Each model shows as `CREATE VIEW` or `CREATE TABLE`
- Green = success, Red = failure
- The order respects the dependency graph

**Exercise 2.1 — Verify in Postgres**
```bash
docker exec -it holodeck-postgres-1 psql -U user -d mydb
```
```sql
\dt staging.*
\dt marts.*
SELECT * FROM marts.mart_customer_summary;
```

**Exercise 2.2 — Run a single model**
```bash
docker exec -it holodeck-dbt-postgres-1 dbt run --select stg_customers
```

**Exercise 2.3 — Run with dependencies**
```bash
# Run mart_customer_summary and everything upstream of it
docker exec -it holodeck-dbt-postgres-1 dbt run --select +mart_customer_summary
```

---

## Module 3 — Add a New Staging Model

**Exercise 3.1 — Create `stg_completed_transactions.sql`**

Create `data_modeling/dbt/models/staging/stg_completed_transactions.sql`:
```sql
select
    transaction_id,
    customer_id,
    amount,
    currency,
    created_at
from {{ ref('stg_transactions') }}
where status = 'completed'
```

Run it:
```bash
docker exec -it holodeck-dbt-postgres-1 dbt run --select stg_completed_transactions
```

**Exercise 3.2 — Change a materialization**

Open `dbt_project.yml` and change staging to materialize as tables instead of views:
```yaml
staging:
  +materialized: table
```

Run `dbt run` and check in Postgres whether staging objects changed from views to tables.
Change it back — views are cheaper for staging.

---

## Module 4 — Write dbt Tests

dbt has two types of tests:
- **Generic** — built-in checks (`not_null`, `unique`, `accepted_values`, `relationships`)
- **Singular** — custom SQL that returns rows when something is wrong

**Exercise 4.1 — Add generic tests**

Create `data_modeling/dbt/models/staging/schema.yml`:
```yaml
version: 2

models:
  - name: stg_customers
    columns:
      - name: customer_id
        tests:
          - unique
          - not_null
      - name: email
        tests:
          - not_null

  - name: stg_transactions
    columns:
      - name: transaction_id
        tests:
          - unique
          - not_null
      - name: status
        tests:
          - accepted_values:
              values: ['completed', 'pending', 'failed']
      - name: customer_id
        tests:
          - relationships:
              to: ref('stg_customers')
              field: customer_id
```

Run the tests:
```bash
docker exec -it holodeck-dbt-postgres-1 dbt test
```

**Exercise 4.2 — Write a singular test**

Create `data_modeling/dbt/tests/assert_no_negative_amounts.sql`:
```sql
-- This test fails if any completed transaction has a negative amount
select *
from {{ ref('stg_transactions') }}
where status = 'completed'
  and amount < 0
```

```bash
docker exec -it holodeck-dbt-postgres-1 dbt test --select assert_no_negative_amounts
```

**Exercise 4.3 — Break a test on purpose**

Insert a bad row in Postgres and re-run tests to see a failure:
```sql
INSERT INTO raw.transactions (user_id, amount, currency, status)
VALUES (1, -99.00, 'USD', 'completed');
```
```bash
docker exec -it holodeck-dbt-postgres-1 dbt test --select assert_no_negative_amounts
```
Observe the failure output, then delete the bad row and confirm tests pass again.

---

## Module 5 — Build a New Mart

**Exercise 5.1 — Create `mart_revenue_by_country.sql`**

Create `data_modeling/dbt/models/marts/mart_revenue_by_country.sql`:
```sql
with customers as (
    select * from {{ ref('stg_customers') }}
),
transactions as (
    select * from {{ ref('stg_completed_transactions') }}
),
joined as (
    select
        c.country,
        count(t.transaction_id)  as transaction_count,
        sum(t.amount)            as total_revenue,
        avg(t.amount)            as avg_transaction_value
    from customers c
    inner join transactions t on c.customer_id = t.customer_id
    group by c.country
)
select * from joined
order by total_revenue desc
```

```bash
docker exec -it holodeck-dbt-postgres-1 dbt run --select mart_revenue_by_country
```

**Exercise 5.2 — Add a description and tests for the new mart**

Add to `schema.yml` (or create `data_modeling/dbt/models/marts/schema.yml`):
```yaml
version: 2

models:
  - name: mart_revenue_by_country
    description: "Total revenue and transaction counts aggregated by customer country."
    columns:
      - name: country
        tests:
          - unique
          - not_null
      - name: total_revenue
        tests:
          - not_null
```

---

## Module 6 — dbt Docs

**Exercise 6.1 — Generate and serve docs**
```bash
docker exec -it holodeck-dbt-postgres-1 dbt docs generate
docker exec -it holodeck-dbt-postgres-1 dbt docs serve --port 8080 --host 0.0.0.0
```

Open **http://localhost:8080** and explore:
- The DAG view — see how models depend on each other
- Click a model to read its description and column definitions
- Navigate from a mart back to its source tables

**Exercise 6.2 — Add descriptions to models**

Edit `stg_customers.sql` to add a config block at the top:
```sql
{{ config(description="Cleaned and renamed customer records from the raw layer.") }}

select ...
```

Regenerate docs and see the description appear.

---

## Checkpoint

Before moving on, you should be able to:
- [ ] Explain the difference between a source, a staging model, and a mart
- [ ] Run `dbt run`, `dbt test`, and `dbt docs generate`
- [ ] Add a new model and wire it into the DAG with `{{ ref() }}`
- [ ] Write both generic and singular tests
- [ ] Read the dbt DAG in the docs UI

## Next Steps
- **`dbt_test`** — validate dbt output visually in Grafana
- **`devops_stack`** — manage the underlying schema changes with Atlas
