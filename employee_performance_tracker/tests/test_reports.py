import builtins
from types import SimpleNamespace

import reports as rpt


class DummyConn:
    def __init__(self, rows):
        self._rows = rows
        self._closed = False
    def cursor(self):
        return self
    def execute(self, *a, **k):
        return self
    def fetchall(self):
        return [self._row_to_row(r) for r in self._rows]
    def fetchone(self):
        return self._row_to_row(self._rows[0]) if self._rows else None
    def _row_to_row(self, d):
        return SimpleNamespace(**d) if not hasattr(SimpleNamespace, "keys") else d
    def commit(self):
        pass
    def close(self):
        self._closed = True


def test_report_all_employees(monkeypatch, capsys):
    # Monkeypatch SQLite connection to return two employees
    monkeypatch.setattr(rpt, "get_sqlite_connection", lambda: DummyConn([
        {"employee_id": 1, "first_name": "A", "last_name": "One", "email": "a@ex.com", "department": "Eng", "hire_date": "2024-01-01"},
        {"employee_id": 2, "first_name": "B", "last_name": "Two", "email": "b@ex.com", "department": "QA", "hire_date": "2024-01-02"},
    ]))
    monkeypatch.setattr(rpt, "list_all_employees", lambda conn: [
        {"employee_id": 1, "first_name": "A", "last_name": "One", "email": "a@ex.com", "department": "Eng", "hire_date": "2024-01-01"},
        {"employee_id": 2, "first_name": "B", "last_name": "Two", "email": "b@ex.com", "department": "QA", "hire_date": "2024-01-02"},
    ])
    rpt.report_all_employees()
    out = capsys.readouterr().out
    assert "All Employees" in out and "A One" in out


def test_report_top_performers(monkeypatch, capsys):
    # two employees with ratings
    monkeypatch.setattr(rpt, "get_sqlite_connection", lambda: DummyConn([
        {"employee_id": 1, "first_name": "A", "last_name": "One"},
        {"employee_id": 2, "first_name": "B", "last_name": "Two"},
    ]))
    monkeypatch.setattr(rpt, "list_all_employees", lambda conn: [
        {"employee_id": 1, "first_name": "A", "last_name": "One"},
        {"employee_id": 2, "first_name": "B", "last_name": "Two"},
    ])
    monkeypatch.setattr(rpt, "get_average_rating_for_employee", lambda collection=None, employee_id=None: 4.0 if employee_id == 1 else 3.5)
    rpt.report_top_performers(2)
    out = capsys.readouterr().out
    assert "Top 2 Performers" in out and "A One" in out


def test_report_reviews_by_date_range(monkeypatch, capsys):
    # fake mongo collection usage path through reports
    class FakeCursor:
        def __init__(self, docs):
            self._docs = list(docs)
        def sort(self, key, order=-1):
            self._docs.sort(key=lambda d: d.get(key), reverse=(order == -1))
            return self
        def __iter__(self):
            return iter(self._docs)

    class FakeCollection:
        def find(self, query):
            start = query["review_date"]["$gte"]
            end = query["review_date"]["$lte"]
            return FakeCursor([
                {"_id": "x1", "employee_id": 1, "reviewer_name": "R", "overall_rating": 4, "review_date": start},
                {"_id": "x2", "employee_id": 2, "reviewer_name": "R2", "overall_rating": 5, "review_date": end},
            ])
    monkeypatch.setattr(rpt, "_get_reviews_collection", lambda: FakeCollection())
    rpt.report_reviews_by_date_range("2024-01-01", "2024-01-02")
    out = capsys.readouterr().out
    assert "Performance Reviews from 2024-01-01 to 2024-01-02" in out


