from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

from flask import Flask, abort, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("APP_SECRET", "dev-secret-change-me")


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
        """
    )
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS contents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            body TEXT NOT NULL
        )
        """
    )
    db.commit()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def sign_username(username: str) -> str:
    signature = hmac.new(
        app.config["SECRET_KEY"].encode("utf-8"),
        username.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{username}|{signature}"


def verify_auth_cookie(value: str | None) -> str | None:
    if not value or "|" not in value:
        return None

    username, signature = value.split("|", 1)
    expected = hmac.new(
        app.config["SECRET_KEY"].encode("utf-8"),
        username.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None

    user = get_db().execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if user is None:
        return None
    return username


def require_login() -> str:
    username = verify_auth_cookie(request.cookies.get("auth"))
    if username is None:
        abort(401)
    return username


@app.route("/")
def entry() -> str:
    return render_template("entry.html")


@app.route("/register", methods=["GET", "POST"])
def register() -> str:
    error = None

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        if len(username) < 3:
            error = "Username muss mindestens 3 Zeichen lang sein."
        elif len(password) < 3:
            error = "Passwort muss mindestens 3 Zeichen lang sein."
        else:
            db = get_db()
            existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            if existing is not None:
                error = "Username existiert bereits."
            else:
                db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, hash_password(password)),
                )
                db.commit()
                return redirect(url_for("login"))

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    error = None

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        user = get_db().execute(
            "SELECT password_hash FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None or user["password_hash"] != hash_password(password):
            error = "Login fehlgeschlagen."
        else:
            response = redirect(url_for("content"))
            response.set_cookie("auth", sign_username(username), httponly=True, samesite="Lax")
            return response

    return render_template("login.html", error=error)


@app.route("/content")
def content() -> str:
    username = require_login()
    rows = get_db().execute("SELECT id, body FROM contents ORDER BY id DESC").fetchall()
    return render_template("content.html", username=username, contents=rows)


@app.route("/detail/<int:content_id>")
def detail(content_id: int) -> str:
    require_login()
    row = get_db().execute("SELECT id, body FROM contents WHERE id = ?", (content_id,)).fetchone()
    if row is None:
        abort(404)
    return render_template("detail.html", content=row)


@app.route("/create", methods=["GET", "POST"])
def create() -> str:
    require_login()
    error = None

    if request.method == "POST":
        text = (request.form.get("text") or "").strip()
        if len(text) < 1024:
            error = "Text muss mindestens 1024 Zeichen enthalten."
        else:
            db = get_db()
            db.execute("INSERT INTO contents (body) VALUES (?)", (text,))
            db.commit()
            return redirect(url_for("content"))

    return render_template("create.html", error=error)


@app.route("/logout")
def logout() -> str:
    response = redirect(url_for("entry"))
    response.set_cookie("auth", "", expires=0)
    return response


@app.errorhandler(401)
def unauthorized(_error):
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
