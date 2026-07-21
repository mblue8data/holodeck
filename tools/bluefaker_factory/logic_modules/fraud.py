import random
from faker import Faker

fake = Faker()

# Fraud Logic

def apply(row):
    country = row.get("Country", "")
    credit_score = row.get("Credit_Score", 700)
    transaction_amount = row.get("Transaction_Amount", 0.0)
    card_type = row.get("Card_Type", "")
    device = row.get("Device", "")

    risky_countries = ["Nigeria", "Russia", "North Korea", "Iran", "Venezuela"]
    is_location_risky = country in risky_countries

    is_suspicious_amount = transaction_amount > 900.0 and credit_score < 500

    suspicious_combos = [
        ("Amex", "Opera"),
        ("Discover", "Internet Explorer"),
        ("MasterCard", "Linux"),
    ]
    is_suspicious_combo = (
        (card_type, next((b for b in ["Opera", "Internet Explorer", "Linux"] if b in device), ""))
        in suspicious_combos
    )

    row["Fraudulent"] = (
        is_location_risky
        or is_suspicious_amount
        or is_suspicious_combo
        or (fake.pybool() and random.random() < 0.03)
    )

    return row
