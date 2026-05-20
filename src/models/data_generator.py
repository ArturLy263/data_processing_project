import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

NUM_RECORDS = 5000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)
SKUS = [f'PROD-{i:03}' for i in range(100)]
WAREHOUSES = ['A', 'B', 'C']
REGIONS = ['North', 'Central', 'South']


def generate_transactions(num_records: int = NUM_RECORDS) -> pd.DataFrame:
    time_delta = END_DATE - START_DATE
    random_dates = [
        START_DATE + timedelta(days=random.randint(0, time_delta.days))
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


def generate_inventory(df_transactions: pd.DataFrame) -> pd.DataFrame:
    sku_dates = (
        df_transactions
        .groupby('item_sku')['transaction_date']
        .agg(['min', 'max'])
        .reset_index()
    )
    inventory_data = []
    for sku in SKUS:
        sku_info = sku_dates[sku_dates['item_sku'] == sku]
        if sku_info.empty:
            continue
        min_date = sku_info['min'].iloc[0]
        max_date = sku_info['max'].iloc[0]
        num_snapshots = random.randint(5, 15)
        date_range = pd.date_range(start=min_date, end=max_date, periods=num_snapshots)
        for date in date_range:
            snapshot_date = date - timedelta(days=random.randint(1, 10))
            inventory_data.append({
                'item_sku': sku,
                'snapshot_date': snapshot_date.date().isoformat(),
                'current_stock': random.randint(100, 5000),
                'warehouse_id': random.choice(WAREHOUSES),
            })
    df = pd.DataFrame(inventory_data)
    df.sort_values(by='snapshot_date', inplace=True)
    return df