import sys
from pathlib import Path
import sqlite3

# Add project root to path to allow imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from utils.db_setup import get_db_connection

def main():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Normalize 'yes' (case insensitive) to 'Yes'
        cursor.execute("UPDATE salary_entries SET degree = 'Yes' WHERE TRIM(LOWER(degree)) = 'yes' AND degree != 'Yes'")
        changed = cursor.rowcount
        
        conn.commit()
        print(f'Normalized Degree -> Yes: {changed} rows updated')
        
        # Show unique values
        cursor.execute("SELECT DISTINCT degree FROM salary_entries ORDER BY degree")
        uniques = [row[0] for row in cursor.fetchall()]
        print('Unique Degree values after:', uniques)
        
    except Exception as e:
        print(f"Error normalizing degrees: {e}")
        return 1
    finally:
        conn.close()
        
    return 0

if __name__ == '__main__':
    sys.exit(main())
