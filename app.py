from flask import Flask, jsonify, session, render_template, request, redirect, url_for
from flask_cors import CORS
from models.user_model import get_user_by_id

from routes.dashboard_routes import dashboard_bp
from routes.transactions_routes import transactions_bp
from routes.budget_routes import budget_bp
from routes.settings_routes import settings_bp
from routes.auth_routes import auth_bp
from routes.report_routes import report_bp
from routes.profile_routes import profile_bp

app = Flask(__name__)
app.secret_key = "super_secret_key_123"   # move to .env later
CORS(app, supports_credentials=True)

# -----------------------------
# REGISTER BLUEPRINTS
# -----------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(budget_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(report_bp)
app.register_blueprint(profile_bp)

@app.context_processor
def inject_user():
    if "user_id" in session:
        user = get_user_by_id(session["user_id"])
        return dict(current_user=user)
    return dict(current_user=None)

# -----------------------------
# FRONTEND ROUTES
# -----------------------------
@app.route("/")
def login_page():
    return render_template("login_page.html")

@app.route("/signup")
def signup_page():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")

@app.route("/transactions")
def transactions_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("alltransactions.html")

@app.route("/addtransaction")
def add_transaction_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))

    txn_type = request.args.get("type")  # income / expense
    return render_template("addtransaction.html", type=txn_type)

@app.route("/edittransaction")
def edit_transaction_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    
    return render_template("edittransaction.html")

@app.route("/budget")
def budget_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("budget.html")

@app.route("/report")
def report_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("report.html")

@app.route("/profile")
def profile_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("profile.html")

@app.route("/settings")
def settings_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("settings.html")

# -----------------------------
# SESSION CHECK
# -----------------------------
@app.route("/session-check")
def check_session():
    if "user_id" in session:
        return jsonify({
            "logged_in": True,
            "username": session.get("username")
        })
    return jsonify({"logged_in": False})

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
