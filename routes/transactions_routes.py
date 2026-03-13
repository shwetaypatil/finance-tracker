from flask import Blueprint, request, jsonify, session
from db import get_db

transactions_bp = Blueprint("transactions", __name__)

# ---------------- GET ALL TRANSACTIONS ----------------
@transactions_bp.route("/api/transactions", methods=["GET"])
def get_transactions():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    search = request.args.get("search", "")
    t_type = request.args.get("type", "")
    date_from = request.args.get("from", "")
    date_to = request.args.get("to", "")
    page = request.args.get("page", "1")
    page_size = request.args.get("page_size", "10")

    try:
        page = max(1, int(page))
    except (TypeError, ValueError):
        page = 1
    try:
        page_size = max(1, min(100, int(page_size)))
    except (TypeError, ValueError):
        page_size = 10

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(dictionary=True)

    base_query = "FROM transactions WHERE user_id = %s"
    params = [user_id]

    if search:
        base_query += " AND (title LIKE %s OR category LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    if t_type:
        base_query += " AND type = %s"
        params.append(t_type)

    if date_from:
        base_query += " AND date >= %s"
        params.append(date_from)

    if date_to:
        base_query += " AND date <= %s"
        params.append(date_to)

    count_query = "SELECT COUNT(*) AS total " + base_query
    cur.execute(count_query, params)
    total = cur.fetchone()["total"] or 0

    offset = (page - 1) * page_size
    data_query = """
        SELECT id, title, category, amount, type, date
    """ + base_query + " ORDER BY date DESC LIMIT %s OFFSET %s"
    data_params = params + [page_size, offset]
    cur.execute(data_query, data_params)
    rows = cur.fetchall()

    # Monthly summary for current month
    cur.execute("""
        SELECT
            SUM(CASE WHEN LOWER(type)='income' THEN amount ELSE 0 END) AS income,
            SUM(CASE WHEN LOWER(type)='expense' THEN amount ELSE 0 END) AS expense
        FROM transactions
        WHERE user_id = %s
          AND MONTH(date) = MONTH(CURDATE())
          AND YEAR(date) = YEAR(CURDATE())
    """, (user_id,))
    summary_row = cur.fetchone() or {}
    income = float(summary_row.get("income") or 0)
    expense = float(summary_row.get("expense") or 0)

    cur.close()
    conn.close()

    return jsonify({
        "transactions": rows,
        "total": total,
        "page": page,
        "page_size": page_size,
        "month_summary": {
            "income": income,
            "expense": expense,
            "balance": income - expense
        }
    })


# ---------------- ADD TRANSACTION ----------------
@transactions_bp.route("/transactions/add", methods=["POST"])
def add_transaction():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    data = request.json or {}

    required = ["title", "category", "amount", "type", "date"]
    missing = [
        k for k in required
        if k not in data or data[k] is None or (isinstance(data[k], str) and data[k].strip() == "")
    ]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor()

    cur.execute("""
        INSERT INTO transactions
        (user_id, title, category, amount, type, date, note)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        data["title"],
        data["category"],
        data["amount"],
        data["type"],
        data["date"],
        data.get("notes") or data.get("note", "")
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Transaction added successfully!"})


# ---------------- GET SINGLE TRANSACTION ----------------
@transactions_bp.route("/transactions/<int:id>", methods=["GET"])
def get_single_transaction(id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM transactions WHERE id = %s AND user_id = %s",
        (id, user_id)
    )
    row = cur.fetchone()

    cur.close()
    conn.close()

    return jsonify(row)


# ---------------- UPDATE TRANSACTION ----------------
@transactions_bp.route("/transactions/update/<int:id>", methods=["PUT"])
def update_transaction(id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]
    data = request.json or {}

    required = ["title", "category", "amount", "type", "date"]
    missing = [
        k for k in required
        if k not in data or data[k] is None or (isinstance(data[k], str) and data[k].strip() == "")
    ]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor()

    cur.execute("""
        UPDATE transactions
        SET title=%s, category=%s, amount=%s, type=%s, date=%s, note=%s
        WHERE id=%s AND user_id=%s
    """, (
        data["title"],
        data["category"],
        data["amount"],
        data["type"],
        data["date"],
        data.get("notes") or data.get("note", ""),
        id,
        user_id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Transaction updated!"})


# ---------------- DELETE TRANSACTION ----------------
@transactions_bp.route("/api/transactions/<int:id>", methods=["DELETE"])
def delete_transaction(id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = session["user_id"]

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM transactions WHERE id=%s AND user_id=%s",
        (id, user_id)
    )
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"message": "Transaction deleted successfully!"})
