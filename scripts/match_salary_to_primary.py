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
        # Backfill monthly_gross_salary from salary_gross_in_usd if missing
        # Note: This assumes 1:1 if no FX rate is applied, or just copies it as a fallback.
        # The original script copied USD as-is to avoid FX dependencies.
        
        cursor.execute("""
            UPDATE salary_entries 
            SET monthly_gross_salary = salary_gross_in_usd 
            WHERE (monthly_gross_salary IS NULL OR monthly_gross_salary = '' OR monthly_gross_salary = 0) 
            AND salary_gross_in_usd IS NOT NULL 
            AND salary_gross_in_usd != ''
        """)
        copied_count = cursor.rowcount
        
        conn.commit()
        print(f'Copied USD to Monthly Gross Salary (where missing): {copied_count} rows updated')
        
    except Exception as e:
        print(f"Error matching salaries: {e}")
        return 1
    finally:
        conn.close()
        
    return 0

if __name__ == '__main__':
    sys.exit(main())
