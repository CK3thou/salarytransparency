import sqlite3
from pathlib import Path

# Get the project root directory
_project_root = Path(__file__).parent.parent
DB_PATH = _project_root / "data" / "salary.db"

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with the salary_entries table."""
    try:
        # Ensure data directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
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
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        raise

def check_db_health():
    """Check if database is accessible and working."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Test basic operations
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='salary_entries'")
        table_exists = cursor.fetchone()[0] > 0
        
        if not table_exists:
            print("Warning: salary_entries table doesn't exist")
            conn.close()
            return False
            
        # Count rows
        cursor.execute("SELECT COUNT(*) FROM salary_entries")
        row_count = cursor.fetchone()[0]
        print(f"Database OK: salary_entries table exists with {row_count} rows")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False

if __name__ == "__main__":
    init_db()
    check_db_health()

