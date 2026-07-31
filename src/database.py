"""SQLite database helpers for the Expense Tracker API.

Uses a plain sqlite3 connection per request (via Flask's `g` object) rather
than an ORM, since the schema is a single table and the assignment allows
either an in-memory store or a local file — SQLite gives us real SQL with
zero extra setup.
"""
import sqlite3
from flask import g


SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL
);
"""


def get_db(app):
    """Return a request-scoped SQLite connection, creating one if needed."""
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create the schema if it doesn't already exist."""
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.execute(SCHEMA)
    conn.commit()
    conn.close()
