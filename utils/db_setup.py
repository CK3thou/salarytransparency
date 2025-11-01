"""Database setup and connection utilities for PostgreSQL"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_db_config():
    """Get database configuration from environment variables"""
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'salary_transparency'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'postgres')
    }

def create_database():
    """Create the database if it doesn't exist"""
    config = get_db_config()
    db_name = config.pop('database')
    
    # Connect to postgres database to create new database
    config_temp = config.copy()
    config_temp['database'] = 'postgres'
    
    try:
        conn = psycopg2.connect(**config_temp)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        return False

def create_tables():
    """Create the salary_data table if it doesn't exist"""
    config = get_db_config()
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS salary_data (
            id SERIAL PRIMARY KEY,
            role VARCHAR(255),
            company_location_country VARCHAR(255),
            monthly_gross_salary_zmw NUMERIC(12, 2),
            salary_gross_usd NUMERIC(12, 2),
            years_of_experience NUMERIC(5, 1),
            degree VARCHAR(10),
            approx_employees VARCHAR(100),
            your_country_location VARCHAR(255),
            nationality VARCHAR(255),
            industry VARCHAR(255),
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_company_location ON salary_data(company_location_country);
        CREATE INDEX IF NOT EXISTS idx_submission_date ON salary_data(submission_date);
        CREATE INDEX IF NOT EXISTS idx_industry ON salary_data(industry);
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()
        conn.close()
        print("Tables created successfully.")
        return True
    except Exception as e:
        print(f"Error creating tables: {str(e)}")
        return False

def get_db_engine():
    """Get SQLAlchemy engine for database operations"""
    config = get_db_config()
    connection_string = (
        f"postgresql://{config['user']}:{config['password']}@"
        f"{config['host']}:{config['port']}/{config['database']}"
    )
    return create_engine(connection_string)

def setup_database():
    """Complete database setup: create database and tables"""
    print("Setting up database...")
    if create_database():
        if create_tables():
            print("Database setup completed successfully!")
            return True
    return False

