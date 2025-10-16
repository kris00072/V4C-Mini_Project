# employee_manager.py
"""
Employee Manager Module
Handles all operations related to employee management in SQLite database.

Functions:
- add_employee
- get_employee_by_id
- list_all_employees
- update_employee
- delete_employee
"""

import sqlite3
from database_connections import get_sqlite_connection

def add_employee(first_name: str, last_name: str, email: str, hire_date: str, department: str) -> int:
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        # Check for duplicate email
        cursor.execute("SELECT employee_id FROM Employees WHERE email = ?", (email,))
        if cursor.fetchone():
            raise ValueError(f"Email '{email}' already exists. Cannot add duplicate employee.")
        # Insert new employee
        cursor.execute(
            "INSERT INTO Employees (first_name, last_name, email, hire_date, department) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, email, hire_date, department)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        raise sqlite3.Error(f"Database error while adding employee: {e}")
    finally:
        conn.close()


def get_employee_by_id(employee_id: int) -> dict:
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT employee_id, first_name, last_name, email, hire_date, department FROM Employees WHERE employee_id = ?",
            (employee_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Employee with ID {employee_id} not found.")
        keys = ["employee_id", "first_name", "last_name", "email", "hire_date", "department"]
        return dict(zip(keys, row))
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Database error while fetching employee: {e}")
    finally:
        conn.close()


def list_all_employees() -> list[dict]:
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT employee_id, first_name, last_name, email, hire_date, department FROM Employees ORDER BY employee_id"
        )
        rows = cursor.fetchall()
        keys = ["employee_id", "first_name", "last_name", "email", "hire_date", "department"]
        return [dict(zip(keys, row)) for row in rows]
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Database error while fetching all employees: {e}")
    finally:
        conn.close()


def update_employee(employee_id: int, field: str, new_value: str):
    valid_fields = ["first_name", "last_name", "email", "hire_date", "department"]
    if field not in valid_fields:
        raise ValueError(f"Invalid field. Choose from: {valid_fields}")
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        query = f"UPDATE Employees SET {field} = ? WHERE employee_id = ?"
        cursor.execute(query, (new_value, employee_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"No employee found with ID {employee_id}")
    except sqlite3.Error as e:
        conn.rollback()
        raise sqlite3.Error(f"Error updating employee: {e}")
    finally:
        conn.close()


def delete_employee(employee_id: int):
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Employees WHERE employee_id = ?", (employee_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"No employee found with ID {employee_id}")
    except sqlite3.Error as e:
        conn.rollback()
        raise sqlite3.Error(f"Error deleting employee: {e}")
    finally:
        conn.close()


# Quick test (optional)
if __name__ == "__main__":
    try:
        emp_id = add_employee("John", "Doe", "john.doe@example.com", "2025-10-16", "Engineering")
        print("Added:", get_employee_by_id(emp_id))
        update_employee(emp_id, "department", "HR")
        print("Updated:", get_employee_by_id(emp_id))
        all_emps = list_all_employees()
        print("All Employees:", all_emps)
        delete_employee(emp_id)
        print("Deleted employee with ID:", emp_id)
    except Exception as e:
        print("Error:", e)
