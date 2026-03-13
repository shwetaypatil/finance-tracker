from flask import Blueprint, request, jsonify, session
import bcrypt
from db import get_db
import mysql.connector

auth_bp = Blueprint("auth", __name__)

# ---------------- SIGNUP ----------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json or {}
    username = data.get("username")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    password = data.get("password")
    confirm = data.get("confirm")

    if not all([username, first_name, last_name, email, password, confirm]):
        return jsonify({"success": False, "msg": "All fields required"})

    if password != confirm:
        return jsonify({"success": False, "msg": "Passwords do not match"})

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    conn = get_db()
    if conn is None:
        return jsonify({"success": False, "msg": "Database connection failed"}), 500
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (username, first_name, last_name, email, password)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, first_name, last_name, email, hashed))

        user_id = cursor.lastrowid

        # Create default settings
        cursor.execute("""
            INSERT INTO user_settings (user_id)
            VALUES (%s)
        """, (user_id,))

        conn.commit()
        return jsonify({"success": True})

    except mysql.connector.Error as err:
        if err.errno == 1062:
            return jsonify({"success": False, "msg": "User already exists"})
        return jsonify({"success": False, "msg": str(err)})

    finally:
        cursor.close()
        conn.close()


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email")
    password = data.get("password")

    conn = get_db()
    if conn is None:
        return jsonify({"success": False, "msg": "Database connection failed"}), 500
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user:
        return jsonify({"success": False, "msg": "User not found"})

    stored_password = user["password"]
    if isinstance(stored_password, str):
        stored_password = stored_password.encode()

    if not bcrypt.checkpw(password.encode(), stored_password):
        return jsonify({"success": False, "msg": "Invalid password"})

    session["user_id"] = user["id"]
    session["username"] = user["username"]

    return jsonify({"success": True})


# ---------------- LOGOUT ----------------
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})
