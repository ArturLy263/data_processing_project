# Retail Sales & Inventory Processing (pandas)

[![CI](https://github.com/ArturLy263/data_processing_project/actions/workflows/ci.yml/badge.svg)](https://github.com/ArturLy263/data_processing_project/actions/workflows/ci.yml)

A small pandas pipeline on **synthetic** retail data. It generates sales transactions and inventory
snapshots, joins each sale to the latest earlier stock snapshot of the same SKU (`merge_asof`),
flags stock-out risk, computes a 30-day rolling average of revenue per region and SKU, and selects
the top 10 % of SKUs by revenue in each region.

Before processing, the input is validated: required columns present, no nulls, unique
`transaction_id`, positive `unit_price` and `units_sold`, non-negative `current_stock`. Invalid data
stops the run with a `DataValidationError` that names the rule and the columns.

The data is generated with fixed random seeds, so every run produces the same output. This is a
learning project on synthetic data, not a production pipeline.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt     # requirements.txt alone is enough to run the pipeline

python -m src.main                      # creates data/raw/ and data/processed/
python -m pytest tests -q
```

Tested with Python 3.12 and 3.14.

To check a run: `data/processed/analysis_output.csv` has 5,000 rows plus a header and
`data/processed/top_performers.csv` 30 rows plus a header; the first rows of `top_performers.csv`
are shown below. Running the pipeline again produces identical files.

## Pipeline

```mermaid
flowchart LR
    G[data_generator.py<br/>5,000 transactions<br/>inventory snapshots] --> R[(data/raw/<br/>CSV + JSON)]
    G --> V[data_validator.py<br/>columns, nulls, values]
    V --> J[merge_asof<br/>sale ↔ latest snapshot]
    J --> S[stock-out risk flag]
    S --> W[30-day rolling revenue<br/>per region and SKU]
    W --> O[(analysis_output.csv)]
    W --> T[top 10 % SKUs per region]
    T --> P[(top_performers.csv)]
```

| Step | Function | Rule |
| --- | --- | --- |
| Validation | `validate_transactions`, `validate_inventory` | see above; raises `DataValidationError` |
| As-of join | `merge_transactions_inventory` | each sale gets the most recent stock snapshot on or before its date |
| Stock-out risk | `add_stockout_risk` | units sold > 5 % of current stock |
| Rolling revenue | `add_rolling_revenue` | mean revenue over the trailing 30 days, per region and SKU |
| Top performers | `get_top_performers` | SKUs at or above the 90th revenue percentile of their region |

## Outputs

- `data/processed/analysis_output.csv` — one row per transaction with stock level, `stockout_risk`
  and `rolling_30d_avg_revenue`
- `data/processed/top_performers.csv` — `region, item_sku, gross_revenue`

First rows of `top_performers.csv`:

```text
region,item_sku,gross_revenue
Central,PROD-009,326489.44
Central,PROD-033,321532.68
Central,PROD-034,315704.64
```

## Structure

```text
src/
├── main.py                     # runs the pipeline
├── models/data_generator.py    # synthetic transactions and inventory
├── processors/analyzer.py      # join, flags, rolling revenue, top performers
└── validators/data_validator.py # input checks
tests/
```

## Tests

- `test_analyzer.py`: the 30-day rolling window and that top performers keep their region
- `test_pipeline.py`: the as-of join picks the latest earlier snapshot of the same SKU (and leaves
  stock empty when there is none), the 5 % stock-out threshold, and a full run of `main()` in a
  temporary directory that writes all files and produces identical output twice
- `test_data_validator.py`: each validation rule

GitHub Actions runs the tests and then the pipeline itself on a fresh checkout.
