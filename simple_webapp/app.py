from __future__ import annotations

import os

import psycopg
from psycopg.rows import dict_row
from flask import Flask, abort, g, redirect, render_template, request, url_for

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://appuser:DeinStarkesPasswort@localhost:5432/appdb",
)

app = Flask(__name__)


@app.context_processor
def inject_cookie() -> dict[str, str | None]:
    return {"cookie": request.cookies.get("name")}


def get_db() -> psycopg.Connection:
    if "db" not in g:
        g.db = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return g.db


@app.teardown_appcontext
def close_db(exc: Exception | None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                username VARCHAR(150) NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS contents (
                id BIGSERIAL PRIMARY KEY,
                body TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    db.commit()


def require_login() -> str:
    username = request.cookies.get("name")
    if not username:
        abort(401)

    with get_db().cursor() as cur:
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
    if user is None:
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
            with db.cursor() as cur:
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                existing = cur.fetchone()
                if existing is not None:
                    error = "Username existiert bereits."
                else:
                    cur.execute(
                        "INSERT INTO users (username, password) VALUES (%s, %s)",
                        (username, password),
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

        with get_db().cursor() as cur:
            cur.execute(
                "SELECT id FROM users WHERE username = %s AND password = %s",
                (username, password),
            )
            user = cur.fetchone()

        if user is None:
            error = "Login fehlgeschlagen."
        else:
            response = redirect(url_for("content"))
            response.set_cookie("name", username)
            return response

    return render_template("login.html", error=error)


@app.route("/content")
def content() -> str:
    username = require_login()
    with get_db().cursor() as cur:
        cur.execute(
            "SELECT id, body FROM contents WHERE char_length(body) >= 1024 ORDER BY id DESC"
        )
        rows = cur.fetchall()
    return render_template("content.html", username=username, contents=rows)


@app.route("/detail/<int:content_id>")
def detail(content_id: int) -> str:
    require_login()
    with get_db().cursor() as cur:
        cur.execute(
            "SELECT id, body FROM contents WHERE id = %s AND char_length(body) >= 1024",
            (content_id,),
        )
        row = cur.fetchone()
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
            with db.cursor() as cur:
                cur.execute("INSERT INTO contents (body) VALUES (%s)", (text,))
            db.commit()
            return redirect(url_for("content"))

    return render_template("create.html", error=error)


@app.route("/logout")
def logout() -> str:
    response = redirect(url_for("entry"))
    response.set_cookie("name", "", expires=0)
    return response


@app.errorhandler(401)
def unauthorized(_error):
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
