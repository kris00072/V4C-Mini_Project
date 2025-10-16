"""
Employee Manager Module
----------------------
Handles all operations related to employee management in SQLite database.
"""

import sqlite3
from database_connections import get_sqlite_connection

def add_employee(first_name: str, last_name: str, email: str, hire_date: str, department: str) -> int:
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT employee_id FROM employees WHERE email = ?", (email,))
        if cursor.fetchone():
            raise ValueError(f"Email '{email}' already exists.")
        cursor.execute(
            "INSERT INTO employees (first_name, last_name, email, hire_date, department) VALUES (?, ?, ?, ?, ?)",
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
            "SELECT * FROM employees WHERE employee_id = ?",
            (employee_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Employee ID {employee_id} not found.")
        return dict(row)
    finally:
        conn.close()


def list_all_employees() -> list[dict]:
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employees ORDER BY employee_id")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_employee(employee_id: int, field: str, new_value: str):
    valid_fields = ["first_name", "last_name", "email", "hire_date", "department"]
    if field not in valid_fields:
        raise ValueError(f"Invalid field. Choose from {valid_fields}")
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        query = f"UPDATE employees SET {field} = ? WHERE employee_id = ?"
        cursor.execute(query, (new_value, employee_id))
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"No employee found with ID {employee_id}")
    finally:
        conn.close()


def delete_employee(employee_id: int):
    conn = get_sqlite_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"No employee found with ID {employee_id}")
    finally:
        conn.close()
