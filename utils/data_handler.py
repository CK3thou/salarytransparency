from pathlib import Path
import os
# Get the project root directory (parent of utils directory)
_project_root = Path(__file__).parent.parent
# CSV containing industries for dropdowns
INDUSTRIES_CSV = _project_root / "data" / "Industries.csv"

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
NATIONALITIES_CSV = _project_root / "data" / "Nationalities.csv"

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
import csv
import threading
import pandas as pd
from datetime import datetime
import sys
import random
from datetime import timedelta

# Cross-platform file locking (fcntl only works on Unix)
# On Windows, we rely on threading.Lock for synchronization
if sys.platform == 'win32':
    # Windows: use no-op locking (threading lock provides synchronization)
    def lock_file(f):
        pass
    def unlock_file(f):
        pass
else:
    # Unix/Linux: use fcntl for file-level locking
    import fcntl
    def lock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
    def unlock_file(f):
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

# Get the project root directory (parent of utils directory)
_project_root = Path(__file__).parent.parent

# Original preloaded CSV (read-only source of initial data)
DATA_CSV = _project_root / "data" / "salary_data.csv"

# New CSV file that will be the primary storage for all new submissions
NEW_CSV = _project_root / "data" / "new_salary.csv"

# CSV containing world cities/locations used for dropdowns
WORLD_CITIES_CSV = _project_root / "data" / "worldcities.csv"

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
        # Trim whitespace across all string cells
        for c in df.columns:
            if df[c].dtype == object:
                df[c] = df[c].astype(str).str.strip().str.strip('"')
        # If reading NEW_CSV, backfill missing Submission Date with random ISO dates in 2023-08-03..2023-12-31
        if path == NEW_CSV and "Submission Date" in df.columns:
            sub_raw = df["Submission Date"].astype(str).str.strip()
            missing_mask = sub_raw.eq("") | sub_raw.str.lower().isin(["nan", "none", "nat"])
            if missing_mask.any():
                start_dt = pd.Timestamp(2023, 8, 3)
                end_dt = pd.Timestamp(2023, 12, 31)
                total_days = (end_dt - start_dt).days
                rand_days = [random.randint(0, total_days) for _ in range(int(missing_mask.sum()))]
                backfill_dates = [(start_dt + pd.Timedelta(days=d)).strftime("%Y-%m-%d") for d in rand_days]
                df.loc[missing_mask, "Submission Date"] = backfill_dates
        # Normalize specific columns for display consistency
        if "Degree" in df.columns:
            df["Degree"] = df["Degree"].str.strip().str.title().replace({"Yes": "Yes", "No": "No"})
        if "Nationality" in df.columns:
            nat = df["Nationality"].str.strip().str.title()
            # Common correction: country name 'Zambia' to demonym 'Zambian'
            df["Nationality"] = nat.replace({"Zambia": "Zambian"})
        if "Your Country/ Location" in df.columns:
            df["Your Country/ Location"] = df["Your Country/ Location"].str.strip()
        if "Company location" in df.columns:
            df["Company location"] = df["Company location"].str.strip()
        if "Industry" in df.columns:
            # Normalize simple industry casing and fix common typos
            df["Industry"] = df["Industry"].astype(str).str.strip()
            df["Industry"] = df["Industry"].replace({
                "FCMG": "FMCG",
                "FINANCE": "Finance",
                "banking": "Banking",
            })
            df["Industry"] = df["Industry"].str.title()
        # Ensure compatibility column used elsewhere
        if "Company location" in df.columns and "Company location (Country)" not in df.columns:
            df["Company location (Country)"] = df["Company location"]
        # normalize numeric fields
        df["Monthly Gross Salary (in ZMW)"] = pd.to_numeric(df["Monthly Gross Salary (in ZMW)"], errors="coerce")
        df["Salary Gross in USD"] = pd.to_numeric(df["Salary Gross in USD"], errors="coerce")
        # parse submission date safely (treat day-first format for NEW_CSV)
        dayfirst = (path == NEW_CSV)
        dates = pd.to_datetime(df["Submission Date"], errors="coerce", dayfirst=dayfirst)
        try:
            dates = dates.infer_objects(copy=False)
        except Exception:
            pass
        dates = dates.fillna(pd.Timestamp.utcnow())
        df["Submission Date"] = dates.astype("datetime64[ns]")
        # Persist cleaned NEW_CSV back to disk so dataset stays fixed on disk
        if path == NEW_CSV:
            df_to_write = df.copy()
            # Ensure dates are written as ISO yyyy-mm-dd
            df_to_write["Submission Date"] = pd.to_datetime(df_to_write["Submission Date"], errors="coerce").dt.strftime("%Y-%m-%d")
            with _lock:
                df_to_write.to_csv(path, index=False, encoding="utf-8")
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
    Also ensures preloaded rows have Submission Date = 2022-01-01 so the UI can
    easily distinguish them from new submissions.
    """
    # ensure new file exists (header) so save_submission can append later
    _ensure_csv_exists(NEW_CSV)

    # Use the helper that normalizes preloaded dates to 2022-01-01
    base_df = load_preloaded_data()
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
                lock_file(f)
                f.seek(0)
                content = f.read(1)
                writer = csv.DictWriter(f, fieldnames=CANONICAL_COLUMNS)
                if not content:
                    f.seek(0)
                    writer.writeheader()
                f.seek(0, 2)
                writer.writerow(row)
            finally:
                unlock_file(f)


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


def backfill_new_csv_submission_dates(
    start_date: str = "2023-08-03",
    end_date: str = "2023-12-31"
) -> int:
    """
    Backfill missing or blank 'Submission Date' values in NEW_CSV with random
    ISO dates (YYYY-MM-DD) between the given inclusive date range.

    Returns the number of rows updated.
    """
    _ensure_csv_exists(NEW_CSV)
    if not NEW_CSV.exists():
        return 0

    # Load as strings to preserve formatting and columns
    df = pd.read_csv(NEW_CSV, dtype=str, keep_default_na=False)
    if df.empty:
        return 0
    if "Submission Date" not in df.columns:
        df["Submission Date"] = ""

    # Prepare date range
    try:
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
    except Exception:
        # Fallback hard-coded if parsing fails
        start_dt = pd.Timestamp(2023, 8, 3)
        end_dt = pd.Timestamp(2023, 12, 31)

    total_days = (end_dt - start_dt).days
    if total_days < 0:
        start_dt, end_dt = end_dt, start_dt
        total_days = (end_dt - start_dt).days

    # Identify rows needing backfill
    sub = df["Submission Date"].astype(str).str.strip()
    mask = sub.eq("") | sub.str.lower().isin(["nan", "none", "nat"])

    updated = 0
    if mask.any():
        # Generate random dates for each missing row
        rand_days = [random.randint(0, total_days) for _ in range(mask.sum())]
        rand_dates = [(start_dt + pd.Timedelta(days=d)).strftime("%Y-%m-%d") for d in rand_days]
        df.loc[mask, "Submission Date"] = rand_dates
        updated = int(mask.sum())

        # Write back to disk atomically-ish
        with _lock:
            df.to_csv(NEW_CSV, index=False, encoding="utf-8")

    return updated