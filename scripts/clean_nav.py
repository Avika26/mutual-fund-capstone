"""
clean_nav.py — Bluestock Mutual Fund Capstone

Cleans raw NAV history data: parses dates, removes duplicates, validates
NAV values, and fills missing calendar days (weekends/holidays) per fund
using forward-fill so every fund has a value for every day in its range.

Input:  data/raw/02_nav_history.csv
Output: data/processed/nav_history_clean.csv
"""

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "02_nav_history.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "nav_history_clean.csv"


def clean_nav(raw_path: Path = RAW_PATH) -> pd.DataFrame:
    """Load and clean the raw NAV history CSV, returning the cleaned DataFrame."""
    df = pd.read_csv(raw_path)

    # Parse dates (stored as text in the raw file)
    df["date"] = pd.to_datetime(df["date"])

    # Sort — required before forward-fill logic works correctly
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

    # Remove exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    logger.info("Removed %d duplicate rows", before - len(df))

    # Validate NAV > 0 — flag and drop invalid rows rather than silently ignoring them
    invalid_nav = df[df["nav"] <= 0]
    logger.info("Rows with NAV <= 0: %d", len(invalid_nav))
    df = df[df["nav"] > 0]

    # Fill missing calendar days (weekends/holidays) per fund via forward-fill.
    # Note: this means fact_nav/nav_history_clean has a value for every calendar
    # day, not just trading days — downstream analysis must filter to trading
    # days (Mon-Fri) before computing returns, or volatility will be understated.
    filled_parts = []
    for code, group in df.groupby("amfi_code"):
        group = group.set_index("date")
        full_range = pd.date_range(group.index.min(), group.index.max(), freq="D")
        group = group.reindex(full_range)
        group["amfi_code"] = code
        group["nav"] = group["nav"].ffill()
        filled_parts.append(group)

    df_clean = pd.concat(filled_parts).reset_index().rename(columns={"index": "date"})
    logger.info("Final shape: %s", df_clean.shape)
    return df_clean


def main() -> None:
    df_clean = clean_nav()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(OUTPUT_PATH, index=False)
    logger.info("Saved to %s", OUTPUT_PATH)


if __name__ == "__main__":
    main()
