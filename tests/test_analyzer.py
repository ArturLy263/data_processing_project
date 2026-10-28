import pandas as pd

from src.processors.analyzer import add_rolling_revenue, get_top_performers


def test_rolling_revenue_uses_a_30_day_time_window():
    df = pd.DataFrame(
        {
            "region": ["North"] * 3,
            "item_sku": ["PROD-001"] * 3,
            "transaction_date": pd.to_datetime(["2024-01-01", "2024-01-15", "2024-06-01"]),
            "gross_revenue": [100.0, 300.0, 50.0],
        }
    )
    result = add_rolling_revenue(df)["rolling_30d_avg_revenue"].tolist()
    # Jan 15 averages Jan 1 + Jan 15; Jun 1 has no other sale within 30 days.
    assert result == [100.0, 200.0, 50.0]


def test_top_performers_keeps_region_column():
    df = pd.DataFrame(
        {
            "region": ["North", "North", "South", "South"],
            "item_sku": ["A", "B", "A", "B"],
            "gross_revenue": [10.0, 90.0, 80.0, 20.0],
        }
    )
    top = get_top_performers(df, quantile=0.9)
    assert "region" in top.columns
    assert set(zip(top["region"], top["item_sku"])) == {("North", "B"), ("South", "A")}
