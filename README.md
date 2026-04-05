# Personal Finance Tracker

Flask-based personal finance tracker with PostgreSQL as the database.

## Prerequisites
- Python 3.10+
- PostgreSQL 13+

## Setup
1. Create a virtual environment and install dependencies:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a PostgreSQL database (example name: `finance_tracker`).

3. Set the `DATABASE_URL` environment variable:
```
set DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<db_name>
```

4. Initialize the schema and seed data:
```
psql -d finance_tracker -f finance_tracker.sql
```

5. Run the app:
```
python app.py
```

## Notes
- `db.py` uses `DATABASE_URL` and connects with `psycopg2`.
- The schema and seed data live in `finance_tracker.sql`.
- If you change the database, re-run the SQL file to recreate tables.

