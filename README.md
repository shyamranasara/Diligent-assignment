# Expense Tracker API

A small REST API for managing personal expenses, built with **Python, Flask, and SQLite**.

## Features

- Add an expense (`title`, `amount`, `category`, `date`)
- View all expenses
- Filter expenses by category
- Calculate total expenses (overall, by a specific category, or grouped by all categories)
- Delete an expense
- Get a single expense by id

## Tech Stack

- **Language:** Python 3.9+
- **Framework:** Flask
- **Storage:** SQLite (via the stdlib `sqlite3` module — a local file, `expenses.db`, created automatically on first run)
- **Testing:** `unittest` (stdlib), runnable via `pytest`

## Project Structure

```
expense-api/
  README.md
  AI_NOTES.md
  requirements.txt
  src/
    app.py         # Flask app + all routes
    database.py     # SQLite connection/schema helpers
  tests/
    test_app.py      # test suite
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the server

```bash
cd src
python3 app.py
```

The server starts on `http://127.0.0.1:5000`. A SQLite file `expenses.db` is created in the `src/` directory on first run (delete it to reset the data).

## Running the tests

From the project root:

```bash
pytest tests/
```

(The tests use only Python's built-in `unittest`, so `python3 -m unittest discover -s tests` also works if `pytest` isn't installed.)

Tests use a temporary SQLite file per test (via `tempfile`), so they never touch `expenses.db` and don't require the server to be running.

## API Reference

### `POST /expenses`
Add an expense.

Request body:
```json
{ "title": "Groceries", "amount": 45.30, "category": "Food", "date": "2026-07-15" }
```
- `date` must be in `YYYY-MM-DD` format.
- `amount` must be a positive number.

Response: `201 Created` with the created expense (including its new `id`).

### `GET /expenses`
List all expenses, most recent date first.
Optional query param: `?category=Food` — filter by category.

### `GET /expenses/<id>`
Get a single expense by id. `404` if it doesn't exist.

### `DELETE /expenses/<id>`
Delete an expense by id. `404` if it doesn't exist.

### `GET /expenses/total`
Overall total.
Optional query param: `?category=Food` — total for just that category.

### `GET /expenses/total/by-category`
Totals grouped by every category, e.g.:
```json
{ "Food": 57.3, "Transport": 12.0 }
```

## Example usage (curl)

```bash
curl -X POST http://127.0.0.1:5000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Groceries","amount":45.30,"category":"Food","date":"2026-07-15"}'

curl http://127.0.0.1:5000/expenses
curl "http://127.0.0.1:5000/expenses?category=Food"
curl http://127.0.0.1:5000/expenses/total
curl "http://127.0.0.1:5000/expenses/total?category=Food"
curl http://127.0.0.1:5000/expenses/total/by-category
curl -X DELETE http://127.0.0.1:5000/expenses/1
```

## Design notes

- SQLite was chosen over an in-memory dict so data survives server restarts and the app can use real SQL (`SUM`, `GROUP BY`) for the totals endpoints, while still needing zero external services.
- Input validation is deliberately strict (required fields, positive numeric amount, `YYYY-MM-DD` date) since this is the kind of bug that's easy to skip and easy to regret.
- No bonus feature was implemented — the four required capabilities plus basic validation and error handling were prioritized instead.
