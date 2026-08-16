"""
load_to_sqlite.py — Bluestock Mutual Fund Capstone

Builds data/processed/bluestock_mf.db from the cleaned CSVs, applying the
schema in sql/schema.sql. The database file is deleted and rebuilt from
scratch on every run, so this script is safe to re-run at any time without
duplicating rows (the original version used if_exists="append", which
would double every table's row count on a second run).

Known data-quality note: 03_aum_by_fund_house.csv's "aum_crore" column was
found to actually be a lakh-crore figure multiplied by 100,000 and
mislabeled as crore (confirmed while building the Power BI dashboard —
see Final_Report.pdf, Section 8.1). This script loads BOTH aum_crore
(as-is, for backward compatibility with existing queries) and
aum_lakh_crore (the correctly-scaled figure) into fact_aum, so downstream
consumers can choose the correct column explicitly rather than guess.
"""

import logging
import sqlite3
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED = PROJECT_ROOT / "data" / "processed"
DB_PATH = PROCESSED / "bluestock_mf.db"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"

FUND_COLS = [
    "amfi_code", "fund_house", "scheme_name", "category", "sub_category",
    "plan", "launch_date", "benchmark", "expense_ratio_pct", "exit_load_pct",
    "fund_manager", "risk_category", "sebi_category_code",
]
TRANSACTION_COLS = [
    "investor_id", "transaction_date", "amfi_code", "transaction_type",
    "amount_inr", "state", "city", "city_tier", "age_group", "gender",
    "payment_mode", "kyc_status",
]
PERFORMANCE_COLS = [
    "amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "sharpe_ratio", "sortino_ratio", "alpha", "beta", "max_drawdown_pct",
]


def rebuild_schema(db_path: Path = DB_PATH, schema_path: Path = SCHEMA_PATH) -> None:
    """Delete any existing database file and recreate it from the schema."""
    if db_path.exists():
        db_path.unlink()
        logger.info("Removed existing database at %s", db_path)

    schema_sql = schema_path.read_text()
    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.close()
    logger.info("Schema applied from %s", schema_path)


def load_all_tables(db_path: Path = DB_PATH, processed_dir: Path = PROCESSED) -> None:
    """Load every cleaned CSV into its corresponding table."""
    engine = create_engine(f"sqlite:///{db_path}")

    fund_master = pd.read_csv(processed_dir / "01_fund_master.csv")
    fund_master[FUND_COLS].to_sql("dim_fund", engine, if_exists="append", index=False)
    logger.info("Loaded dim_fund: %d rows", len(fund_master))

    nav = pd.read_csv(processed_dir / "nav_history_clean.csv")
    nav["amfi_code"] = nav["amfi_code"].astype(str)
    nav[["amfi_code", "date", "nav"]].to_sql("fact_nav", engine, if_exists="append", index=False)
    logger.info("Loaded fact_nav: %d rows", len(nav))

    tx = pd.read_csv(processed_dir / "investor_transactions_clean.csv")
    tx[TRANSACTION_COLS].to_sql("fact_transactions", engine, if_exists="append", index=False)
    logger.info("Loaded fact_transactions: %d rows", len(tx))

    perf = pd.read_csv(processed_dir / "scheme_performance_clean.csv")
    perf[PERFORMANCE_COLS].to_sql("fact_performance", engine, if_exists="append", index=False)
    logger.info("Loaded fact_performance: %d rows", len(perf))

    aum = pd.read_csv(processed_dir / "03_aum_by_fund_house.csv")
    aum["aum_lakh_crore"] = aum["aum_crore"] / 100_000  # see module docstring
    aum[["date", "fund_house", "aum_crore", "aum_lakh_crore", "num_schemes"]].to_sql(
        "fact_aum", engine, if_exists="append", index=False
    )
    logger.info("Loaded fact_aum: %d rows", len(aum))


def main() -> None:
    rebuild_schema()
    load_all_tables()
    logger.info("All tables loaded into %s", DB_PATH)


if __name__ == "__main__":
    main()
