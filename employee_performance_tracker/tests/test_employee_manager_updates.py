import employee_manager as em


def test_update_paths_all_fields(temp_sqlite_db):
    conn = temp_sqlite_db
    emp_id = em.add_employee(conn, "A", "B", "a@ex.com", "2024-01-01", "Eng")
    # update first_name
    em.update_employee(emp_id, conn, field="first_name", new_value="C")
    assert em.get_employee_by_id(emp_id, conn)["first_name"] == "C"
    # last_name
    em.update_employee(emp_id, conn, field="last_name", new_value="D")
    assert em.get_employee_by_id(emp_id, conn)["last_name"] == "D"
    # email (unique ok)
    em.update_employee(emp_id, conn, field="email", new_value="c@ex.com")
    assert em.get_employee_by_id(emp_id, conn)["email"] == "c@ex.com"
    # hire_date
    em.update_employee(emp_id, conn, field="hire_date", new_value="2024-02-02")
    assert em.get_employee_by_id(emp_id, conn)["hire_date"] == "2024-02-02"
    # department
    em.update_employee(emp_id, conn, field="department", new_value="QA")
    assert em.get_employee_by_id(emp_id, conn)["department"] == "QA"


