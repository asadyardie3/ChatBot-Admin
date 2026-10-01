import os
from functools import wraps

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

import db
from bot import process

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
db.init_db()


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "email" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"reply": "Please log in."}), 401
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return redirect(url_for("chat" if "email" in session else "login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        if db.find_by_email(email):
            session["email"] = email
            return redirect(url_for("chat"))
        error = "This email is not registered. Access denied."
    return render_template("login.html", error=error)


@app.route("/chat")
@login_required
def chat():
    return render_template("chat.html", email=session["email"])


@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"reply": "Please type a command."})
    return jsonify({"reply": process(message, session["email"])})


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)