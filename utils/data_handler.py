from pathlib import Path
import os
import pandas as pd
from datetime import datetime
import sys
import random
from utils.db_setup import get_db_connection, init_db

# Get the project root directory (parent of utils directory)
_project_root = Path(__file__).parent.parent

# CSV containing industries for dropdowns
INDUSTRIES_CSV = _project_root / "data" / "Industries.csv"
# CSV containing nationalities for dropdowns
NATIONALITIES_CSV = _project_root / "data" / "Nationalities.csv"
# CSV containing world cities/locations used for dropdowns
WORLD_CITIES_CSV = _project_root / "data" / "worldcities.csv"

# Canonical column order used by the app
CANONICAL_COLUMNS = [
    "Role",
    "Company location",
    "Monthly Gross Salary",
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

def get_industries() -> list:
    """
    Return a sorted list of industries from the Industries CSV.
    Falls back to an empty list if the file isn't present or cannot be read.
    """
    try:
        if not INDUSTRIES_CSV.exists():
            return []
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

def get_nationalities() -> list:
    """
    Return a sorted list of nationalities from the Nationalities CSV.
    Falls back to an empty list if the file isn't present or cannot be read.
    """
    try:
        if not NATIONALITIES_CSV.exists():
            return []
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

def load_data() -> pd.DataFrame:
    """
    Load all data from the SQLite database and return a normalized DataFrame.
    """
    # Ensure DB is initialized
    init_db()
    
    conn = get_db_connection()
    try:
        query = "SELECT * FROM salary_entries"
        df = pd.read_sql_query(query, conn)
        
        if df.empty:
            return pd.DataFrame(columns=CANONICAL_COLUMNS)
            
        # Rename DB columns to Canonical columns
        rename_map = {
            "role": "Role",
            "company_location": "Company location",
            "monthly_gross_salary": "Monthly Gross Salary",
            "salary_gross_in_usd": "Salary Gross in USD",
            "years_of_experience": "Years of Experience",
            "degree": "Degree",
            "company_size": "Approx. No. of employees in company",
            "country_location": "Your Country/ Location",
            "nationality": "Nationality",
            "industry": "Industry",
            "submission_date": "Submission Date",
            "exchange_rate": "Real-time USD ZMW exchange rate"
        }
        df = df.rename(columns=rename_map)
        
        # Ensure all canonical columns exist
        for col in CANONICAL_COLUMNS:
            if col not in df.columns:
                df[col] = ""
                
        # Compatibility column
        if "Company location" in df.columns and "Company location (Country)" not in df.columns:
            df["Company location (Country)"] = df["Company location"]
            
        # Normalizations (similar to original _read_csv_safe)
        if "Degree" in df.columns:
            df["Degree"] = df["Degree"].astype(str).str.strip().str.title().replace({"Yes": "Yes", "No": "No"})
        if "Nationality" in df.columns:
            nat = df["Nationality"].astype(str).str.strip().str.title()
            df["Nationality"] = nat.replace({"Zambia": "Zambian"})
        if "Industry" in df.columns:
            df["Industry"] = df["Industry"].astype(str).str.strip()
            df["Industry"] = df["Industry"].replace({
                "FCMG": "FMCG",
                "FINANCE": "Finance",
                "banking": "Banking",
            })
            df["Industry"] = df["Industry"].str.title()
            
        # Ensure numeric types
        df["Monthly Gross Salary"] = pd.to_numeric(df["Monthly Gross Salary"], errors="coerce")
        df["Salary Gross in USD"] = pd.to_numeric(df["Salary Gross in USD"], errors="coerce")
        
        # Ensure dates
        df["Submission Date"] = pd.to_datetime(df["Submission Date"], errors="coerce")
        
        return df[CANONICAL_COLUMNS + ["Company location (Country)"]] if "Company location (Country)" in df.columns else df[CANONICAL_COLUMNS]
        
    except Exception as e:
        print(f"Error loading data from DB: {e}")
        return pd.DataFrame(columns=CANONICAL_COLUMNS)
    finally:
        conn.close()

def save_submission(record: dict):
    """
    Save a single submission to the SQLite database.
    Returns True on success, False on failure.
    """
    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        mapping_preferences = {
            "role": ["Role", "role"],
            "company_location": ["Company location", "company_location", "Company location (Country)"],
            "monthly_gross_salary": ["Monthly Gross Salary", "monthly_gross_salary_zmw", "Monthly Salary (ZMW)"],
            "salary_gross_in_usd": ["Salary Gross in USD", "Salary Gross in USD (leave blank if you get paid in ZMW)", "salary_gross_usd"],
            "years_of_experience": ["Years of Experience", "years_of_experience"],
            "degree": ["Degree", "Degree (or not)", "degree"],
            "company_size": ["Approx. No. of employees in company", "approx_no_of_employees"],
            "country_location": ["Your Country/ Location", "country_location"],
            "nationality": ["Nationality", "nationality"],
            "industry": ["Industry", "industry"],
            "submission_date": ["Submission Date", "submission_date"],
            "exchange_rate": ["Real-time USD ZMW exchange rate", "realtime_usd_zmw_rate"]
        }
        
        # Build DB row
        db_row = {}
        for db_col, keys in mapping_preferences.items():
            val = None
            for k in keys:
                if k in record and record.get(k) not in (None, ""):
                    val = record.get(k)
                    break
            
            if db_col == "submission_date":
                if not val:
                    val = datetime.now().strftime("%Y-%m-%d")
                else:
                    try:
                        # Try to parse and format as ISO
                        val = pd.to_datetime(str(val), dayfirst=True, errors="coerce").strftime("%Y-%m-%d")
                    except Exception:
                        val = datetime.now().strftime("%Y-%m-%d")
            
            # Numeric handling
            if db_col in ("monthly_gross_salary", "salary_gross_in_usd", "exchange_rate") and val is not None:
                try:
                    val = float(val)
                except:
                    val = None
            
            db_row[db_col] = val

        cursor.execute('''
            INSERT INTO salary_entries (
                role, company_location, monthly_gross_salary, salary_gross_in_usd,
                years_of_experience, degree, company_size, country_location,
                nationality, industry, submission_date, exchange_rate
            ) VALUES (
                :role, :company_location, :monthly_gross_salary, :salary_gross_in_usd,
                :years_of_experience, :degree, :company_size, :country_location,
                :nationality, :industry, :submission_date, :exchange_rate
            )
        ''', db_row)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving submission to DB: {e}")
        return False

def backfill_new_csv_submission_dates(
    start_date: str = "2023-08-03",
    end_date: str = "2023-12-31"
) -> int:
    """
    Backfill missing 'submission_date' values in DB with random dates.
    """
    try:
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find rows with missing dates
        cursor.execute("SELECT id FROM salary_entries WHERE submission_date IS NULL OR submission_date = ''")
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return 0
            
        try:
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
        except Exception:
            start_dt = pd.Timestamp(2023, 8, 3)
            end_dt = pd.Timestamp(2023, 12, 31)
            
        total_days = (end_dt - start_dt).days
        updated_count = 0
        
        for row in rows:
            rand_day = random.randint(0, total_days)
            rand_date = (start_dt + pd.Timedelta(days=rand_day)).strftime("%Y-%m-%d")
            
            cursor.execute("UPDATE salary_entries SET submission_date = ? WHERE id = ?", (rand_date, row['id']))
            updated_count += 1
            
        conn.commit()
        conn.close()
        return updated_count
    except Exception as e:
        print(f"Error backfilling dates: {e}")
        return 0
