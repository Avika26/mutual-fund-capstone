"""
clean_performance.py — Bluestock Mutual Fund Capstone

Validates raw scheme performance data: checks that return/risk columns are
genuinely numeric, and flags (does not drop) extreme Sharpe ratios and
out-of-range expense ratios for manual review. Values are flagged rather
than silently corrected or removed, since "extreme" here may reflect a
genuine data characteristic (see Final_Report.pdf, Section 6.3, for the
Sharpe Ratio discrepancy this flagged during analysis).

Input:  data/raw/07_scheme_performance.csv
Output: data/processed/scheme_performance_clean.csv
"""

import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "07_scheme_performance.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "scheme_performance_clean.csv"

NUMERIC_COLS = [
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "sharpe_ratio", "sortino_ratio", "alpha", "beta",
]
SHARPE_LOW, SHARPE_HIGH = -2, 5
EXPENSE_LOW, EXPENSE_HIGH = 0.1, 2.5


def validate_performance(raw_path: Path = RAW_PATH) -> pd.DataFrame:
    """Load the raw scheme performance CSV and log validation warnings. Returns the DataFrame unmodified."""
    df = pd.read_csv(raw_path)

    # Check for non-numeric values hiding in columns that should be numeric
    for col in NUMERIC_COLS:
        non_numeric = df[pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()]
        if len(non_numeric) > 0:
            logger.warning("Non-numeric values found in %s:\n%s", col, non_numeric[[col]])

    # Flag extreme/implausible Sharpe ratios for manual review
    flagged = df[(df["sharpe_ratio"] < SHARPE_LOW) | (df["sharpe_ratio"] > SHARPE_HIGH)]
    logger.info("Flagged %d rows with extreme Sharpe ratios", len(flagged))
    if len(flagged) > 0:
        logger.info("%s", flagged[["scheme_name", "sharpe_ratio"]])

    # Flag expense ratios outside the expected 0.1%-2.5% range
    bad_expense = df[(df["expense_ratio_pct"] < EXPENSE_LOW) | (df["expense_ratio_pct"] > EXPENSE_HIGH)]
    logger.info("Rows with expense_ratio_pct outside %s-%s range: %d", EXPENSE_LOW, EXPENSE_HIGH, len(bad_expense))
    if len(bad_expense) > 0:
        logger.info("%s", bad_expense[["scheme_name", "expense_ratio_pct"]])

    return df


def main() -> None:
    df = validate_performance()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info("Saved to %s", OUTPUT_PATH)


if __name__ == "__main__":
    main()
