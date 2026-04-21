from __future__ import annotations

from typing import Any

from flask import abort, redirect, render_template, request, url_for
from sqlalchemy import text

from . import app, db


@app.context_processor
def inject_current_user() -> dict[str, str | None]:
    return {"current_user": get_logged_in_username()}


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
    db.session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS auth_state (
                id BIGINT PRIMARY KEY,
                username VARCHAR(150)
            )
            """
        )
    )
    db.session.execute(
        text(
            """
            INSERT INTO auth_state (id, username)
            VALUES (1, NULL)
            ON CONFLICT (id) DO NOTHING
            """
        )
    )
    db.session.commit()


def get_logged_in_username() -> str | None:
    row = (
        db.session.execute(
            text("SELECT username FROM auth_state WHERE id = 1")
        )
        .mappings()
        .first()
    )
    if row is None:
        return None
    return row["username"]


def require_login() -> str:
    username = get_logged_in_username()
    if not username:
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
        password_confirm = request.form.get("password_confirm") or ""

        if not username:
            error = "Username darf nicht leer sein."
        elif not password:
            error = "Passwort darf nicht leer sein."
        elif password != password_confirm:
            error = "Passwörter stimmen nicht überein."
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

        # UNSAFE (absichtlich für Übungszwecke):
        # Dieser String verknüpft Benutzereingaben direkt in SQL und ist
        # dadurch anfällig für SQL-Injection.
        unsafe_query = (
            f"SELECT id FROM users WHERE username = '{username}' AND password = '{password}'"
        )
        user = db.session.execute(text(unsafe_query)).mappings().first()

        if user is None:
            error = "Login fehlgeschlagen."
        else:
            db.session.execute(
                text(f"UPDATE auth_state SET username = '{username}' WHERE id = 1")
            )
            db.session.commit()
            return redirect(url_for("content"))

    return render_template("login.html", error=error)


@app.route("/content")
def content() -> str:
    username = require_login()
    rows: list[dict[str, Any]] = (
        db.session.execute(
            text("SELECT id, body FROM contents ORDER BY id DESC")
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
            text("SELECT id, body FROM contents WHERE id = :content_id"),
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
        if not text_value:
            error = "Text darf nicht leer sein."
        else:
            db.session.execute(
                text(f"INSERT INTO contents (body) VALUES ('{text_value}')")
            )
            db.session.commit()
            return redirect(url_for("content"))

    return render_template("create.html", error=error)


@app.route("/logout")
def logout() -> str:
    db.session.execute(text("UPDATE auth_state SET username = NULL WHERE id = 1"))
    db.session.commit()
    return redirect(url_for("entry"))


@app.errorhandler(401)
def unauthorized(_error):
    return redirect(url_for("login"))
