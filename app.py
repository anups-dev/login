from contextlib import closing
from datetime import timedelta
import os
from pathlib import Path
import secrets
import sqlite3
import warnings

from argon2 import PasswordHasher
from flask import (
    Flask,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

app = Flask(__name__)
DATABASE_PATH = Path(__file__).with_name("users.db")
password_hasher = PasswordHasher()
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get(
    "SESSION_COOKIE_SECURE", "false"
).strip().lower() in {"1", "true", "yes", "on"}
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)
if not os.environ.get("FLASK_SECRET_KEY"):
    warnings.warn(
        "FLASK_SECRET_KEY is not set; sessions will be invalidated when the app restarts.",
        RuntimeWarning,
        stacklevel=2,
    )


def create_users_table():
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )


def get_user_by_email(email):
    normalized_email = email.strip().lower()
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        connection.row_factory = sqlite3.Row
        return connection.execute(
            "SELECT id, email, password_hash, created_at FROM users WHERE email = ?",
            (normalized_email,),
        ).fetchone()


def create_user(email, password):
    normalized_email = email.strip().lower()
    password_hash = password_hasher.hash(password)
    with closing(sqlite3.connect(DATABASE_PATH)) as connection:
        with connection:
            cursor = connection.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (normalized_email, password_hash),
            )
            return cursor.lastrowid


create_users_table()


def check_credentials(email, password):
    # TODO: replace with real hash check
    return email == "test@example.com" and password == "password"


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_email" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if email and password and check_credentials(email, password):
            session.clear()
            session.permanent = True
            session["user_email"] = email
            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password.",
            email=email,
        )

    return render_template("login.html", email="")


@app.route("/dashboard")
def dashboard():
    if "user_email" not in session:
        return redirect(url_for("login"))

    response = make_response(render_template("dashboard.html"))
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))
