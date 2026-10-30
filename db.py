from psycopg2 import pool
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from environment variables")

db_pool = pool.SimpleConnectionPool(
    1, 10,
    DATABASE_URL,
    sslmode="require"
)

def get_db():
    return db_pool.getconn()

def put_db(conn):
    db_pool.putconn(conn)