from flask import Blueprint, jsonify, session
from datetime import date
from psycopg2.extras import RealDictCursor
from db import get_db, put_db

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard-data", methods=["GET"])
def dashboard_data():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # 1. Total Income
    cursor.execute("""
        SELECT SUM(amount) AS total_income
        FROM transactions WHERE user_id=%s AND type='Income'
    """, (user_id,))
    total_income = cursor.fetchone()["total_income"] or 0

    # 2. Total Expense
    cursor.execute("""
        SELECT SUM(amount) AS total_expense
        FROM transactions WHERE user_id=%s AND type='Expense'
    """, (user_id,))
    total_expense = cursor.fetchone()["total_expense"] or 0

    # 3. Balance
    balance = total_income - total_expense

    # 4. Monthly Budget
    cursor.execute("""
        SELECT amount
        FROM budget
        WHERE user_id=%s
          AND month=EXTRACT(MONTH FROM CURRENT_DATE)
          AND year=EXTRACT(YEAR FROM CURRENT_DATE)
    """, (user_id,))
    result = cursor.fetchone()
    budget = result["amount"] if result else 0

    # 5. Spending This Month
    cursor.execute("""
        SELECT SUM(amount) AS spent
        FROM transactions
        WHERE user_id=%s
        AND type='Expense'
        AND EXTRACT(MONTH FROM date)=EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM date)=EXTRACT(YEAR FROM CURRENT_DATE)
    """, (user_id,))
    spent = cursor.fetchone()["spent"] or 0

    # 6. Budget Usage %
    budget_percent = (spent / budget * 100) if budget > 0 else 0

    # 7. Recent Transactions
    cursor.execute("""
        SELECT title, category, amount, date, type
        FROM transactions
        WHERE user_id=%s
        ORDER BY date DESC LIMIT 5
    """, (user_id,))
    recent = cursor.fetchall()

    cursor.close()
    put_db(conn)

    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "budget_total": budget,
        "budget_spent": spent,
        "budget_used_percent": round(budget_percent, 2),
        "recent_transactions": recent
    })


@dashboard_bp.route("/dashboard-charts", methods=["GET"])
def dashboard_charts():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Monthly totals for every month of the current year
    today = date.today()
    current_year = today.year

    cursor.execute("""
        SELECT EXTRACT(MONTH FROM date) AS month,
               type,
               SUM(amount) AS total
        FROM transactions
        WHERE user_id=%s
          AND EXTRACT(YEAR FROM date)=%s
        GROUP BY EXTRACT(MONTH FROM date), type
        ORDER BY month
    """, (user_id, current_year))
    monthly_rows = cursor.fetchall()

    months = list(range(1, 13))
    labels = [date(current_year, month, 1).strftime("%b") for month in months]

    income_map = {month: 0 for month in months}
    expense_map = {month: 0 for month in months}

    for row in monthly_rows:
        month = row.get("month")
        total = float(row.get("total") or 0)
        t_type = str(row.get("type") or "").lower()
        if month in income_map and t_type == "income":
            income_map[month] = total
        if month in expense_map and t_type == "expense":
            expense_map[month] = total

    income_data = [income_map[month] for month in months]
    expense_data = [expense_map[month] for month in months]

    # Expense categories for current month
    cursor.execute("""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE user_id=%s
          AND type='Expense'
          AND EXTRACT(MONTH FROM date)=EXTRACT(MONTH FROM CURRENT_DATE)
          AND EXTRACT(YEAR FROM date)=EXTRACT(YEAR FROM CURRENT_DATE)
        GROUP BY category
        ORDER BY total DESC
        LIMIT 6
    """, (user_id,))
    category_rows = cursor.fetchall()

    category_total = 0
    categories = []
    for row in category_rows:
        total = float(row.get("total") or 0)
        category_total += total
        categories.append({
            "category": row.get("category") or "Uncategorized",
            "total": total
        })

    cursor.close()
    put_db(conn)

    return jsonify({
        "months": labels,
        "income": income_data,
        "expense": expense_data,
        "categories": categories,
        "category_total": category_total
    })
