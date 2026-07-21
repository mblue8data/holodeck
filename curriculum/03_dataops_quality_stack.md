# Curriculum: DataOps — Quality & Observability

**Sequence:** `dataops_quality_stack`
**Level:** Intermediate
**Stack:** Postgres · dbt-postgres · Soda · Grafana

> This is the *data quality and observability* half of DataOps. The
> *infrastructure and schema* half lives in `dataops_infra_stack`. Real
> DataOps teams own both — load both stacks together to practice the full loop.

## What You Will Learn
- The difference between **dbt tests** (in-model assertions) and **Soda checks** (declarative YAML)
- When to use each: dbt for pipeline-native tests, Soda for cross-project or source-data checks
- Visualizing data quality signals in Grafana dashboards
- The pattern for catching a transformation bug end-to-end

## Prerequisites
- Completed `data_modeling` curriculum — dbt staging and marts models must exist in Postgres
- Comfortable with basic SQL

## Start the Stack
```bash
# Run data_modeling first to populate the modeled layers
./holo --load data_modeling
# Then start the quality stack
./holo --load dataops_quality_stack
```

---

## Module 1 — Verify Modeled Data in SQL

Before writing formal checks, confirm the models landed correctly.

```bash
docker exec -it holodeck-postgres-1 psql -U user -d mydb
```

```sql
-- Row counts in every modeled layer
SELECT 'stg_customers'          AS model, COUNT(*) FROM staging.stg_customers
UNION ALL
SELECT 'stg_transactions',               COUNT(*) FROM staging.stg_transactions
UNION ALL
SELECT 'mart_customer_summary',          COUNT(*) FROM marts.mart_customer_summary;
```

**Exercise 1.1 — Null check on critical columns**
```sql
SELECT
    COUNT(*)                                     AS total_rows,
    COUNT(*) FILTER (WHERE customer_id IS NULL)  AS null_customer_id,
    COUNT(*) FILTER (WHERE total_spent IS NULL)  AS null_total_spent
FROM marts.mart_customer_summary;
```

**Exercise 1.2 — Spot unexpected status values**
```sql
SELECT status, COUNT(*) AS count
FROM staging.stg_transactions
GROUP BY status
ORDER BY count DESC;
```

If you see values outside `completed`, `pending`, `failed` your dbt
`accepted_values` test should have caught this — verify tests are passing
before trusting the mart.

---

## Module 2 — dbt Tests: Assertions Inside the DAG

dbt tests live *inside your project* and run as part of the pipeline. They
are the right choice when the check is tightly coupled to the model.

**Exercise 2.1 — Run the existing dbt tests**
```bash
docker exec -it holodeck-dbt-postgres-1 dbt test
```

Read the output: each test compiles to a SELECT and *fails* if it returns
any rows. That's the fundamental dbt test contract.

**Exercise 2.2 — Add a `unique` test**

Edit `data_modeling/dbt/models/staging/sources.yml` (or the schema file for
`stg_customers`) and add:
```yaml
models:
  - name: stg_customers
    columns:
      - name: id
        tests:
          - unique
          - not_null
```
Re-run: `dbt test --select stg_customers`. Both should pass.

**Exercise 2.3 — Add a custom SQL test**

Create `data_modeling/dbt/tests/assert_positive_amounts.sql`:
```sql
SELECT * FROM {{ ref('stg_transactions') }} WHERE amount < 0
```
Run `dbt test`. Because we seeded no negative amounts, this passes.

**Takeaway:** dbt tests are *code that runs against your models* — they
version with the project, gate deploys, and are the correct tool for
"is my transformation correct."

---

## Module 3 — Soda Checks: Declarative Data Quality

Soda checks live in `soda/checks.yml` — separate from your pipeline code.
They're the right choice for **source-data quality**, **cross-project checks**,
and **checks that don't belong to any single model**.

Check the pre-built `soda/checks.yml`:
```bash
cat soda/checks.yml
```

