from db import get_db
import psycopg2
from psycopg2.extras import RealDictCursor

def get_user_by_id(user_id):
    connection = get_db()
    if connection is None:
        return None
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT id, username, email, first_name, last_name FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
    except psycopg2.Error:
        cursor.execute(
            "SELECT id, username, email FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user
