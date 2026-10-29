import pandas as pd
import psycopg
import pytest

from src.load.postgres_loader import get_database_url, load_results, revenue_by_region
from src.processors.analyzer import (
    add_rolling_revenue,
    add_stockout_risk,
    get_top_performers,
    merge_transactions_inventory,
)


@pytest.fixture
def results():
    tx = pd.DataFrame(
        {
            "transaction_id": [1, 2, 3],
            "item_sku": ["A", "A", "B"],
            "region": ["North", "North", "South"],
            "transaction_date": ["2024-01-05", "2024-01-20", "2024-01-20"],
            "unit_price": [10.0, 10.0, 5.5],
            "units_sold": [2, 30, 4],
        }
    )
    inv = pd.DataFrame(
        {
            "item_sku": ["A", "B"],
            "snapshot_date": ["2024-01-01", "2024-01-25"],
            "current_stock": [100, 999],
            "warehouse_id": ["W1", "W2"],
        }
    )
    analysis = add_rolling_revenue(add_stockout_risk(merge_transactions_inventory(tx, inv)))
    return analysis, get_top_performers(analysis, quantile=0.5)


def count(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def test_load_writes_both_tables(pg_conn, results):
    analysis, top = results
    load_results(pg_conn, analysis, top)

    assert count(pg_conn, "sales_analysis") == 3
    assert count(pg_conn, "top_performers") == len(top)
    row = pg_conn.execute(
        "SELECT transaction_date::text, gross_revenue::text, current_stock, snapshot_date, stockout_risk "
        "FROM sales_analysis WHERE transaction_id = 3"
    ).fetchone()
    # B's only snapshot is after the sale, so stock and snapshot date are NULL.
    assert row == ("2024-01-20", "22.00", None, None, False)


def test_load_is_idempotent(pg_conn, results):
    analysis, top = results
    load_results(pg_conn, analysis, top)
    load_results(pg_conn, analysis, top)
    assert count(pg_conn, "sales_analysis") == 3


def test_failed_load_keeps_previous_results(pg_conn, results):
    analysis, top = results
    load_results(pg_conn, analysis, top)

    broken = analysis.copy()
    broken.loc[0, "units_sold"] = -1  # violates the CHECK constraint
    with pytest.raises(psycopg.errors.CheckViolation):
        load_results(pg_conn, broken, top)

    assert count(pg_conn, "sales_analysis") == 3
    assert pg_conn.execute("SELECT MIN(units_sold) FROM sales_analysis").fetchone()[0] == 2


def test_revenue_by_region_query(pg_conn, results):
    analysis, top = results
    load_results(pg_conn, analysis, top)
    rows = [(r, n, str(rev), risks) for r, n, rev, risks in revenue_by_region(pg_conn)]
    # 30 units against a stock of 100 is above the 5 % threshold.
    assert rows == [("North", 2, "320.00", 1), ("South", 1, "22.00", 0)]


def test_missing_database_url_has_clear_error(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="DATABASE_URL is not set"):
        get_database_url()
