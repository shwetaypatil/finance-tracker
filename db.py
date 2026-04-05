# import psycopg2
# import os

# def get_db():
#     try:
#         connection = psycopg2.connect(
#             os.environ.get("DATABASE_URL"),
#             sslmode="require"
#         )
#         print("Database connection successful!")
#         return connection
#     except Exception as err:
#         print("Error connecting to PostgreSQL:", err)
#         return None

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