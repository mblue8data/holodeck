from dagster import asset, Definitions, ScheduleDefinition, define_asset_job

@asset
def raw_customers():
    """Placeholder asset representing the raw customers table in Postgres."""
    return {"status": "available"}

@asset
def raw_transactions():
    """Placeholder asset representing the raw transactions table in Postgres."""
    return {"status": "available"}

@asset(deps=[raw_customers, raw_transactions])
def customer_summary():
    """Aggregates customers and transactions into a summary mart."""
    return {"status": "ready"}

daily_job = define_asset_job("daily_pipeline", selection="*")

daily_schedule = ScheduleDefinition(
    job=daily_job,
    cron_schedule="0 6 * * *",
)

defs = Definitions(
    assets=[raw_customers, raw_transactions, customer_summary],
    schedules=[daily_schedule],
)
