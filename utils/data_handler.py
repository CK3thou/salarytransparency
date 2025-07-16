import pandas as pd
import os
from datetime import datetime

def clean_salary_data(df):
    """Clean and format salary data"""
    try:
        print("Original columns:", df.columns.tolist())  # Debug print

        # Rename columns first
        column_mapping = {
            'Monthly Gross Salary ZMW': 'Monthly Gross Salary (in ZMW)',
            'Company location': 'Company location (Country)',
            'Salary Gross in USD (leave blank if you get paid in ZMW)': 'Salary Gross in USD'
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
        df['Years of Experience'] = df['Years of Experience'].str.extract('(\d+)', expand=False)
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
    """Load salary data from Excel or CSV file"""
    # Define empty DataFrame with required columns
    empty_df = pd.DataFrame(columns=[
        'Role', 'Company location (Country)', 'Monthly Gross Salary (in ZMW)',
        'Salary Gross in USD', 'Years of Experience', 'Degree',
        'Approx. No. of employees in company', 'Your Country/ Location',
        'Nationality', 'Industry', 'Submission Date'
    ])

    try:
        # Get the absolute path to the data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(current_dir), 'data')
        excel_path = os.path.join(data_dir, 'salary_data.xlsx')
        csv_path = os.path.join(data_dir, 'salary_data.csv')

        print(f"Current working directory: {os.getcwd()}")
        print(f"Looking for data files in: {data_dir}")
        print(f"Excel path: {excel_path}")
        print(f"CSV path: {csv_path}")
        print(f"Excel file exists: {os.path.exists(excel_path)}")
        print(f"CSV file exists: {os.path.exists(csv_path)}")

        # Try to load Excel file first
        if os.path.exists(excel_path):
            print("Found Excel file, loading data...")
            try:
                df = pd.read_excel(excel_path)
                print(f"Successfully read Excel file with {len(df)} rows")
            except Exception as e:
                print(f"Error reading Excel file: {str(e)}")
                raise
        # Fall back to CSV if Excel doesn't exist
        elif os.path.exists(csv_path):
            print("Found CSV file, loading data...")
            try:
                df = pd.read_csv(csv_path)
                print(f"Successfully read CSV file with {len(df)} rows")
            except Exception as e:
                print(f"Error reading CSV file: {str(e)}")
                raise
        else:
            print("No data files found, returning empty DataFrame")
            return empty_df

        # Clean and format the data
        print("Cleaning data...")
        df = clean_salary_data(df)
        print(f"Successfully loaded and cleaned {len(df)} rows of data")
        print("Columns in final DataFrame:", df.columns.tolist())
        return df
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        import traceback
        print("Full traceback:")
        print(traceback.format_exc())
        return empty_df

def save_submission(data):
    """Save new submission to the current data file"""
    # Add submission timestamp
    data['Submission Date'] = pd.Timestamp.now()

    try:
        # Get the absolute path to the data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(current_dir), 'data')
        excel_path = os.path.join(data_dir, 'salary_data.xlsx')
        csv_path = os.path.join(data_dir, 'salary_data.csv')

        df = load_data()
        new_row = pd.DataFrame([data])

        # If Excel file exists, append to it
        if os.path.exists(excel_path):
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_excel(excel_path, index=False)
        else:
            # Otherwise, append to CSV
            if os.path.exists(csv_path):
                df = pd.concat([df, new_row], ignore_index=True)
            else:
                df = new_row
            df.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving submission: {str(e)}")
        return False

def save_uploaded_file(df):
    """Save uploaded Excel file data"""
    try:
        # Get the absolute path to the data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(current_dir), 'data')
        excel_path = os.path.join(data_dir, 'salary_data.xlsx')
        csv_path = os.path.join(data_dir, 'salary_data.csv')

        # Add submission timestamp for new entries if column doesn't exist
        if 'Submission Date' not in df.columns:
            df['Submission Date'] = pd.Timestamp.now()

        # Clean data before saving
        df = clean_salary_data(df)
        # Save to both Excel and CSV for backup
        df.to_excel(excel_path, index=False)
        df.to_csv(csv_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving uploaded file: {str(e)}")
        return False