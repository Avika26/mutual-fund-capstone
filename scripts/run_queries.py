"""
run_queries.py — Bluestock Mutual Fund Capstone

Runs every query in sql/queries.sql against the built database and prints
a preview of each result set. Used as a quick sanity check that the schema
and data loaded correctly — not part of the core ETL pipeline itself.

Input: data/processed/bluestock_mf.db, sql/queries.sql
"""

import logging
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "bluestock_mf.db"
QUERIES_PATH = PROJECT_ROOT / "sql" / "queries.sql"
PREVIEW_ROWS = 5


def load_queries(queries_path: Path = QUERIES_PATH) -> list[str]:
    """Read queries.sql, strip full-line comments, and split into individual statements."""
    lines = queries_path.read_text().splitlines(keepends=True)
    clean_lines = [line for line in lines if not line.strip().startswith("--")]
    sql_script = "".join(clean_lines)
    return [q.strip() for q in sql_script.split(";") if q.strip()]


def run_queries(db_path: Path = DB_PATH, queries_path: Path = QUERIES_PATH) -> None:
    """Execute every query and log a preview of each result set."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for i, query in enumerate(load_queries(queries_path), 1):
        logger.info("--- Query %d ---", i)
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows[:PREVIEW_ROWS]:
                logger.info("%s", row)
            logger.info("(%d total rows)", len(rows))
        except sqlite3.Error as e:
            logger.error("Query %d failed: %s", i, e)

    conn.close()


def main() -> None:
    run_queries()


if __name__ == "__main__":
    main()