You'll see checks for `raw.customers` and `raw.transactions` — the same
data dbt's staging layer reads from. Soda is validating the *upstream*
contract; dbt tests validate the *downstream* transformation.

**Exercise 3.1 — Run a scan**
```bash
docker exec -it soda soda scan -d holodeck -c /soda/configuration.yml /soda/checks.yml
```

Every check passes (green) or fails (red) with a row count and the offending
SQL — you can copy that SQL straight into psql to investigate.

**Exercise 3.2 — Make a check fail**

Insert a bad row:
```bash
docker exec -it holodeck-postgres-1 psql -U user -d mydb -c \
  "INSERT INTO raw.transactions (user_id, amount, currency, status) VALUES (1, -50, 'USD', 'unknown');"
```
Re-run the scan. Two checks should now fail: `min(amount) >= 0` and the
`valid values` check on `status`. Delete the bad row and re-scan:
```bash
docker exec -it holodeck-postgres-1 psql -U user -d mydb -c \
  "DELETE FROM raw.transactions WHERE status = 'unknown';"
```

**Exercise 3.3 — Write your own check**

Add to `soda/checks.yml`:
```yaml
checks for raw.customers:
  - invalid_count(country) = 0:
      valid values: [US, NG, DE, KR, RU, GB, FR, JP, CA, AU]
```
Re-scan. All seeded rows should pass. Add a row with `country = 'XX'` and
watch it fail.

**When to reach for Soda over dbt tests:**
- You need to check *raw* / source data before it hits your models
- The check spans multiple projects or teams
- You want data quality without adding a dbt dependency
- You want checks that can be authored by non-dbt users (analysts, DQ engineers)

---

## Module 4 — Visualize Quality in Grafana

Open Grafana at **http://localhost:3001** and create a new dashboard called
**Data Quality**.

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
Set thresholds: green above 1, red at 0 — instant alert if a model produces
no rows.

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

## Module 5 — Business Reconciliation

Data quality isn't just nulls — it's whether the numbers make business sense.

**Exercise 5.1 — Mart vs source reconciliation**
```sql
SELECT
    (SELECT SUM(total_spent) FROM marts.mart_customer_summary)           AS mart_total,
    (SELECT SUM(amount) FROM raw.transactions WHERE status = 'completed') AS source_total;
```
If these differ, there's a transformation bug.

**Panel 4 — Reconciliation stat**

Add a Stat panel:
```sql
SELECT
    ROUND(
        ABS(
            (SELECT SUM(total_spent) FROM marts.mart_customer_summary) -
            (SELECT SUM(amount) FROM raw.transactions WHERE status = 'completed')
        ), 2
    ) AS discrepancy;
```
Set green at 0, red at any non-zero value.

**Exercise 5.2 — Introduce a bug and catch it end-to-end**

Edit `data_modeling/dbt/models/marts/mart_customer_summary.sql` — change:
```sql
-- from
sum(case when t.status = 'completed' then t.amount else 0 end)
-- to (bug: includes pending too)
sum(case when t.status IN ('completed', 'pending') then t.amount else 0 end)
```
Re-run dbt:
```bash
docker exec -it holodeck-dbt-postgres-1 dbt run --select mart_customer_summary
```
Reload the Grafana dashboard — the discrepancy panel now shows a non-zero
value. This is the full DataOps quality loop: code change → deploy → observed
regression. Fix the model and verify it returns to `0.00`.

---

## Checkpoint

Before moving on, you should be able to:
- [ ] Explain the difference between dbt tests and Soda checks, and when to use each
- [ ] Run `dbt test` and interpret the failures
- [ ] Author and run a Soda check against Postgres
- [ ] Build a Grafana data quality dashboard with row counts, null checks, and reconciliation
- [ ] Catch a transformation bug using dashboard + reconciliation panel

## Next Steps
- **`dataops_infra_stack`** — the other half of the DataOps loop: use Terraform + Atlas to *ship* the changes your quality checks protect against. Load it alongside this stack.
- **`warehouse_stack`** — richer models to write more interesting quality checks for
