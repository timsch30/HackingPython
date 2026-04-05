from __future__ import annotations

import os
from typing import Any

from flask import Flask, abort, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://appuser:3215@localhost:5432/Local_Postgres_Hacking_Python_PW_3215"
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemy wird als Flask-Erweiterung genutzt (wie im gewünschten Stil).
db = SQLAlchemy(app)


@app.context_processor
def inject_cookie() -> dict[str, str | None]:
    return {"cookie": request.cookies.get("name")}


def init_db() -> None:
    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS users (
                id BIGSERIAL PRIMARY KEY,
                username VARCHAR(150) NOT NULL UNIQUE,
                password TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS contents (
                id BIGSERIAL PRIMARY KEY,
                body TEXT NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
    )
    db.session.commit()


def require_login() -> str:
    username = request.cookies.get("name")
    if not username:
        abort(401)

    user = (
        db.session.execute(
            text("SELECT id FROM users WHERE username = :username"),
            {"username": username},
        )
        .mappings()
        .first()
    )
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
            existing = (
                db.session.execute(
                    text("SELECT id FROM users WHERE username = :username"),
                    {"username": username},
                )
                .mappings()
                .first()
            )
            if existing is not None:
                error = "Username existiert bereits."
            else:
                db.session.execute(
                    text("INSERT INTO users (username, password) VALUES (:username, :password)"),
                    {"username": username, "password": password},
                )
                db.session.commit()
                return redirect(url_for("login"))

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    error = None

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        user = (
            db.session.execute(
                text(
                    "SELECT id FROM users WHERE username = :username AND password = :password"
                ),
                {"username": username, "password": password},
            )
            .mappings()
            .first()
        )

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
    rows: list[dict[str, Any]] = (
        db.session.execute(
            text(
                "SELECT id, body FROM contents WHERE char_length(body) >= 1024 ORDER BY id DESC"
            )
        )
        .mappings()
        .all()
    )
    return render_template("content.html", username=username, contents=rows)


@app.route("/detail/<int:content_id>")
def detail(content_id: int) -> str:
    require_login()
    row = (
        db.session.execute(
            text(
                "SELECT id, body FROM contents WHERE id = :content_id AND char_length(body) >= 1024"
            ),
            {"content_id": content_id},
        )
        .mappings()
        .first()
    )

    if row is None:
        abort(404)
    return render_template("detail.html", content=row)


@app.route("/create", methods=["GET", "POST"])
def create() -> str:
    require_login()
    error = None

    if request.method == "POST":
        text_value = (request.form.get("text") or "").strip()
        if len(text_value) < 1024:
            error = "Text muss mindestens 1024 Zeichen enthalten."
        else:
            db.session.execute(
                text("INSERT INTO contents (body) VALUES (:body)"),
                {"body": text_value},
            )
            db.session.commit()
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
