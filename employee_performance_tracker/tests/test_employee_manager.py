import pytest

from employee_manager import (
    add_employee,
    list_all_employees,
    get_employee_by_id,
    delete_employee,
    update_employee,
    search_employees_by_name,
    search_employees_by_department,
    get_recently_hired_employees,
)


def test_add_and_retrieve_employee_success(temp_sqlite_db):
    conn = temp_sqlite_db
    emp_id = add_employee(
        conn,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        hire_date="2024-01-01",
        department="Engineering",
    )
    assert emp_id > 0
    emp = get_employee_by_id(emp_id, conn)
    assert emp["email"] == "john.doe@example.com"


def test_add_duplicate_email_rejected(temp_sqlite_db):
    conn = temp_sqlite_db
    emp_id1 = add_employee(
        conn,
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2024-01-02",
        department="QA",
    )
    assert emp_id1 > 0
    # attempt duplicate
    emp_id2 = add_employee(
        conn,
        first_name="Jake",
        last_name="Doe",
        email="jane@example.com",
        hire_date="2024-02-02",
        department="QA",
    )
    assert emp_id2 == -1


def test_list_and_delete_employees(temp_sqlite_db):
    conn = temp_sqlite_db
    ids = []
    for i in range(3):
        emp_id = add_employee(
            conn,
            first_name=f"A{i}",
            last_name=f"B{i}",
            email=f"a{i}@ex.com",
            hire_date="2023-03-03",
            department="Ops",
        )
        ids.append(emp_id)
    emps = list_all_employees(conn)
    assert len(emps) == 3
    # update
    update_employee(ids[0], conn, field="department", new_value="Support")
    assert get_employee_by_id(ids[0], conn)["department"] == "Support"
    # search
    assert search_employees_by_name("A", conn)
    assert search_employees_by_department("Ops", conn)
    # recent
    assert get_recently_hired_employees(2, conn)
    delete_employee(ids[1], conn)
    emps = list_all_employees(conn)
    assert len(emps) == 2


