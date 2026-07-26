import os
import glob
import pandas as pd

RAW_DIR = "data/raw"
REPORTS_DIR = "reports"

os.makedirs(REPORTS_DIR, exist_ok=True)

csv_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
dataframes = {}

for path in csv_files:
    name = os.path.splitext(os.path.basename(path))[0]
    print("=" * 70)
    print(f"FILE: {path}")
    df = pd.read_csv(path)
    dataframes[name] = df

    print("Shape:", df.shape)
    print("Dtypes:\n", df.dtypes)
    print("Head:\n", df.head())

    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]
    dups = df.duplicated().sum()
    if not nulls.empty:
        print("Anomaly - nulls found:\n", nulls)
    if dups > 0:
        print(f"Anomaly - {dups} duplicate rows")

fund_master = dataframes.get("01_fund_master")
if fund_master is not None:
    print("=" * 70)
    print("FUND MASTER EXPLORATION")
    print("Unique fund houses:\n", fund_master["fund_house"].unique())
    print("Unique categories:\n", fund_master["category"].unique())
    print("Unique sub-categories:\n", fund_master["sub_category"].unique())
    print("Unique risk categories:\n", fund_master["risk_category"].unique())

nav_history = dataframes.get("02_nav_history")
summary_lines = []
if fund_master is not None and nav_history is not None:
    fm_codes = set(fund_master["amfi_code"].astype(str))
    nav_codes = set(nav_history["amfi_code"].astype(str))
    missing = fm_codes - nav_codes
    print("=" * 70)
    print(f"fund_master unique codes: {len(fm_codes)}")
    print(f"nav_history unique codes: {len(nav_codes)}")
    print(f"codes missing from nav_history: {len(missing)}")
    if missing:
        print("Missing codes:", missing)

    summary_lines.append(f"fund_master unique codes: {len(fm_codes)}")
    summary_lines.append(f"nav_history unique codes: {len(nav_codes)}")
    summary_lines.append(f"codes missing from nav_history: {len(missing)}")

with open(os.path.join(REPORTS_DIR, "data_quality_summary.txt"), "w") as f:
    f.write("DATA QUALITY SUMMARY - Day 1\n")
    f.write("=" * 40 + "\n\n")
    for name, df in dataframes.items():
        f.write(f"{name}: shape={df.shape}, nulls={int(df.isnull().sum().sum())}, "
                f"duplicates={int(df.duplicated().sum())}\n")
    f.write("\n" + "\n".join(summary_lines) + "\n")

print("\nDone. Report written to reports/data_quality_summary.txt")