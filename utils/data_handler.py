from pathlib import Path
import os

# Get the project root directory (parent of utils directory)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# CSV containing industries for dropdowns
INDUSTRIES_CSV = DATA_DIR / "Industries.csv"

def get_industries() -> list:
    """
    Return a sorted list of industries from the Industries CSV.
    Falls back to an empty list if the file isn't present or cannot be read.
    """
    try:
        if not INDUSTRIES_CSV.exists():
            return []
        import pandas as pd
        df = pd.read_csv(INDUSTRIES_CSV, dtype=str, keep_default_na=False)
        if df.empty:
            return []
        # Prefer a column named 'Industry' but fall back to the first column
        if 'Industry' in df.columns:
            series = df['Industry']
        else:
            series = df.iloc[:, 0]
        # Normalize entries: strip whitespace and quotes, remove empties
        inds = series.astype(str).str.strip().str.strip('"').tolist()
        inds = [i for i in inds if i and i.lower() not in ('nan', 'none', 'industry')]
        unique_sorted = sorted(set(inds))
        return unique_sorted
    except Exception:
        return []
# CSV containing nationalities for dropdowns
NATIONALITIES_CSV = DATA_DIR / "Nationalities.csv"

def get_nationalities() -> list:
    """
    Return a sorted list of nationalities from the Nationalities CSV.
    Falls back to an empty list if the file isn't present or cannot be read.
    """
    try:
        if not NATIONALITIES_CSV.exists():
            return []
        import pandas as pd
        df = pd.read_csv(NATIONALITIES_CSV, dtype=str, keep_default_na=False)
        if df.empty:
            return []
        # Prefer a column named 'Nationality' but fall back to the first column
        if 'Nationality' in df.columns:
            series = df['Nationality']
        else:
            series = df.iloc[:, 0]
        # Normalize entries: strip whitespace and quotes, remove empties
        nats = series.astype(str).str.strip().str.strip('"').tolist()
        nats = [n for n in nats if n and n.lower() not in ('nan', 'none')]
        unique_sorted = sorted(set(nats))
        return unique_sorted
    except Exception:
        return []
from pathlib import Path
import csv
import threading
import pandas as pd
from datetime import datetime
import fcntl

# Original preloaded CSV (read-only source of initial data)
DATA_CSV = DATA_DIR / "salary_data.csv"

# New CSV file that will be the primary storage for all new submissions
NEW_CSV = DATA_DIR / "new_salary.csv"

# CSV containing world cities/locations used for dropdowns
WORLD_CITIES_CSV = DATA_DIR / "worldcities.csv"

# Canonical column order used by the app
CANONICAL_COLUMNS = [
    "Role",
    "Company location",
    "Monthly Gross Salary (in ZMW)",
    "Salary Gross in USD",
    "Years of Experience",
    "Degree",
    "Approx. No. of employees in company",
    "Your Country/ Location",
    "Nationality",
    "Industry",
    "Submission Date",
    "Real-time USD ZMW exchange rate"
]

_lock = threading.Lock()

def _ensure_csv_exists(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CANONICAL_COLUMNS)

def _map_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_map = {
        "Company location": "Company location",
        "Company location (Country)": "Company location",
        "Monthly Gross Salary ZMW": "Monthly Gross Salary (in ZMW)",
        "Monthly Gross Salary (in ZMW)": "Monthly Gross Salary (in ZMW)",
        "Salary Gross in USD (leave blank if you get paid in ZMW)": "Salary Gross in USD",
        "Salary Gross in USD": "Salary Gross in USD",
        "Years of Experience": "Years of Experience",
        "Degree (or not)": "Degree",
        "Degree": "Degree",
        "Approx. No. of employees in company": "Approx. No. of employees in company",
        "Your Country/ Location": "Your Country/ Location",
        "Nationality": "Nationality",
        "Industry": "Industry",
        "Real-time USD ZMW exchange rate": "Real-time USD ZMW exchange rate",
        "Submission Date": "Submission Date",
        "Role": "Role",
        "role": "Role"
    }
    new_cols = {}
    for c in df.columns:
        mapped = col_map.get(c, None)
        if mapped:
            new_cols[c] = mapped
        else:
            new_cols[c] = c
    df = df.rename(columns=new_cols)
    for col in CANONICAL_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    # Ensure compatibility column for display
    if "Company location" in df.columns and "Company location (Country)" not in df.columns:
        df["Company location (Country)"] = df["Company location"]
    # If both exist but "Company location (Country)" is empty, fill from "Company location"
    if "Company location (Country)" in df.columns and "Company location" in df.columns:
        df["Company location (Country)"] = df["Company location (Country)"].replace("", pd.NA).fillna(df["Company location"])
    df = df[CANONICAL_COLUMNS]
    return df

