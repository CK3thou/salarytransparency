# Database Setup Guide

This application uses PostgreSQL to store salary data. Follow these steps to set up the database.

## Prerequisites

1. Install PostgreSQL on your system:
   - Windows: Download from https://www.postgresql.org/download/windows/
   - macOS: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql` (Ubuntu/Debian)

2. Ensure PostgreSQL is running on your system.

## Setup Steps

### 1. Create Environment File

Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

### 2. Configure Database Credentials

Edit the `.env` file with your PostgreSQL credentials:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=salary_transparency
DB_USER=postgres
DB_PASSWORD=your_postgres_password
```

### 3. Install Python Dependencies

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 4. Migrate CSV Data to Database

Run the migration script to import existing CSV data into PostgreSQL:
```bash
python migrate_csv_to_db.py
```

This script will:
- Create the database if it doesn't exist
- Create the necessary tables
- Import all data from `data/salary_data.csv`

### 5. Run the Application

Start the Streamlit application:
```bash
streamlit run main.py
```

The application will automatically:
- Connect to PostgreSQL on startup
- Load data from the database
- Save all new submissions to the database

## Database Schema

The `salary_data` table includes:
- `id`: Primary key (auto-increment)
- `role`: Job role/title
- `company_location_country`: Company location
- `monthly_gross_salary_zmw`: Monthly salary in ZMW
- `salary_gross_usd`: Salary in USD (optional)
- `years_of_experience`: Years of experience
- `degree`: Whether the person has a degree
- `approx_employees`: Approximate number of employees
- `your_country_location`: Employee's location
- `nationality`: Nationality
- `industry`: Industry sector
- `submission_date`: Timestamp of submission
- `created_at`: Record creation timestamp

## Troubleshooting

### Connection Errors

If you see connection errors:
1. Verify PostgreSQL is running: `pg_isready` or check services
2. Check your `.env` file has correct credentials
3. Ensure the database user has necessary permissions

### Database Already Exists

If the migration script reports the database already exists, you can:
- Continue to add CSV data (it will prompt)
- Drop and recreate: `DROP DATABASE salary_transparency;` (in psql)
- Or let the migration continue if data already exists

### Empty Database

If the app shows no data:
1. Verify the migration script ran successfully
2. Check database connection in `.env`
3. Verify data exists: `SELECT COUNT(*) FROM salary_data;` (in psql)

