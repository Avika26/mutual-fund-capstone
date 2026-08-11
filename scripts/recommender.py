"""
Simple Fund Recommender — Bluestock Mutual Fund Capstone

Given a risk appetite (Low / Moderate / High), returns the top 3 funds by
Sharpe ratio within the matching risk_grade bucket.

Risk mapping (data has 5 raw categories, condensed to 3 for user input):
  Low      -> Low
  Moderate -> Moderate, Moderately High
  High     -> High, Very High
"""

import pandas as pd
import sqlite3
from pathlib import Path

RISK_MAP = {
    'Low': ['Low'],
    'Moderate': ['Moderate', 'Moderately High'],
    'High': ['High', 'Very High']
}


def get_recommendations(risk_appetite, db_path, sharpe_series, top_n=3):
    """
    risk_appetite: str, one of 'Low', 'Moderate', 'High'
    db_path: Path to bluestock_mf.db
    sharpe_series: pd.Series indexed by amfi_code, containing Sharpe ratios
                   (must be computed beforehand, e.g. from Performance_Analytics)
    top_n: number of funds to return
    """
    if risk_appetite not in RISK_MAP:
        raise ValueError(f"risk_appetite must be one of {list(RISK_MAP.keys())}")

    conn = sqlite3.connect(db_path)
    dim_fund = pd.read_sql(
        "SELECT amfi_code, scheme_name, category, risk_category FROM dim_fund", conn
    )
    conn.close()

    matching_categories = RISK_MAP[risk_appetite]
    matched_funds = dim_fund[dim_fund['risk_category'].isin(matching_categories)].copy()

    matched_funds['sharpe_ratio'] = matched_funds['amfi_code'].map(sharpe_series)
    matched_funds = matched_funds.dropna(subset=['sharpe_ratio'])

    top_funds = matched_funds.sort_values('sharpe_ratio', ascending=False).head(top_n)
    return top_funds[['amfi_code', 'scheme_name', 'category', 'risk_category', 'sharpe_ratio']]


if __name__ == "__main__":
    print("This script is meant to be imported, e.g.:")
    print("  from recommender import get_recommendations")
    print("  get_recommendations('Moderate', db_path, sharpe_series)")