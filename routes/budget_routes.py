from flask import Blueprint, request, jsonify, session
from datetime import datetime
from psycopg2.extras import RealDictCursor
from db import get_db, put_db

budget_bp = Blueprint("budget", __name__)

# save budget
@budget_bp.route("/api/budget", methods=["POST"])
def save_budget():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    amount = data.get("amount")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = None

    if amount is None or amount <= 0:
        return jsonify({"error": "Invalid budget amount"}), 400

    user_id = session["user_id"]
    month = datetime.now().month
    year = datetime.now().year

    db = get_db()
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute(
            "SELECT id FROM budget WHERE user_id=%s AND month=%s AND year=%s",
            (user_id, month, year)
        )
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE budget SET amount=%s WHERE id=%s",
                (amount, existing["id"])
            )
        else:
            cursor.execute(
                """INSERT INTO budget (user_id, month, year, amount)
                   VALUES (%s, %s, %s, %s)""",
                (user_id, month, year, amount)
            )

        db.commit()
    finally:
        cursor.close()
        put_db(db)

    return jsonify({"success": True})

# get budget of the current month
@budget_bp.route("/api/budget/current", methods=["GET"])
def get_current_budget():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    month = datetime.now().month
    year = datetime.now().year

    db = get_db()
    if db is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        # Get user's total budget
        cursor.execute(
            "SELECT amount FROM budget WHERE user_id = %s AND month = %s AND year = %s",
            (user_id, month, year)
        )
        budget = cursor.fetchone()

        if not budget:
            return jsonify({
                "amount": 0,
                "used": 0,
                "remaining": 0,
                "percent": 0
            })

        amount = float(budget["amount"])

        # Get amount used (sum of expense transactions)
        cursor.execute(
            """SELECT SUM(amount) AS total 
               FROM transactions 
               WHERE user_id = %s AND type='Expense'
               AND EXTRACT(MONTH FROM date) = %s AND EXTRACT(YEAR FROM date) = %s""",
            (user_id, month, year)
        )
        result = cursor.fetchone()
        used = float(result["total"]) if result["total"] else 0

        remaining = amount - used
        percent = (used / amount) * 100 if amount > 0 else 0

        return jsonify({
            "amount": amount,
            "used": used,
            "remaining": remaining,
            "percent": percent
        })
    finally:
        cursor.close()
        put_db(db)
