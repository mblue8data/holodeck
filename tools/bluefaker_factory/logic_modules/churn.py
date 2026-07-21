from faker import Faker
fake = Faker()

# Logic for Churn
def apply(row):
    subscription = row.get("Subscription_Level")
    sessions = row.get("Num_Sessions", 100)
    pages = row.get("Pages_Visited", 0)
    credit_score = row.get("Credit_Score", 999)
    income = row.get("Annual_Income", 0)

    if subscription == "Free" and sessions < 10:
        row["Churned"] = True
    elif subscription == "Enterprise" and pages > 40:
        row["Churned"] = False
    elif credit_score < 450 and income < 40000:
        row["Churned"] = True
    else:
        row["Churned"] = fake.pybool()

    return row 

