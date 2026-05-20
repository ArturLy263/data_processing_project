import csv
import json
import random
from datetime import datetime, timedelta
import pandas as pd

TRANSACTION_USER_ID = [f'PROD-{i:03}' for i in range(10000, 11000)]
PRODUCT_CATEGORY = ['Apparel', 'Electronics', 'Groceries']

def generate_transaction(transaction_id):
    return {
        "transaction_id": transaction_id,
        "user_id": random.choice(TRANSACTION_USER_ID),
        "product_category": random.choice(PRODUCT_CATEGORY),
        "amount": round(random.uniform(100.0, 1000.0), 2),
        "timestamp": datetime.now().isoformat(),
    }

def write_transaction_to_csv(filename, num_transactions):
    with open(filename, mode= 'w', newline= '') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ['transaction_id', 'user_id', 'product_category', 'amount', 'timestamp']
        )

        for i in range(1, num_transactions + 1):
            tx = generate_transaction(i)
            writer.writerow([
                tx["transaction_id"],
                tx["user_id"],
                tx["product_category"],
                tx["amount"],
                tx["timestamp"]
            ])

write_transaction_to_csv('transactions.csv', 100)

PROFILE_USER_ID = list(range(10000, 11000))
COUNTRY = ['USA', 'UK', 'SPAIN']
START_DATE = datetime(2015, 1,1)
END_DATE = datetime(2020,12, 23)
delta = END_DATE - START_DATE
delta = delta.days

def generate_user_profile(user_id):
    random_days = random.randint(0, (END_DATE - START_DATE).days)
    registration_date = START_DATE + timedelta(days=random_days)

    return{
        "user_id": user_id,
        "country": random.choice(COUNTRY),
        "registration_date": registration_date.date().isoformat(),
        "is_premium": random.choice([True, False])
    }

def generate_user_profiles(num_profiles):
    profiles = []
    for i in range(num_profiles):
        user_id = PROFILE_USER_ID[i]
        profile = generate_user_profile(user_id)
        profiles.append(profile)

    return profiles

def build_user_profiles_json(num_profiles):
    profiles = generate_user_profiles(num_profiles)
    with open('../user_profiles.json', 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=4)

build_user_profiles_json(100)

EVENT_TYPE = ['VIEW', 'COMMENT', 'BOUGHT', 'RESERVED']
LOG_USER_ID = [f'USER-{i}' for i in range(10000, 11000)]

def generate_log_entry(log_id):
    if random.random() < 0.08:
        user_id = None
    else:
        user_id = random.choice(LOG_USER_ID)

    return {
        "log_id": log_id,
        "user_id": user_id,
        "event_type": random.choice(EVENT_TYPE),
        "latency_ms": random.randint(50, 500),
        "timestamp": datetime.now().isoformat()
    }

def write_log_to_csv(filename, num_logs):
    with open(filename, mode= 'w', newline= '', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            ['log_id', 'user_id', 'event_type', 'latency_ms', 'timestamp']
        )
        for log_id in range(1, num_logs + 1):
            log = generate_log_entry(log_id)
            writer.writerow(log.values())

write_log_to_csv('log_entries.csv', 100)

class SelfFileWriter:
    def __init__(self, filename, mode='w'):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        print(f"[{self.filename}]: Attempting to open file in '{self.mode}' mode")
        self.file = open(self.filename, self.mode)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

def build_transactions_csv():
    lines = []
    lines.append("transaction_id,user_id,product_category,amount,timestamp")

    for i in range(1, 101):
        lines.append(
            f"{i},USER-{i},Electronics,199.99,2025-01-01T10:00:00"
        )

    return "\n".join(lines)

def build_user_profiles_json():
    profiles = []

    for i in range(100):
        profiles.append({
            "user_id": f"USER-{i}",
            "country": random.choice(['USA', 'UK', 'SPAIN']),
            "registration_date": "2019-01-01",
            "is_premium": random.choice([True, False])
        })

    return profiles

def build_log_entries_csv():
    lines = []
    lines.append("log_id,user_id,event_type,latency_ms,timestamp")

    for i in range(1, 101):
        lines.append(
            f"{i},USER-{i},VIEW,100,2025-01-01T10:00:00"
        )

    return "\n".join(lines)

csv_content = build_transactions_csv()

with SelfFileWriter("transactions.csv") as f:
    f.write(csv_content)

with SelfFileWriter("log_entries.csv") as f:
    f.write(build_log_entries_csv())


df_users = pd.read_json("../user_profiles.json")
df_trans = pd.read_csv("transactions.csv")
df_logs = pd.read_csv("log_entries.csv")

df_users["user_id"] = df_users["user_id"].apply(lambda x: f"USER-{x - 10000}")

df_logs = df_logs.dropna(subset=['user_id'])

df_revenue = (
    df_trans.groupby("user_id")
    .agg(
        total_revenue=("amount", "sum"),
        num_transactions=("transaction_id", "count"),
    )
    .reset_index()
)

df_engagement = (
    df_logs.groupby("user_id")
    .agg(
        total_events=("log_id", "count"),
        avg_latency_ms= ("latency_ms", "mean")
    )
    .reset_index()
)

df_final = df_users.merge(
    df_revenue,
    on = "user_id",
    how = "left",
)

df_final = df_final.merge(
    df_engagement,
    on = "user_id",
    how = "left",
)

df_final["avg_transaction_value"] = df_final["total_revenue"] / df_final["num_transactions"]

metric_cols = [
    "total_revenue",
    "num_transactions",
    "total_events",
    "avg_latency_ms",
    "avg_transaction_value",
]

df_final[metric_cols] = df_final[metric_cols].fillna(0)

with SelfFileWriter("final_summary.csv") as f:
    df_final.to_csv(f, index=False)