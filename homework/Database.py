import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta

NUM_RECORDS = 5000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)
SKUS = [f'PROD-{i:03}' for i in range(100)]
WAREHOUSE = ['A', 'B', 'C']
REGIONS = ['North', 'Central', 'South']

def generate_transactions(num_records):
    time_delta =END_DATE -START_DATE
    random_dates = [
        START_DATE + timedelta (days=random.randint(0, time_delta.days))
        for _ in range(num_records)
    ]

    data = {
        'transaction_id': range(10000, 10000 + num_records),
        'item_sku': np.random.choice(SKUS, size=num_records),
        'region': np.random.choice(REGIONS, size=num_records),
        'transaction_date': random_dates,
        'unit_price': np.round(np.random.uniform(10.0, 500.0, num_records), 2),
        'units_sold': np.random.randint(1, 101, num_records),
    }

    df = pd.DataFrame(data)
    df.sort_values(by='transaction_date', inplace=True)
    return df

def generate_inventory(df_transactions):
    sku_min_max_dates = df_transactions.groupby('item_sku')['transaction_date'].agg(['min', 'max']).reset_index()

    inventory_data = []

    for sku in SKUS:
        sku_info = sku_min_max_dates[sku_min_max_dates['item_sku'] == sku]
        if sku_info.empty:
            continue

        min_date = sku_info['min'].iloc[0]
        max_date = sku_info['max'].iloc[0]
        num_snapshots = random.randint(5, 15)
        date_range = pd.date_range(start=min_date, end=max_date, periods= num_snapshots)

        for date in date_range:
            snapshot_date = date - timedelta(days=random.randint(1, 10))
            inventory_data.append({
            'item_sku': sku,
            'snapshot_date': snapshot_date.date().isoformat(),
            'current_stock': random.randint(100, 5000),
            'warehouse_id': random.choice(WAREHOUSE)
        })

    df = pd.DataFrame(inventory_data)
    df.sort_values(by='snapshot_date', inplace=True)
    return df

df_tx = generate_transactions(NUM_RECORDS)
df_tx.to_csv('transactions_core.csv', index=False)
print(f"Generated {len(df_tx)} records in 'transactions_core.csv'")

df_inv = generate_inventory(df_tx)
df_inv['snapshot_date'] = df_inv['snapshot_date'].astype(str)
df_inv.to_json('inventory_updates.json', orient='records', indent=4)
print(f'Generated {len(df_inv)} records in inventory_updates.json')

df_tx['transaction_date'] = pd.to_datetime(df_tx['transaction_date'])
df_inv['snapshot_date'] = pd.to_datetime(df_inv['snapshot_date'])
df_tx['gross_revenue'] = df_tx['unit_price'] * df_tx['units_sold']
df_tx = df_tx.sort_values('transaction_date')
df_inv = df_inv.sort_values('snapshot_date')
df_combined = pd.merge_asof(
    df_tx,
    df_inv,
    left_on='transaction_date',
    right_on='snapshot_date',
    by='item_sku',
    direction='backward'
)

df_combined['stockout_risk'] =(
    df_combined['units_sold'] > 0.05 * df_combined['current_stock']
)

df_combined = df_combined.sort_values('transaction_date')

df_combined = df_combined.sort_values('transaction_date')

df_combined['30d_avg_revenue'] = (
    df_combined
    .groupby(['region', 'item_sku'])['gross_revenue']
    .transform(lambda x: x.rolling(30, min_periods=1).mean())
)

revenue_by_item = (
    df_combined
    .groupby(['region', 'item_sku'], as_index=False)['gross_revenue']
    .sum()
)

def top_10_percent(df):
    threshold = df['gross_revenue'].quantile(0.9)
    return df[df['gross_revenue'] >= threshold]

top_performers = (
    revenue_by_item
    .groupby('region', group_keys=False)
    .apply(top_10_percent, include_groups=False)
)

top_performers.to_csv('top_performers_analysis.csv', index=False)

df_combined.to_csv('analysis_output.csv', index=False)
