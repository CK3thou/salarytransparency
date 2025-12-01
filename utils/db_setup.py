import sqlite3
from pathlib import Path

# Get the project root directory
_project_root = Path(__file__).parent.parent
DB_PATH = _project_root / "data" / "salary.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the salary_entries table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salary_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            company_location TEXT,
            monthly_gross_salary REAL,
            salary_gross_in_usd REAL,
            years_of_experience TEXT,
            degree TEXT,
            company_size TEXT,
            country_location TEXT,
            nationality TEXT,
            industry TEXT,
            submission_date TEXT,
            exchange_rate REAL
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()

