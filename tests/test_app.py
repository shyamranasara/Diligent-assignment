"""Test suite for the Expense Tracker API.

Written with unittest (stdlib) so it has zero extra dependencies beyond
Flask itself, but it is fully discoverable and runnable by pytest too
(pytest auto-detects unittest.TestCase classes), which is what the README
instructs reviewers to run.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import create_app  # noqa: E402


class ExpenseAPITestCase(unittest.TestCase):
    def setUp(self):
        self._tmp_dir = tempfile.TemporaryDirectory()
        db_path = os.path.join(self._tmp_dir.name, "test_expenses.db")
        app = create_app(db_path)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        self._tmp_dir.cleanup()

    def add(self, title="Lunch", amount=12.5, category="Food", date="2026-07-01"):
        return self.client.post(
            "/expenses",
            json={"title": title, "amount": amount, "category": category, "date": date},
        )

    def test_index(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)

    def test_add_expense_success(self):
        resp = self.add()
        self.assertEqual(resp.status_code, 201)
        body = resp.get_json()
        self.assertEqual(body["title"], "Lunch")
        self.assertEqual(body["amount"], 12.5)
        self.assertEqual(body["category"], "Food")
        self.assertEqual(body["date"], "2026-07-01")
        self.assertIn("id", body)

    def test_add_expense_missing_field(self):
        resp = self.client.post(
            "/expenses", json={"title": "Lunch", "amount": 10, "category": "Food"}
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("date", resp.get_json()["error"])

    def test_add_expense_invalid_amount(self):
        resp = self.add(amount="not-a-number")
        self.assertEqual(resp.status_code, 400)

    def test_add_expense_negative_amount(self):
        resp = self.add(amount=-5)
        self.assertEqual(resp.status_code, 400)

    def test_add_expense_invalid_date(self):
        resp = self.add(date="07/01/2026")
        self.assertEqual(resp.status_code, 400)

    def test_add_expense_non_json_body(self):
        resp = self.client.post("/expenses", data="not json")
        self.assertEqual(resp.status_code, 400)

    def test_view_all_expenses(self):
        self.add(title="Lunch", category="Food")
        self.add(title="Bus", category="Transport")
        resp = self.client.get("/expenses")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 2)

    def test_view_all_expenses_empty(self):
        resp = self.client.get("/expenses")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_filter_by_category(self):
        self.add(title="Lunch", category="Food")
        self.add(title="Dinner", category="Food")
        self.add(title="Bus", category="Transport")
        resp = self.client.get("/expenses?category=Food")
        body = resp.get_json()
        self.assertEqual(len(body), 2)
        self.assertTrue(all(e["category"] == "Food" for e in body))

    def test_filter_by_category_no_match(self):
        self.add(category="Food")
        resp = self.client.get("/expenses?category=Nonexistent")
        self.assertEqual(resp.get_json(), [])

    def test_total_overall(self):
        self.add(amount=10)
        self.add(amount=15.5)
        resp = self.client.get("/expenses/total")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["total"], 25.5)

    def test_total_overall_no_expenses(self):
        resp = self.client.get("/expenses/total")
        self.assertEqual(resp.get_json()["total"], 0)

    def test_total_by_specific_category(self):
        self.add(amount=10, category="Food")
        self.add(amount=20, category="Food")
        self.add(amount=5, category="Transport")
        resp = self.client.get("/expenses/total?category=Food")
        body = resp.get_json()
        self.assertEqual(body["category"], "Food")
        self.assertEqual(body["total"], 30)

    def test_total_by_category_breakdown(self):
        self.add(amount=10, category="Food")
        self.add(amount=20, category="Food")
        self.add(amount=5, category="Transport")
        resp = self.client.get("/expenses/total/by-category")
        self.assertEqual(resp.get_json(), {"Food": 30, "Transport": 5})

    def test_get_single_expense(self):
        created = self.add().get_json()
        resp = self.client.get(f"/expenses/{created['id']}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["id"], created["id"])

    def test_get_single_expense_not_found(self):
        resp = self.client.get("/expenses/9999")
        self.assertEqual(resp.status_code, 404)

    def test_delete_expense(self):
        created = self.add().get_json()
        expense_id = created["id"]

        resp = self.client.delete(f"/expenses/{expense_id}")
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f"/expenses/{expense_id}")
        self.assertEqual(resp.status_code, 404)

    def test_delete_expense_not_found(self):
        resp = self.client.delete("/expenses/9999")
        self.assertEqual(resp.status_code, 404)

    def test_delete_removes_from_total(self):
        created = self.add(amount=50).get_json()
        self.add(amount=10)
        self.client.delete(f"/expenses/{created['id']}")
        resp = self.client.get("/expenses/total")
        self.assertEqual(resp.get_json()["total"], 10)


if __name__ == "__main__":
    unittest.main()
