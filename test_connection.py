from db import get_db

connection = get_db()

if connection:
    cursor = connection.cursor()
    cursor.execute("SELECT current_database();")
    result = cursor.fetchone()
    print("Connected to database:", result[0])

    cursor.close()
    connection.close()
else:
    print("Connection failed.")
