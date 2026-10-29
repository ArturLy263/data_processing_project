import pandas as pd

from src.main import main
from src.processors.analyzer import add_stockout_risk, merge_transactions_inventory


def test_merge_uses_latest_earlier_snapshot_of_the_same_sku():
    tx = pd.DataFrame(
        {
            "item_sku": ["A", "A", "B"],
            "transaction_date": ["2024-01-05", "2024-01-20", "2024-01-20"],
            "unit_price": [10.0, 10.0, 5.0],
            "units_sold": [2, 3, 4],
        }
    )
    inv = pd.DataFrame(
        {
            "item_sku": ["A", "A", "B"],
            "snapshot_date": ["2024-01-01", "2024-01-10", "2024-01-25"],
            "current_stock": [100, 50, 999],
        }
    )
    result = merge_transactions_inventory(tx, inv).sort_values(["item_sku", "transaction_date"])
    assert result["current_stock"].tolist()[:2] == [100, 50]
    assert pd.isna(result["current_stock"].tolist()[2])  # B has no snapshot before its sale
    assert result["gross_revenue"].tolist() == [20.0, 30.0, 20.0]


def test_stockout_risk_threshold_is_5_percent_of_stock():
    df = pd.DataFrame({"units_sold": [5, 6], "current_stock": [100, 100]})
    assert add_stockout_risk(df)["stockout_risk"].tolist() == [False, True]


def test_main_writes_reproducible_outputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    main()
    first = (tmp_path / "data/processed/top_performers.csv").read_bytes()
    analysis = pd.read_csv(tmp_path / "data/processed/analysis_output.csv")
    assert len(analysis) == 5000
    assert analysis["current_stock"].notna().all()
    assert (tmp_path / "data/raw/transactions.csv").exists()
    assert (tmp_path / "data/raw/inventory.json").exists()

    main()
    assert (tmp_path / "data/processed/top_performers.csv").read_bytes() == first
