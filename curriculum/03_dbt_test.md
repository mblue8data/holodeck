# Curriculum: dbt Output Validation with Grafana

**Sequence:** `dbt_test`
**Level:** Beginner
**Stack:** Postgres · Grafana

## What You Will Learn
- How to validate dbt model output visually
- Building data quality dashboards in Grafana
- Spotting anomalies in modeled data using charts and stats
- The difference between dbt tests (code) and visual validation (human)

## Prerequisites
- Completed `data_modeling` curriculum — dbt models must exist in Postgres

## Start the Stack
```bash
# Run data_modeling first to populate the marts
./holo --load data_modeling
# Then start the validation stack
./holo --load dbt_test
```

---

## Module 1 — Verify dbt Output in SQL

Before building dashboards, confirm the models landed correctly.

```bash
docker exec -it holodeck-postgres-1 psql -U user -d mydb
```

```sql
-- Check row counts in every modeled layer
SELECT 'stg_customers'          AS model, COUNT(*) FROM staging.stg_customers
UNION ALL
SELECT 'stg_transactions',               COUNT(*) FROM staging.stg_transactions
UNION ALL
SELECT 'mart_customer_summary',          COUNT(*) FROM marts.mart_customer_summary;
```

**Exercise 1.1 — Look for nulls in critical columns**
```sql
SELECT
    COUNT(*)                                            AS total_rows,
    COUNT(*) FILTER (WHERE customer_id IS NULL)        AS null_customer_id,
    COUNT(*) FILTER (WHERE total_spent IS NULL)        AS null_total_spent
FROM marts.mart_customer_summary;
```

**Exercise 1.2 — Spot unexpected status values**
```sql
SELECT status, COUNT(*) AS count
FROM staging.stg_transactions
GROUP BY status
ORDER BY count DESC;
```

If you see values outside `completed`, `pending`, `failed` your dbt `accepted_values` test should have caught this — verify tests are passing before trusting the mart.

---

## Module 2 — Data Quality Dashboard in Grafana

Open Grafana at **http://localhost:3000**

Create a new dashboard called **dbt Data Quality**.

**Panel 1 — Row count by model (Stat panels)**

Add three Stat panels side by side:

```sql
-- Panel: stg_customers row count
SELECT COUNT(*) AS value FROM staging.stg_customers;
```
```sql
-- Panel: stg_transactions row count
SELECT COUNT(*) AS value FROM staging.stg_transactions;
```
```sql
-- Panel: mart_customer_summary row count
SELECT COUNT(*) AS value FROM marts.mart_customer_summary;
```

Set thresholds: green above 1, red at 0 — instant alert if a model produces no rows.

**Panel 2 — Transaction status breakdown (Pie chart)**
```sql
SELECT status, COUNT(*) AS count
FROM staging.stg_transactions
GROUP BY status;
```

**Panel 3 — Null check table (Table panel)**
```sql
SELECT
    'mart_customer_summary' AS model,
    COUNT(*) FILTER (WHERE customer_id IS NULL)  AS null_customer_id,
    COUNT(*) FILTER (WHERE name IS NULL)         AS null_name,
    COUNT(*) FILTER (WHERE total_spent IS NULL)  AS null_total_spent
FROM marts.mart_customer_summary;
```

---

## Module 3 — Business Validation

Data quality isn't just about nulls — it's about whether the numbers make business sense.

**Exercise 3.1 — Does customer summary match the source?**
```sql
-- Total spent in the mart should equal total in the source
SELECT
    (SELECT SUM(total_spent) FROM marts.mart_customer_summary)   AS mart_total,
    (SELECT SUM(amount) FROM raw.transactions WHERE status = 'completed') AS source_total;
```

If these differ, there is a transformation bug.

**Panel 4 — Mart vs source reconciliation (Stat with color threshold)**

Add this as a Stat panel. Set:
- Green: both values equal
- Red: any difference

```sql
SELECT
    ROUND(
        ABS(
            (SELECT SUM(total_spent) FROM marts.mart_customer_summary) -
            (SELECT SUM(amount) FROM raw.transactions WHERE status = 'completed')
        ), 2
    ) AS discrepancy;
```
A value of `0.00` means the mart is accurate.

**Exercise 3.2 — Introduce a bug and catch it**

Edit `data_modeling/dbt/models/marts/mart_customer_summary.sql` — change the `WHERE` filter:
```sql
-- Change this
sum(case when t.status = 'completed' then t.amount else 0 end)
-- To this (bug: includes pending too)
sum(case when t.status IN ('completed', 'pending') then t.amount else 0 end)
```

Re-run dbt:
```bash
docker exec -it holodeck-dbt-postgres-1 dbt run --select mart_customer_summary
```

Reload the Grafana dashboard — the discrepancy panel should now show a non-zero value. Fix the model and verify it returns to `0.00`.

---

## Checkpoint

Before moving on, you should be able to:
- [ ] Query all three modeled layers and verify row counts
- [ ] Build a data quality dashboard with null checks and row counts
- [ ] Explain the difference between dbt tests and visual validation
- [ ] Catch a transformation bug using a reconciliation panel

## Next Steps
- **`warehouse_stack`** — add more complex models and validate them here
- **`devops_stack`** — govern schema changes that would break these models
