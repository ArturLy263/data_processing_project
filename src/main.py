import argparse
import random
from pathlib import Path

import numpy as np

from src.models.data_generator import generate_transactions, generate_inventory
from src.processors.analyzer import (
    merge_transactions_inventory,
    add_stockout_risk,
    add_rolling_revenue,
    get_top_performers,
)
from src.validators.data_validator import validate_inventory, validate_transactions


SEED = 42
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")


def main(load_postgres: bool = False):
    random.seed(SEED)
    np.random.seed(SEED)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating data...")
    df_tx = generate_transactions()
    df_inv = generate_inventory(df_tx)

    df_tx.to_csv("data/raw/transactions.csv", index=False)
    df_inv.to_json("data/raw/inventory.json", orient="records", indent=4)
    print(f"Generated {len(df_tx)} transactions, {len(df_inv)} inventory snapshots")

    validate_transactions(df_tx)
    validate_inventory(df_inv)

    df = merge_transactions_inventory(df_tx, df_inv)
    df = add_stockout_risk(df)
    df = add_rolling_revenue(df)

    df.to_csv("data/processed/analysis_output.csv", index=False)
    top = get_top_performers(df)
    top.to_csv("data/processed/top_performers.csv", index=False)
    print("Done. Results saved to data/processed/")

    if load_postgres:
        import psycopg

        from src.load.postgres_loader import get_database_url, load_results

        with psycopg.connect(get_database_url()) as conn:
            load_results(conn, df, top)
        print(f"Loaded {len(df)} rows into sales_analysis and {len(top)} into top_performers")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retail sales and inventory pipeline")
    parser.add_argument(
        "--load-postgres",
        action="store_true",
        help="also load the results into PostgreSQL (DATABASE_URL)",
    )
    main(load_postgres=parser.parse_args().load_postgres)
