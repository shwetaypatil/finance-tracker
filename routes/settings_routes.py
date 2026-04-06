from flask import Blueprint, request, jsonify, send_file, session
import csv
import io
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from db import get_db, put_db

settings_bp = Blueprint("settings", __name__)

# CHANGE TO DARK OR LIGHT MODE
@settings_bp.route("/api/settings/theme", methods=["POST"])
def update_theme():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    theme = request.json.get("theme")   # 'light' or 'dark'

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET theme = %s WHERE id = %s", (theme, user_id))
    conn.commit()
    put_db(conn)

    return jsonify({"status": "success", "message": "Theme updated"})


# -----------------------------
# 1️⃣ UPDATE LANGUAGE
# -----------------------------
@settings_bp.route("/api/settings/language", methods=["POST"])
def update_language():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    language = request.json.get("language")   # 'en', 'hi', etc.

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = %s WHERE id = %s", (language, user_id))
    conn.commit()
    put_db(conn)

    return jsonify({"status": "success", "message": "Language updated"})


# -----------------------------
# GET USER PREFERENCES (THEME, LANGUAGE, REPORT FILTERS)
# -----------------------------
@settings_bp.route("/api/settings/preferences", methods=["GET"])
def get_preferences():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    now = datetime.now()
    defaults = {
        "theme": "light",
        "language": "en",
        "report_period": "monthly",
        "report_month": now.month,
        "report_year": now.year
    }

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cursor.execute(
            "SELECT theme, language, report_period, report_month, report_year FROM users WHERE id=%s",
            (user_id,)
        )
        row = cursor.fetchone() or {}
        prefs = defaults.copy()
        for key in prefs.keys():
            if row.get(key) is not None:
                prefs[key] = row.get(key)
        return jsonify(prefs)
    except psycopg2.Error:
        # Fallback if report_* columns are missing
        try:
            cursor.execute(
                "SELECT theme, language FROM users WHERE id=%s",
                (user_id,)
            )
            row = cursor.fetchone() or {}
            prefs = defaults.copy()
            if row.get("theme") is not None:
                prefs["theme"] = row.get("theme")
            if row.get("language") is not None:
                prefs["language"] = row.get("language")
            return jsonify(prefs)
        except psycopg2.Error:
            return jsonify(defaults)
    finally:
        cursor.close()
        put_db(conn)


# -----------------------------
# UPDATE REPORT FILTERS (PER-USER)
# -----------------------------
@settings_bp.route("/api/settings/report", methods=["POST"])
def update_report_preferences():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    period = (data.get("period") or "monthly").lower()
    month = data.get("month")
    year = data.get("year")

    try:
        month = int(month)
        year = int(year)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid month/year"}), 400

    if month < 1 or month > 12:
        return jsonify({"error": "Month must be between 1 and 12"}), 400
    if year < 1970 or year > 2100:
        return jsonify({"error": "Year out of range"}), 400

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE users
            SET report_period = %s, report_month = %s, report_year = %s
            WHERE id = %s
            """,
            (period, month, year, user_id)
        )
        conn.commit()
        return jsonify({"status": "success"})
    except psycopg2.Error:
        return jsonify({"error": "Report preference columns missing in users table"}), 501
    finally:
        cursor.close()
        put_db(conn)


# -----------------------------
# 2️⃣ EXPORT TRANSACTIONS AS CSV
# -----------------------------
@settings_bp.route("/api/settings/export_csv", methods=["GET"])
def export_csv():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    cursor.execute("""
        SELECT title, category, amount, date, type
        FROM transactions 
        WHERE user_id = %s
        ORDER BY date DESC
    """, (user_id, ))

    rows = cursor.fetchall()
    put_db(conn)

    # Convert to CSV (memory)
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Title", "Category", "Amount", "Date", "Type"])
    for r in rows:
        writer.writerow([r["title"], r["category"], r["amount"], r["date"], r["type"]])

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name="transactions_export.csv"
    )


# -----------------------------
# 3️⃣ DELETE ALL TRANSACTIONS
# -----------------------------
@settings_bp.route("/api/settings/delete_all", methods=["DELETE"])
def delete_all_transactions():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transactions WHERE user_id = %s", (user_id,))
    conn.commit()
    put_db(conn)

    return jsonify({"status": "success", "message": "All transactions deleted."})


# # -----------------------------
# # 4️⃣ LOGOUT
# # -----------------------------
# @settings_bp.route("/api/logout", methods=["POST"])
# def logout():
#     # You will destroy the session cookie here (later)
#     return jsonify({"status": "success", "message": "Logged out successfully"})
