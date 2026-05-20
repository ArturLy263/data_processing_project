import pandas as pd


def merge_transactions_inventory(
    df_tx: pd.DataFrame, df_inv: pd.DataFrame
) -> pd.DataFrame:
    df_tx = df_tx.copy()
    df_inv = df_inv.copy()
    df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])
    df_inv["snapshot_date"] = pd.to_datetime(df_inv["snapshot_date"])
    df_tx["gross_revenue"] = df_tx["unit_price"] * df_tx["units_sold"]
    df_tx = df_tx.sort_values("transaction_date")
    df_inv = df_inv.sort_values("snapshot_date")
    df_combined = pd.merge_asof(
        df_tx,
        df_inv,
        left_on="transaction_date",
        right_on="snapshot_date",
        by="item_sku",
        direction="backward",
    )
    return df_combined


def add_stockout_risk(df: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
    df = df.copy()
    df["stockout_risk"] = df["units_sold"] > threshold * df["current_stock"]
    return df


def add_rolling_revenue(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    df = df.copy()
    df["30d_avg_revenue"] = df.groupby(["region", "item_sku"])[
        "gross_revenue"
    ].transform(lambda x: x.rolling(window, min_periods=1).mean())
    return df


def get_top_performers(df: pd.DataFrame, quantile: float = 0.9) -> pd.DataFrame:
    revenue_by_item = df.groupby(["region", "item_sku"], as_index=False)[
        "gross_revenue"
    ].sum()

    def top_percent(group):
        threshold = group["gross_revenue"].quantile(quantile)
        return group[group["gross_revenue"] >= threshold]

    return revenue_by_item.groupby("region", group_keys=False).apply(
        top_percent, include_groups=False
    )
