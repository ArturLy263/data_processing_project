import pandas as pd
import pytest

from src.validators.data_validator import (
    DataValidationError,
    validate_inventory,
    validate_transactions,
)


def transactions(**overrides):
    data = {
        "transaction_id": [1, 2],
        "item_sku": ["PROD-001", "PROD-002"],
        "region": ["North", "South"],
        "transaction_date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "unit_price": [10.0, 20.0],
        "units_sold": [1, 2],
    }
    data.update(overrides)
    return pd.DataFrame(data)


def inventory(**overrides):
    data = {
        "item_sku": ["PROD-001"],
        "snapshot_date": ["2023-12-31"],
        "current_stock": [100],
        "warehouse_id": ["A"],
    }
    data.update(overrides)
    return pd.DataFrame(data)


def test_valid_data_passes():
    validate_transactions(transactions())
    validate_inventory(inventory())


@pytest.mark.parametrize(
    "overrides, message",
    [
        ({"transaction_id": [1, 1]}, "duplicate transaction_id"),
        ({"unit_price": [10.0, 0.0]}, "unit_price must be positive"),
        ({"units_sold": [1, -3]}, "units_sold must be positive"),
        ({"region": ["North", None]}, "null values {'region': 1}"),
    ],
)
def test_invalid_transactions_are_rejected(overrides, message):
    with pytest.raises(DataValidationError, match=message):
        validate_transactions(transactions(**overrides))


def test_missing_column_is_reported():
    with pytest.raises(DataValidationError, match=r"missing columns \['units_sold'\]"):
        validate_transactions(transactions().drop(columns="units_sold"))


def test_negative_stock_is_rejected():
    with pytest.raises(DataValidationError, match="current_stock cannot be negative"):
        validate_inventory(inventory(current_stock=[-1]))
