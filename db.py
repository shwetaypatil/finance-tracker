from psycopg2 import pool
import os

db_pool = pool.SimpleConnectionPool(
    1, 10,
    os.environ.get("DATABASE_URL"),
    sslmode="require"
)

def get_db():
    return db_pool.getconn()

def put_db(conn):
    db_pool.putconn(conn)