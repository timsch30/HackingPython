from __future__ import annotations

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://postgres:3215@localhost:5432/postgres"
)

app = Flask(__name__, template_folder="../templates")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

from . import routes  # noqa: E402,F401
