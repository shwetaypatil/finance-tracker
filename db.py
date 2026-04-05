import psycopg2
import os

def get_db():
    try:
        connection = psycopg2.connect(
            os.environ.get("DATABASE_URL")
        )
        print("Database connection successful!")
        return connection
    except Exception as err:
        print("Error connecting to PostgreSQL:", err)
        return None