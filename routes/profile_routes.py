from flask import Blueprint, request, jsonify, session
from db import get_db, put_db

profile_bp = Blueprint("profile", __name__)


def _is_name_valid(name):
    if not name:
        return False
    if len(name) < 2:
        return False
    return name.replace(" ", "").isalpha()


@profile_bp.route("/api/profile/personal", methods=["POST"])
def update_personal_info():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json or {}
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()

    if not _is_name_valid(first_name) or not _is_name_valid(last_name):
        return jsonify({"error": "Invalid first or last name"}), 400

    conn = get_db()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET first_name = %s, last_name = %s WHERE id = %s",
        (first_name, last_name, user_id)
    )
    conn.commit()
    cursor.close()
    put_db(conn)

    return jsonify({"success": True})
