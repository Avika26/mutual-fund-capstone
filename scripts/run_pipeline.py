"""
run_pipeline.py — Bluestock Mutual Fund Capstone

Master execution script. Runs the full ETL pipeline end-to-end, in order:

  1. clean_nav            -> data/processed/nav_history_clean.csv
  2. clean_transactions    -> data/processed/investor_transactions_clean.csv
  3. clean_performance     -> data/processed/scheme_performance_clean.csv
  4. load_to_sqlite        -> data/processed/bluestock_mf.db (rebuilt from scratch)
  5. run_queries           -> sanity-check query run (optional, see --skip-queries)

Usage:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py --skip-queries   # skip the sanity-check step

Safe to re-run at any time: load_to_sqlite.py rebuilds the database from
scratch on every run rather than appending, so re-running this script will
not duplicate any data.

Does NOT run the live NAV fetch (a separate, network-dependent step) —
run that manually first if you need fresh live NAV data before cleaning.
"""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


def run_step(step_name: str, step_fn) -> None:
    """Run a single pipeline step, logging its start/success and stopping the pipeline on failure."""
    logger.info("=== %s ===", step_name)
    try:
        step_fn()
        logger.info("%s complete.\n", step_name)
    except Exception:
        logger.exception("%s failed. Stopping pipeline.", step_name)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Bluestock MF capstone ETL pipeline.")
    parser.add_argument("--skip-queries", action="store_true", help="Skip the final sanity-check query run.")
    args = parser.parse_args()

    import clean_nav
    import clean_transactions
    import clean_performance
    import load_to_sqlite

    run_step("Clean NAV history", clean_nav.main)
    run_step("Clean investor transactions", clean_transactions.main)
    run_step("Validate scheme performance", clean_performance.main)
    run_step("Load database", load_to_sqlite.main)

    if not args.skip_queries:
        import run_queries
        run_step("Run sanity-check queries", run_queries.main)

    logger.info("Pipeline finished successfully.")


if __name__ == "__main__":
    main()
