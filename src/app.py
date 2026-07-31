"""Expense Tracker REST API.

Endpoints:
    POST   /expenses                 Add an expense
    GET    /expenses                 List all expenses (optional ?category=)
    GET    /expenses/<id>            Get a single expense
    DELETE /expenses/<id>            Delete an expense
    GET    /expenses/total           Overall total (optional ?category=)
    GET    /expenses/total/by-category  Totals grouped by category
"""
from datetime import datetime

from flask import Flask, jsonify, request

from database import close_db, get_db, init_db

REQUIRED_FIELDS = ("title", "amount", "category", "date")


def create_app(database_path="expenses.db"):
    app = Flask(__name__)
    app.config["DATABASE"] = database_path

    init_db(app)
    app.teardown_appcontext(close_db)

    @app.get("/")
    def index():
        return jsonify({"status": "ok", "service": "expense-tracker-api"})

    @app.post("/expenses")
    def add_expense():
        data = request.get_json(silent=True)
        if data is None:
            return jsonify({"error": "Request body must be JSON"}), 400

        missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] in (None, "")]
        if missing:
            return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

        title = str(data["title"]).strip()
        category = str(data["category"]).strip()
        date_str = str(data["date"]).strip()

        try:
            amount = float(data["amount"])
        except (TypeError, ValueError):
            return jsonify({"error": "amount must be a number"}), 400
        if amount <= 0:
            return jsonify({"error": "amount must be greater than 0"}), 400

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "date must be in YYYY-MM-DD format"}), 400

        db = get_db(app)
        cur = db.execute(
            "INSERT INTO expenses (title, amount, category, date) VALUES (?, ?, ?, ?)",
            (title, amount, category, date_str),
        )
        db.commit()
        new_id = cur.lastrowid
        row = db.execute("SELECT * FROM expenses WHERE id = ?", (new_id,)).fetchone()
        return jsonify(dict(row)), 201

    @app.get("/expenses")
    def list_expenses():
        db = get_db(app)
        category = request.args.get("category")
        if category:
            rows = db.execute(
                "SELECT * FROM expenses WHERE category = ? ORDER BY date DESC, id DESC",
                (category,),
            ).fetchall()
        else:
            rows = db.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC").fetchall()
        return jsonify([dict(r) for r in rows]), 200

    @app.get("/expenses/total")
    def total_expenses():
        db = get_db(app)
        category = request.args.get("category")
        if category:
            row = db.execute(
                "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE category = ?",
                (category,),
            ).fetchone()
            return jsonify({"category": category, "total": round(row["total"], 2)}), 200
        row = db.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses").fetchone()
        return jsonify({"total": round(row["total"], 2)}), 200

    @app.get("/expenses/total/by-category")
    def total_by_category():
        db = get_db(app)
        rows = db.execute(
            "SELECT category, COALESCE(SUM(amount), 0) AS total "
            "FROM expenses GROUP BY category ORDER BY category"
        ).fetchall()
        return jsonify({r["category"]: round(r["total"], 2) for r in rows}), 200

    @app.get("/expenses/<int:expense_id>")
    def get_expense(expense_id):
        db = get_db(app)
        row = db.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        if row is None:
            return jsonify({"error": f"Expense {expense_id} not found"}), 404
        return jsonify(dict(row)), 200

    @app.delete("/expenses/<int:expense_id>")
    def delete_expense(expense_id):
        db = get_db(app)
        row = db.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
        if row is None:
            return jsonify({"error": f"Expense {expense_id} not found"}), 404
        db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        db.commit()
        return jsonify({"message": f"Expense {expense_id} deleted"}), 200

    return app


if __name__ == "__main__":
    flask_app = create_app("expenses.db")
    flask_app.run(debug=True, port=5000)
