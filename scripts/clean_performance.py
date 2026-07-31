import pandas as pd
import os

df = pd.read_csv("data/raw/07_scheme_performance.csv")

# 1. Validate numeric return columns
numeric_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
                 "sharpe_ratio", "sortino_ratio", "alpha", "beta"]
for col in numeric_cols:
    non_numeric = df[pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()]
    if len(non_numeric) > 0:
        print(f"Non-numeric values found in {col}:\n{non_numeric[[col]]}")

# 2. Flag anomalies — extreme/implausible values
flagged = df[(df["sharpe_ratio"] < -2) | (df["sharpe_ratio"] > 5)]
print(f"Flagged {len(flagged)} rows with extreme Sharpe ratios")
print(flagged[["scheme_name", "sharpe_ratio"]])

# 3. Validate expense_ratio_pct is within expected range (0.1% - 2.5%)
bad_expense = df[(df["expense_ratio_pct"] < 0.1) | (df["expense_ratio_pct"] > 2.5)]
print(f"Rows with expense_ratio_pct outside 0.1-2.5 range: {len(bad_expense)}")
if len(bad_expense) > 0:
    print(bad_expense[["scheme_name", "expense_ratio_pct"]])

os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/scheme_performance_clean.csv", index=False)
print("Saved to data/processed/scheme_performance_clean.csv")