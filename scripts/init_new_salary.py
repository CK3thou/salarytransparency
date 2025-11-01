"""Create new_salary.csv (header) and optionally copy/normalize preloaded data preview."""
from pathlib import Path
from utils.data_handler import NEW_CSV, CANONICAL_COLUMNS, _ensure_csv_exists

if __name__ == "__main__":
    _ensure_csv_exists(NEW_CSV)
    print(f"Ensured new submissions file exists: {NEW_CSV}")
    print("New submissions will be saved to this file; preloaded data remains in salary_data.csv.")