from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import Flask, abort, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"

app = Flask(__name__)


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc: Exception | None) -> None:
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
            password TEXT NOT NULL
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


@app.before_request
def ensure_db() -> None:
    init_db()


def get_logged_in_user() -> str | None:
    username = request.cookies.get("name")
    if not username:
        return None

    user = get_db().execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if user is None:
        return None

    return username


def require_login() -> str:
    username = get_logged_in_user()
    if username is None:
        abort(401)
    return username


@app.route("/")
def entry() -> str:
    cookie = get_logged_in_user()
    return render_template("entry.html", cookie=cookie)


@app.route("/register", methods=["GET", "POST"])
def register() -> str:
    error = None
    cookie = get_logged_in_user()

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
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password),
                )
                db.commit()
                return redirect(url_for("login"))

    return render_template("register.html", error=error, cookie=cookie)


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    error = None
    cookie = get_logged_in_user()

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        user = get_db().execute(
            "SELECT id FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()

        if user is None:
            error = "Login fehlgeschlagen."
        else:
            response = redirect(url_for("content"))
            response.set_cookie("name", username)
            return response

    return render_template("login.html", error=error, cookie=cookie)


@app.route("/content")
def content() -> str:
    username = require_login()
    rows = get_db().execute("SELECT id, body FROM contents ORDER BY id DESC").fetchall()
    return render_template("content.html", username=username, contents=rows, cookie=username)


@app.route("/detail/<int:content_id>")
def detail(content_id: int) -> str:
    username = require_login()
    row = get_db().execute(
        "SELECT id, body FROM contents WHERE id = ? AND length(body) >= 1024",
        (content_id,),
    ).fetchone()
    if row is None:
        abort(404)
    return render_template("detail.html", content=row, cookie=username)


@app.route("/create", methods=["GET", "POST"])
def create() -> str:
    username = require_login()
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

    return render_template("create.html", error=error, cookie=username)


@app.route("/logout")
def logout() -> str:
    response = redirect(url_for("entry"))
    response.set_cookie("name", "", expires=0)
    return response


@app.errorhandler(401)
def unauthorized(_error):
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
