import pandas as pd

TRANSACTION_COLUMNS = [
    "transaction_id",
    "item_sku",
    "region",
    "transaction_date",
    "unit_price",
    "units_sold",
]
INVENTORY_COLUMNS = ["item_sku", "snapshot_date", "current_stock", "warehouse_id"]


class DataValidationError(ValueError):
    """Raised when input data breaks a rule the pipeline relies on."""


def _check_columns_and_nulls(df: pd.DataFrame, columns: list[str], name: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise DataValidationError(f"{name}: missing columns {missing}")
    nulls = {c: int(n) for c, n in df[columns].isna().sum().items() if n}
    if nulls:
        raise DataValidationError(f"{name}: null values {nulls}")


def validate_transactions(df: pd.DataFrame) -> None:
    _check_columns_and_nulls(df, TRANSACTION_COLUMNS, "transactions")
    if df["transaction_id"].duplicated().any():
        raise DataValidationError("transactions: duplicate transaction_id values")
    if (df["unit_price"] <= 0).any():
        raise DataValidationError("transactions: unit_price must be positive")
    if (df["units_sold"] <= 0).any():
        raise DataValidationError("transactions: units_sold must be positive")


def validate_inventory(df: pd.DataFrame) -> None:
    _check_columns_and_nulls(df, INVENTORY_COLUMNS, "inventory")
    if (df["current_stock"] < 0).any():
        raise DataValidationError("inventory: current_stock cannot be negative")
