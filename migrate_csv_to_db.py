"""Script to migrate CSV data to PostgreSQL database"""
import os
import sys
import pandas as pd
from sqlalchemy import text
from utils.db_setup import setup_database, get_db_engine
from utils.data_handler import clean_salary_data

def migrate_csv_to_database():
    """Migrate CSV data to PostgreSQL database"""
    print("Starting CSV to PostgreSQL migration...")
    
    # Setup database (create if doesn't exist)
    if not setup_database():
        print("Failed to setup database. Exiting.")
        return False
    
    # Load and clean CSV data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'data', 'salary_data.csv')
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found at: {csv_path}")
        return False
    
    print(f"Reading CSV file: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from CSV")
    
    # Clean the data using existing function
    print("Cleaning data...")
    df = clean_salary_data(df)
    print(f"Cleaned data: {len(df)} rows remaining")
    
    if df.empty:
        print("No data to migrate after cleaning.")
        return False
    
    # Map column names to database column names
    column_mapping = {
        'Role': 'role',
        'Company location (Country)': 'company_location_country',
        'Monthly Gross Salary (in ZMW)': 'monthly_gross_salary_zmw',
        'Salary Gross in USD': 'salary_gross_usd',
        'Years of Experience': 'years_of_experience',
        'Degree': 'degree',
        'Approx. No. of employees in company': 'approx_employees',
        'Your Country/ Location': 'your_country_location',
        'Nationality': 'nationality',
        'Industry': 'industry',
        'Submission Date': 'submission_date'
    }
    
    # Rename columns for database
    df_migrate = df.copy()
    for old_col, new_col in column_mapping.items():
        if old_col in df_migrate.columns:
            df_migrate = df_migrate.rename(columns={old_col: new_col})
    
    # Ensure we only have columns that exist in the mapping
    db_columns = list(column_mapping.values())
    df_migrate = df_migrate[[col for col in db_columns if col in df_migrate.columns]]
    
    # Get database engine
    engine = get_db_engine()
    
    try:
        # Check if data already exists
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM salary_data"))
            existing_count = result.scalar()
            
            if existing_count > 0:
                print(f"Database already contains {existing_count} records.")
                # In non-interactive mode (like Streamlit), default to appending
                try:
                    response = input("Do you want to add the CSV data anyway? (y/n): ")
                    if response.lower() != 'y':
                        print("Migration cancelled.")
                        return False
                except EOFError:
                    # Non-interactive mode, proceed with append
                    print("Non-interactive mode: Appending CSV data to existing records...")
        
        # Insert data into database
        print("Inserting data into database...")
        df_migrate.to_sql(
            'salary_data',
            engine,
            if_exists='append',
            index=False,
            method='multi'
        )
        
        # Verify insertion
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM salary_data"))
            total_count = result.scalar()
            print(f"Migration completed! Total records in database: {total_count}")
        
        return True
        
    except Exception as e:
        print(f"Error migrating data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_csv_to_database()
    sys.exit(0 if success else 1)

