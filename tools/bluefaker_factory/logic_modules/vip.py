def apply(row):
    row["VIP_Customer"] = (
        row.get("Annual_Income", 0) > 150000 and
        row.get("Last_Purchase_Amount", 0.0) > 800.0 and
        row.get("Subscription_Level") in ["Premium", "Enterprise"]
    )
    return row
