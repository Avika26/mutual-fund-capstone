"""
clean_transactions.py — Bluestock Mutual Fund Capstone

Cleans raw investor transaction data: parses dates, standardizes
transaction_type casing/spelling, validates amount_inr, and checks
kyc_status values against the expected category set.

Input:  data/raw/08_investor_transactions.csv
Output: data/processed/investor_transactions_clean.csv
"""

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "08_investor_transactions.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "investor_transactions_clean.csv"

VALID_KYC_STATUSES = {"Verified", "Pending"}


def clean_transactions(raw_path: Path = RAW_PATH) -> pd.DataFrame:
    """Load and clean the raw investor transactions CSV, returning the cleaned DataFrame."""
    df = pd.read_csv(raw_path)

    df["transaction_date"] = pd.to_datetime(df["transaction_date"])

    # Standardise transaction_type — strip whitespace, fix casing/spelling
    df["transaction_type"] = df["transaction_type"].str.strip().str.title()
    df["transaction_type"] = df["transaction_type"].replace({"Sip": "SIP"})
    logger.info("Transaction types found: %s", df["transaction_type"].unique().tolist())

    # Validate amount_inr > 0
    invalid_amt = df[df["amount_inr"] <= 0]
    logger.info("Rows with amount_inr <= 0: %d", len(invalid_amt))
    df = df[df["amount_inr"] > 0]

    # Check kyc_status values are only expected categories (flagged, not dropped)
    logger.info("KYC status values found: %s", df["kyc_status"].unique().tolist())
    unexpected_kyc = df[~df["kyc_status"].isin(VALID_KYC_STATUSES)]
    logger.info("Unexpected KYC values: %d", len(unexpected_kyc))

    return df


def main() -> None:
    df = clean_transactions()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info("Saved to %s", OUTPUT_PATH)


if __name__ == "__main__":
    main()
