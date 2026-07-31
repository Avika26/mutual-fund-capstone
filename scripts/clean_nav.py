import pandas as pd
import os

df = pd.read_csv("data/raw/02_nav_history.csv")

# 1. Parse dates properly (currently stored as text)
df["date"] = pd.to_datetime(df["date"])

# 2. Sort — required before forward-fill logic works correctly
df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)

# 3. Remove exact duplicate rows
before = len(df)
df = df.drop_duplicates()
print(f"Removed {before - len(df)} duplicate rows")

# 4. Validate NAV > 0 — flag instead of silently dropping
invalid_nav = df[df["nav"] <= 0]
print(f"Rows with NAV <= 0: {len(invalid_nav)}")
df = df[df["nav"] > 0]

# 5. Fill missing calendar days (weekends/holidays) per fund
filled_parts = []
for code, group in df.groupby("amfi_code"):
    group = group.set_index("date")
    full_range = pd.date_range(group.index.min(), group.index.max(), freq="D")
    group = group.reindex(full_range)
    group["amfi_code"] = code
    group["nav"] = group["nav"].ffill()
    filled_parts.append(group)

df_clean = pd.concat(filled_parts).reset_index().rename(columns={"index": "date"})

print("Final shape:", df_clean.shape)

os.makedirs("data/processed", exist_ok=True)
df_clean.to_csv("data/processed/nav_history_clean.csv", index=False)
print("Saved to data/processed/nav_history_clean.csv")