from faker import Faker
fake = Faker()

def apply(row):
    row["At_Risk_Flag"] = (
        row.get("Num_Sessions", 0) > 80 and
        row.get("Annual_Income", 0) < 50000 and
        row.get("Credit_Score", 999) < 550
    )
    return row