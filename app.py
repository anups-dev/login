import os
import secrets
import warnings

from flask import Flask, redirect, render_template, request, session, url_for
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
if not os.environ.get("FLASK_SECRET_KEY"):
    warnings.warn(
        "FLASK_SECRET_KEY is not set; sessions will be invalidated when the app restarts.",
        RuntimeWarning,
        stacklevel=2,
    )


def check_credentials(email, password):
    # TODO: replace with real hash check
    return email == "test@example.com" and password == "password"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        session.clear()

        if email and password and check_credentials(email, password):
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

    return "Welcome"

