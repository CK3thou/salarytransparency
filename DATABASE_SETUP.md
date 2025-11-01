# Data Storage Notes

This project no longer uses a database. All data is stored in a single CSV file:

- Primary dataset (single source of truth): `data/new_salary.csv`
- New submissions are appended to this file by the app.
- The app reads from this file on startup to power charts and tables.

If `data/new_salary.csv` is missing, the app will create it with the proper header automatically.

Legacy database setup and migration scripts have been deprecated and removed. No further database configuration is required.

