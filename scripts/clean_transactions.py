import pandas as pd
import os

df = pd.read_csv("data/raw/08_investor_transactions.csv")

# 1. Parse dates
df["transaction_date"] = pd.to_datetime(df["transaction_date"])

# 2. Standardise transaction_type — strip whitespace, fix casing
df["transaction_type"] = df["transaction_type"].str.strip().str.title()
df["transaction_type"] = df["transaction_type"].replace({"Sip": "SIP"})
print("Transaction types found:", df["transaction_type"].unique())

# 3. Validate amount_inr > 0
invalid_amt = df[df["amount_inr"] <= 0]
print(f"Rows with amount_inr <= 0: {len(invalid_amt)}")
df = df[df["amount_inr"] > 0]

# 4. Check kyc_status values are only expected categories
print("KYC status values found:", df["kyc_status"].unique())
valid_kyc = {"Verified", "Pending"}
unexpected_kyc = df[~df["kyc_status"].isin(valid_kyc)]
print(f"Unexpected KYC values: {len(unexpected_kyc)}")

os.makedirs("data/processed", exist_ok=True)
df.to_csv("data/processed/investor_transactions_clean.csv", index=False)
print("Saved to data/processed/investor_transactions_clean.csv")