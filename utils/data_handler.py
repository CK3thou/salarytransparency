import pandas as pd
import os
from datetime import datetime
from sqlalchemy import text
from utils.db_setup import get_db_engine, setup_database

def clean_salary_data(df):
    """Clean and format salary data"""
    try:
        print("Original columns:", df.columns.tolist())  # Debug print

        # Rename columns first
        column_mapping = {
            'Monthly Gross Salary ZMW': 'Monthly Gross Salary (in ZMW)',
            'Company location': 'Company location (Country)',
            'Salary Gross in USD (leave blank if you get paid in ZMW)': 'Salary Gross in USD',
            'Degree (or not)': 'Degree'
        }

        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df = df.rename(columns={old_col: new_col})

        print("Columns after renaming:", df.columns.tolist())  # Debug print

        # Replace '#VALUE!' with NaN
        df['Monthly Gross Salary (in ZMW)'] = pd.to_numeric(df['Monthly Gross Salary (in ZMW)'], errors='coerce')

        # Clean up salary columns
        df['Salary Gross in USD'] = pd.to_numeric(df['Salary Gross in USD'], errors='coerce')

        # Clean up years of experience
        df['Years of Experience'] = df['Years of Experience'].astype(str)
        # Use a raw string for the regex to avoid invalid escape sequence warnings
        df['Years of Experience'] = df['Years of Experience'].str.extract(r'(\d+)', expand=False)
        df['Years of Experience'] = pd.to_numeric(df['Years of Experience'], errors='coerce')

        # Remove unnecessary columns
        columns_to_keep = [
            'Role', 'Company location (Country)', 'Monthly Gross Salary (in ZMW)',
            'Salary Gross in USD', 'Years of Experience', 'Degree',
            'Approx. No. of employees in company', 'Your Country/ Location',
            'Nationality', 'Industry', 'Submission Date'
        ]

        # Ensure all required columns exist
        for col in columns_to_keep:
            if col not in df.columns:
                if col == 'Submission Date':
                    df[col] = pd.Timestamp.now()  # Use current time for existing entries
                else:
                    df[col] = None

        df = df[columns_to_keep]

        # Drop rows where all values are NaN
        df = df.dropna(how='all')

        # Drop rows where salary is NaN
        df = df.dropna(subset=['Monthly Gross Salary (in ZMW)'])

        print("Final columns:", df.columns.tolist())  # Debug print
        print("Number of rows after cleaning:", len(df))  # Debug print

        return df
    except Exception as e:
        print(f"Error cleaning data: {str(e)}")
        return df

def load_data():
    """Load salary data from PostgreSQL database"""
    # Define empty DataFrame with required columns
    empty_df = pd.DataFrame(columns=[
        'Role', 'Company location (Country)', 'Monthly Gross Salary (in ZMW)',
        'Salary Gross in USD', 'Years of Experience', 'Degree',
        'Approx. No. of employees in company', 'Your Country/ Location',
        'Nationality', 'Industry', 'Submission Date'
    ])

    try:
        # Try to load from PostgreSQL database
        print("Attempting to load data from PostgreSQL database...")
        engine = get_db_engine()
        
        # Ensure database and tables exist
        setup_database()
        
        # Query data from database
        query = """
        SELECT 
            role AS "Role",
            company_location_country AS "Company location (Country)",
            monthly_gross_salary_zmw AS "Monthly Gross Salary (in ZMW)",
            salary_gross_usd AS "Salary Gross in USD",
            years_of_experience AS "Years of Experience",
            degree AS "Degree",
            approx_employees AS "Approx. No. of employees in company",
            your_country_location AS "Your Country/ Location",
            nationality AS "Nationality",
            industry AS "Industry",
            submission_date AS "Submission Date"
        FROM salary_data
        ORDER BY submission_date DESC
        """
        
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
        
        if df.empty:
            print("Database is empty, returning empty DataFrame")
            return empty_df
        
        print(f"Successfully loaded {len(df)} rows from database")
        
        # Ensure proper data types
        df['Submission Date'] = pd.to_datetime(df['Submission Date'])
        
        print(f"Columns in DataFrame: {df.columns.tolist()}")
        return df
        
    except Exception as e:
        print(f"Error loading data from database: {str(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        print("Returning empty DataFrame")
        return empty_df

def save_submission(data):
    """Save new submission to PostgreSQL database"""
    # Add submission timestamp
    data['Submission Date'] = pd.Timestamp.now()

    try:
        print("Attempting to save submission to PostgreSQL database...")
        engine = get_db_engine()
        
        # Ensure database and tables exist
        setup_database()
        
        # Prepare data for database insertion
        insert_data = {
            'role': data.get('Role'),
            'company_location_country': data.get('Company location (Country)'),
            'monthly_gross_salary_zmw': data.get('Monthly Gross Salary (in ZMW)'),
            'salary_gross_usd': data.get('Salary Gross in USD'),
            'years_of_experience': data.get('Years of Experience'),
            'degree': data.get('Degree'),
            'approx_employees': data.get('Approx. No. of employees in company'),
            'your_country_location': data.get('Your Country/ Location'),
            'nationality': data.get('Nationality'),
            'industry': data.get('Industry'),
            'submission_date': data.get('Submission Date')
        }
        
        # Convert to DataFrame for easier insertion
        new_row = pd.DataFrame([insert_data])
        
        # Insert into database
        new_row.to_sql(
            'salary_data',
            engine,
            if_exists='append',
            index=False
        )
        
        print("Successfully saved submission to database")
        return True
        
    except Exception as e:
        print(f"Error saving submission to database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def save_uploaded_file(df):
    """Save uploaded Excel/CSV file data to PostgreSQL database"""
    try:
        print("Attempting to save uploaded file data to PostgreSQL database...")
        
        # Add submission timestamp for new entries if column doesn't exist
        if 'Submission Date' not in df.columns:
            df['Submission Date'] = pd.Timestamp.now()

        # Clean data before saving
        df = clean_salary_data(df)
        
        if df.empty:
            print("No data to save after cleaning")
            return False
        
        engine = get_db_engine()
        
        # Ensure database and tables exist
        setup_database()
        
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
        df_db = df.copy()
        for old_col, new_col in column_mapping.items():
            if old_col in df_db.columns:
                df_db = df_db.rename(columns={old_col: new_col})
        
        # Ensure we only have columns that exist in the mapping
        db_columns = [col for col in column_mapping.values() if col in df_db.columns]
        df_db = df_db[db_columns]
        
        # Insert into database
        df_db.to_sql(
            'salary_data',
            engine,
            if_exists='append',
            index=False
        )
        
        print(f"Successfully saved {len(df_db)} rows to database")
        return True
        
    except Exception as e:
        print(f"Error saving uploaded file to database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False