"""
DEPRECATED: This legacy script has been retired.
The application uses a single source of truth: data/new_salary.csv.
This file remains only as a stub to avoid confusion if referenced.
"""

import sys
from utils.data_handler import NEW_CSV, _ensure_csv_exists

def main():
    _ensure_csv_exists(NEW_CSV)
    print(f"Ensured new submissions file exists: {NEW_CSV}")
    print("init_new_salary.py is deprecated and no longer needed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())