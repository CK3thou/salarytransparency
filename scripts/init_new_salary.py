"""
Initializes the SQLite database.
"""

import sys
from pathlib import Path

# Add project root to path to allow imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.db_setup import init_db, DB_PATH

def main():
    init_db()
    print(f"Ensured database exists: {DB_PATH}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
