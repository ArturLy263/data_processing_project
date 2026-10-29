"""Load the pipeline's results into PostgreSQL.

Both tables are replaced in a single transaction: a failed load leaves the
previous results in place, and running the load again gives the same rows.
"""

import os

import pandas as pd
import psycopg

SALES_ANALYSIS_COLUMNS = [
    "transaction_id",
    "item_sku",
    "region",
    "transaction_date",
    "unit_price",
    "units_sold",
    "gross_revenue",
    "snapshot_date",
    "current_stock",
    "warehouse_id",
    "stockout_risk",
    "rolling_30d_avg_revenue",
]
TOP_PERFORMERS_COLUMNS = ["region", "item_sku", "gross_revenue"]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sales_analysis (
    transaction_id          INTEGER PRIMARY KEY,
    item_sku                TEXT NOT NULL,
    region                  TEXT NOT NULL,
    transaction_date        DATE NOT NULL,
    unit_price              NUMERIC(10, 2) NOT NULL CHECK (unit_price > 0),
    units_sold              INTEGER NOT NULL CHECK (units_sold > 0),
    gross_revenue           NUMERIC(14, 2) NOT NULL,
    snapshot_date           DATE,
    current_stock           INTEGER CHECK (current_stock >= 0),
    warehouse_id            TEXT,
    stockout_risk           BOOLEAN NOT NULL,
    rolling_30d_avg_revenue DOUBLE PRECISION NOT NULL
);

CREATE TABLE IF NOT EXISTS top_performers (
    region        TEXT NOT NULL,
    item_sku      TEXT NOT NULL,
    gross_revenue NUMERIC(14, 2) NOT NULL,
    PRIMARY KEY (region, item_sku)
);
"""


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set, e.g. "
            "postgresql://retail:retail@localhost:5435/retail"
        )
    return url


def _rows(df: pd.DataFrame, columns: list[str]):
    # Python objects with None for missing values, which psycopg can adapt.
    values = df[columns].astype(object)
    return values.where(df[columns].notna(), None).itertuples(index=False, name=None)


def _copy(cursor: psycopg.Cursor, table: str, df: pd.DataFrame, columns: list[str]) -> None:
    with cursor.copy(f"COPY {table} ({', '.join(columns)}) FROM STDIN") as copy:
        for row in _rows(df, columns):
            copy.write_row(row)


def load_results(conn: psycopg.Connection, analysis: pd.DataFrame, top: pd.DataFrame) -> None:
    """Create the tables if needed and replace their contents atomically."""
    # A sale without an earlier snapshot has no stock, which makes the column
    # float in pandas; nullable Int64 keeps it an integer for PostgreSQL.
    analysis = analysis.assign(current_stock=analysis["current_stock"].astype("Int64"))
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute("TRUNCATE sales_analysis, top_performers")
            _copy(cur, "sales_analysis", analysis, SALES_ANALYSIS_COLUMNS)
            _copy(cur, "top_performers", top, TOP_PERFORMERS_COLUMNS)


def revenue_by_region(conn: psycopg.Connection) -> list[tuple]:
    """Example query over the loaded data: transactions, revenue and stock-out risks per region."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT region,
                   COUNT(*)                                AS transactions,
                   SUM(gross_revenue)                      AS gross_revenue,
                   COUNT(*) FILTER (WHERE stockout_risk)   AS stockout_risks
            FROM sales_analysis
            GROUP BY region
            ORDER BY region
            """
        )
        return cur.fetchall()
