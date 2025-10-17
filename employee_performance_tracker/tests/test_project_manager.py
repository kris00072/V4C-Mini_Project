from project_manager import (
    add_project,
    list_all_projects,
    get_projects_for_employee,
    get_employees_for_project,
    assign_employee_to_project,
    update_project,
    delete_project,
    search_projects_by_name,
    get_projects_by_status,
    get_project_count_by_status,
    export_projects_to_csv,
)
from employee_manager import add_employee


def test_create_project_and_assignments(temp_sqlite_db):
    conn = temp_sqlite_db
    # seed employees
    e1 = add_employee(conn, "A", "One", "a1@ex.com", "2023-01-01", "Eng")
    e2 = add_employee(conn, "B", "Two", "b2@ex.com", "2023-01-02", "Eng")
    pid = add_project(conn, "P1", "2024-01-01", "", "Planning")
    assert pid > 0
    # assign
    rid1 = assign_employee_to_project(e1, pid, "Dev", conn)
    rid2 = assign_employee_to_project(e2, pid, "QA", conn)
    assert rid1 != -1 and rid2 != -1

    emps = get_employees_for_project(pid, conn)
    assert {r["employee_id"] for r in emps} == {e1, e2}
    projs = get_projects_for_employee(e1, conn)
    assert any(r["project_id"] == pid for r in projs)

    # update project fields non-interactively
    update_project(pid, conn, project_name="P1-upd", start_date="2024-01-02", end_date="", status="Planning")
    # search
    assert any(p["project_name"] == "P1-upd" for p in search_projects_by_name("P1", conn))
    # status
    by_status = get_projects_by_status("Planning", conn)
    assert any(p["project_id"] == pid for p in by_status)
    # counts
    counts = get_project_count_by_status(conn)
    assert isinstance(counts, dict) and "Planning" in counts
    # export
    import tempfile, os
    fd, path = tempfile.mkstemp(suffix=".csv")
    os.close(fd)
    try:
        export_projects_to_csv(path, conn)
        assert os.path.exists(path)
    finally:
        try:
            os.remove(path)
        except Exception:
            pass
    # delete
    delete_project(pid, conn)
    assert not any(p["project_id"] == pid for p in list_all_projects(conn))


