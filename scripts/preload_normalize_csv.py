"""
Normalize / clean the provided salary CSV in-place so the app can use it as primary storage.
This script:
- reads /workspaces/salarytransparency/data/salary_data.csv
- normalizes column names to the app canonical names
- removes empty rows
- writes back in canonical column order
"""
from pathlib import Path
import pandas as pd
from utils.data_handler import CANONICAL_COLUMNS, _map_columns, DATA_CSV

def normalize_inplace(csv_path: Path):
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    if df.empty:
        print("CSV empty, writing header only.")
        pd.DataFrame(columns=CANONICAL_COLUMNS).to_csv(csv_path, index=False)
        return
    df = _map_columns(df)
    # drop rows that are completely empty (all canonical columns blank)
    df = df.replace("", pd.NA).dropna(how="all", subset=CANONICAL_COLUMNS)
    # normalize numeric/date where possible
    df["Monthly Gross Salary (in ZMW)"] = pd.to_numeric(df["Monthly Gross Salary (in ZMW)"], errors="coerce")
    df["Salary Gross in USD"] = pd.to_numeric(df["Salary Gross in USD"], errors="coerce")
    df["Submission Date"] = pd.to_datetime(df["Submission Date"], errors="coerce").fillna(pd.Timestamp.utcnow())
    # write back
    df.to_csv(csv_path, index=False)
    print(f"Normalized and wrote {len(df)} rows to {csv_path}")

if __name__ == "__main__":
    csv_path = Path("/workspaces/salarytransparency/data/salary_data.csv")
    if not csv_path.exists():
        print("CSV not found:", csv_path)
    else:
        normalize_inplace(csv_path)