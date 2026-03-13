# import mysql.connector

# def get_db():
#     connection = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="",         # default XAMPP
#         database="finance_tracker"
#     )
#     return connection


import mysql.connector

def get_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # default XAMPP password is empty
            database="finance_tracker"
        )
        print("Database connection successful!")
        return connection
    except mysql.connector.Error as err:
        print("Error connecting to MySQL:", err)
        return None
