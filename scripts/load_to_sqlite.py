import pandas as pd
from sqlalchemy import create_engine
import sqlite3

engine = create_engine("sqlite:///data/processed/bluestock_mf.db")

# Run the schema first
with open("sql/schema.sql", "r") as f:
    schema_sql = f.read()

conn = sqlite3.connect("data/processed/bluestock_mf.db")
conn.executescript(schema_sql)
conn.close()

# Load dim_fund
fund_master = pd.read_csv("data/processed/01_fund_master.csv")
fund_cols = ["amfi_code", "fund_house", "scheme_name", "category", "sub_category",
             "plan", "launch_date", "benchmark", "expense_ratio_pct", "exit_load_pct",
             "fund_manager", "risk_category", "sebi_category_code"]
fund_master[fund_cols].to_sql("dim_fund", engine, if_exists="append", index=False)
print(f"Loaded dim_fund: {len(fund_master)} rows")

# Load fact_nav
nav = pd.read_csv("data/processed/nav_history_clean.csv")
nav["amfi_code"] = nav["amfi_code"].astype(str)
nav[["amfi_code", "date", "nav"]].to_sql("fact_nav", engine, if_exists="append", index=False)
print(f"Loaded fact_nav: {len(nav)} rows")

# Load fact_transactions
tx = pd.read_csv("data/processed/investor_transactions_clean.csv")
tx_cols = ["investor_id", "transaction_date", "amfi_code", "transaction_type",
           "amount_inr", "state", "city", "city_tier", "age_group", "gender",
           "payment_mode", "kyc_status"]
tx[tx_cols].to_sql("fact_transactions", engine, if_exists="append", index=False)
print(f"Loaded fact_transactions: {len(tx)} rows")

# Load fact_performance
perf = pd.read_csv("data/processed/scheme_performance_clean.csv")
perf_cols = ["amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
             "sharpe_ratio", "sortino_ratio", "alpha", "beta", "max_drawdown_pct"]
perf[perf_cols].to_sql("fact_performance", engine, if_exists="append", index=False)
print(f"Loaded fact_performance: {len(perf)} rows")

# Load fact_aum
aum = pd.read_csv("data/processed/03_aum_by_fund_house.csv")
aum[["date", "fund_house", "aum_crore", "num_schemes"]].to_sql(
    "fact_aum", engine, if_exists="append", index=False)
print(f"Loaded fact_aum: {len(aum)} rows")

print("\nAll tables loaded into data/processed/bluestock_mf.db")