def _read_csv_safe(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=CANONICAL_COLUMNS)
    try:
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
        if df.empty:
            return pd.DataFrame(columns=CANONICAL_COLUMNS)
        df = _map_columns(df)
        # Ensure compatibility column used elsewhere
        if "Company location" in df.columns and "Company location (Country)" not in df.columns:
            df["Company location (Country)"] = df["Company location"]
        # normalize numeric fields
        df["Monthly Gross Salary (in ZMW)"] = pd.to_numeric(df["Monthly Gross Salary (in ZMW)"], errors="coerce")
        df["Salary Gross in USD"] = pd.to_numeric(df["Salary Gross in USD"], errors="coerce")
        # parse submission date safely and avoid future downcasting warning
        dates = pd.to_datetime(df["Submission Date"], errors="coerce")
        try:
            dates = dates.infer_objects(copy=False)
        except Exception:
            pass
        dates = dates.fillna(pd.Timestamp.utcnow())
        df["Submission Date"] = dates.astype("datetime64[ns]")
        return df
    except Exception:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)

def load_preloaded_data() -> pd.DataFrame:
    """
    Return the preloaded data (from DATA_CSV) with Submission Date set to 2022-01-01
    so preloaded rows show the requested fixed submission date.
    """
    base = _read_csv_safe(DATA_CSV)
    if base.empty:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)
    # set Submission Date to 2022-01-01 for all preloaded rows
    base["Submission Date"] = pd.to_datetime("2022-01-01")
    # ensure compatibility column name expected elsewhere
    if "Company location" in base.columns and "Company location (Country)" not in base.columns:
        base["Company location (Country)"] = base["Company location"]
    return base

def load_data() -> pd.DataFrame:
    """
    Load preloaded data (salary_data.csv) and any new submissions (new_salary.csv),
    concatenate them and return a single DataFrame the app will use.
    """
    # ensure new file exists (header) so save_submission can append later
    _ensure_csv_exists(NEW_CSV)

    # base_df should be read without overriding dates here (preloaded dates are set via load_preloaded_data)
    base_df = _read_csv_safe(DATA_CSV)
    new_df = _read_csv_safe(NEW_CSV)

    if base_df.empty and new_df.empty:
        return pd.DataFrame(columns=CANONICAL_COLUMNS)

    combined = pd.concat([base_df, new_df], ignore_index=True, sort=False)
    # keep canonical columns and compatibility name expected by filters
    if "Company location" in combined.columns and "Company location (Country)" not in combined.columns:
        combined["Company location (Country)"] = combined["Company location"]
    return combined

def save_submission(record: dict):
    """
    Append a single submission to NEW_CSV. This file is the primary storage for new entries.
    Uses an exclusive file lock to avoid concurrent write corruption.
    """
    _ensure_csv_exists(NEW_CSV)

    mapping_preferences = {
        "Role": ["Role", "role"],
        "Company location": ["Company location", "company_location", "Company location (Country)"],
        "Monthly Gross Salary (in ZMW)": ["Monthly Gross Salary (in ZMW)", "Monthly Gross Salary ZMW", "monthly_gross_salary_zmw"],
        "Salary Gross in USD": ["Salary Gross in USD", "Salary Gross in USD (leave blank if you get paid in ZMW)", "salary_gross_usd"],
        "Years of Experience": ["Years of Experience", "years_of_experience"],
        "Degree": ["Degree", "Degree (or not)", "degree"],
        "Approx. No. of employees in company": ["Approx. No. of employees in company", "approx_no_of_employees"],
        "Your Country/ Location": ["Your Country/ Location", "country_location"],
        "Nationality": ["Nationality", "nationality"],
        "Industry": ["Industry", "industry"],
        "Submission Date": ["Submission Date", "submission_date"],
        "Real-time USD ZMW exchange rate": ["Real-time USD ZMW exchange rate", "realtime_usd_zmw_rate"]
    }

    row = {}
    for canonical, keys in mapping_preferences.items():
        val = None
        for k in keys:
            if k in record and record.get(k) not in (None, ""):
                val = record.get(k)
                break
        if canonical == "Submission Date" and not val:
            val = datetime.utcnow().isoformat(sep=" ")
        row[canonical] = "" if val is None else val

    # append to NEW_CSV with file lock
    with _lock:
        with open(NEW_CSV, "a+", newline="", encoding="utf-8") as f:
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.seek(0)
                content = f.read(1)
                writer = csv.DictWriter(f, fieldnames=CANONICAL_COLUMNS)
                if not content:
                    f.seek(0)
                    writer.writeheader()
                f.seek(0, 2)
                writer.writerow(row)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def get_locations() -> list:
    """
    Return a sorted list of locations from the worldcities CSV.
    Falls back to an empty list if the file isn't present or cannot be read.
    """
    try:
        if not WORLD_CITIES_CSV.exists():
            return []
        # Use pandas for robust CSV parsing (handles quoted values)
        df = pd.read_csv(WORLD_CITIES_CSV, dtype=str, keep_default_na=False)
        if df.empty:
            return []
        # Prefer a column named 'Location' but fall back to the first column
        if 'Location' in df.columns:
            series = df['Location']
        else:
            series = df.iloc[:, 0]
        # Normalize entries: strip whitespace and quotes, remove empties
        locs = series.astype(str).str.strip().str.strip('"').tolist()
        # Filter out blanks and duplicates, sort alphabetically
        locs = [l for l in locs if l and l.lower() not in ('nan', 'none')]
        unique_sorted = sorted(set(locs))
        return unique_sorted
    except Exception:
        return []