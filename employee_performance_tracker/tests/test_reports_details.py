import reports as rpt


class DummyConn:
    def __init__(self, employees=None, projects=None, ep=None):
        self.employees = employees or []
        self.projects = projects or []
        self.ep = ep or []
    def close(self):
        pass


def test_report_employee_detail(monkeypatch, capsys):
    # employee 10 assigned to two projects
    conn = DummyConn()
    monkeypatch.setattr(rpt, "get_sqlite_connection", lambda: conn)
    monkeypatch.setattr(rpt, "get_employee_by_id", lambda eid, c: {
        "employee_id": eid, "first_name": "Dev", "last_name": " Singh", "email": "d@ex.com", "department": "Eng", "hire_date": "2024-01-01"
    })
    monkeypatch.setattr(rpt, "get_projects_for_employee", lambda eid, c: [
        {"project_id": 1, "project_name": "P1", "role": "Dev"},
        {"project_id": 2, "project_name": "P2", "role": "QA"},
    ])
    # ratings/aggregations
    monkeypatch.setattr(rpt, "_get_reviews_collection", lambda: None)
    monkeypatch.setattr(rpt, "get_performance_reviews_for_employee", lambda **k: [{}, {}])
    monkeypatch.setattr(rpt, "get_average_rating_for_employee", lambda **k: 4.2)
    monkeypatch.setattr(rpt, "aggregate_strengths", lambda **k: {"python": 2})
    monkeypatch.setattr(rpt, "aggregate_areas_for_improvement", lambda **k: {"comm": 1})
    monkeypatch.setattr(rpt, "get_top_goals", lambda **k: ["goal1"]) 
    rpt.report_employee_detail(10)
    out = capsys.readouterr().out
    assert "Projects Assigned:" in out and "P1" in out and "Average Rating: 4.2" in out


def test_report_project_detail(monkeypatch, capsys):
    conn = DummyConn()
    monkeypatch.setattr(rpt, "get_sqlite_connection", lambda: conn)
    monkeypatch.setattr(rpt, "get_project_by_id", lambda pid, c: {
        "project_id": pid, "project_name": "P1", "start_date": "2024-01-01", "end_date": None
    })
    monkeypatch.setattr(rpt, "get_employees_for_project", lambda pid, c: [
        {"employee_id": 10, "first_name": "Dev", "last_name": "Singh", "role": "Dev"}
    ])
    monkeypatch.setattr(rpt, "_get_reviews_collection", lambda: None)
    monkeypatch.setattr(rpt, "get_average_rating_for_employee", lambda **k: 4.1)
    rpt.report_project_detail(1)
    out = capsys.readouterr().out
    assert "Assigned Employees:" in out and "Dev Singh" in out and "4.1" in out


