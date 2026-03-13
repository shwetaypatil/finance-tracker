from db import get_db   # use the same mysql object you already use
import mysql.connector

def get_user_by_id(user_id):
    connection = get_db()
    if connection is None:
        return None
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, username, email, first_name, last_name FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
    except mysql.connector.Error:
        cursor.execute(
            "SELECT id, username, email FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user
