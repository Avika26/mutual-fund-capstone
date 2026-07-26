import requests
import pandas as pd
import os
import time

SCHEMES = {
    "125497": "SBI_Small_Cap",
    "119551": "SBI_Bluechip",
    "120503": "ICICI_Bluechip",
    "118632": "Nippon_Large_Cap",
    "119092": "Axis_Bluechip",
    "120841": "Kotak_Bluechip",
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

os.makedirs("data/raw", exist_ok=True)

for code, name in SCHEMES.items():
    url = f"https://api.mfapi.in/mf/{code}"
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            payload = resp.json()
            df = pd.DataFrame(payload["data"])
            df["amfi_code"] = code
            df["scheme_name"] = payload["meta"]["scheme_name"]
            df.to_csv(f"data/raw/nav_{name}_{code}.csv", index=False)
            print(f"Saved {name}: {len(df)} rows -> {payload['meta']['scheme_name']}")
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {name}: {e}")
            time.sleep(3)
    else:
        print(f"Giving up on {name} after 3 attempts")