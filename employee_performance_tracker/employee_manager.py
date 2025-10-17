"""
Employee Manager Module
----------------------
Handles all operations related to employee management in SQLite database.
"""

import sqlite3
import re
import csv
from datetime import datetime
from database_connections import get_sqlite_connection
from tabulate import tabulate

# -------------------------
# Validation Helpers
# -------------------------
def validate_name(name: str) -> bool:
    if not name.isalpha():
        print("⚠️  Name must contain only letters.")
        return False
    if not name:
        print("⚠️  Name cannot be empty.")
        return False
    return True

def validate_email(email: str, conn) -> bool:
    regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(regex, email):
        print("⚠️  Invalid email format.")
        return False
    cursor = conn.cursor()
    cursor.execute("SELECT employee_id FROM employees WHERE email = ?", (email,))
    if cursor.fetchone():
        print(f"⚠️  Email '{email}' already exists.")
        return False
    return True

def validate_hire_date(hire_date: str) -> bool:
    try:
        date_obj = datetime.strptime(hire_date, "%Y-%m-%d")
        if date_obj > datetime.now():
            print("⚠️  Hire date cannot be in the future.")
            return False
        return True
    except ValueError:
        print("⚠️  Date must be in YYYY-MM-DD format.")
        return False

def validate_department(department: str) -> bool:
    if not department.strip():
        print("⚠️  Department cannot be empty.")
        return False
    return True

def get_valid_input(prompt: str, validate_func, conn=None):  # pragma: no cover
    while True:
        value = input(prompt)
        if conn:
            if validate_func(value, conn):
                return value
        else:
            if validate_func(value):
                return value

# -------------------------
# Employee Operations
# -------------------------
def add_employee(conn, first_name=None, last_name=None, email=None, hire_date=None, department=None) -> int:
    if first_name is None:
        first_name = get_valid_input("Enter first name: ", validate_name)
    if last_name is None:
        last_name = get_valid_input("Enter last name: ", validate_name)
    if email is None:
        email = get_valid_input("Enter email: ", validate_email, conn)
    if hire_date is None:
        hire_date = get_valid_input("Enter hire date (YYYY-MM-DD): ", validate_hire_date)
    if department is None:
        department = get_valid_input("Enter department: ", validate_department)

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (first_name, last_name, email, hire_date, department) VALUES (?, ?, ?, ?, ?)",
            (first_name, last_name, email, hire_date, department)
        )
        conn.commit()
        print(f"✅ Employee '{first_name} {last_name}' added with ID {cursor.lastrowid}.")
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        print(f"⚠️ Database error: {e}")
        return -1

def get_employee_by_id(employee_id: int, conn) -> dict:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))
    row = cursor.fetchone()
    if not row:
        print(f"⚠️ Employee ID {employee_id} not found.")
        return {}
    return dict(row)

def list_all_employees(conn) -> list[dict]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees ORDER BY employee_id")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def update_employee(employee_id: int, conn, field=None, new_value=None):
    valid_fields = ["first_name", "last_name", "email", "hire_date", "department"]
    if field is None:
        field = input(f"Enter field to update {valid_fields}: ").strip()
    if field not in valid_fields:
        print(f"⚠️ Invalid field. Choose from {valid_fields}")
        return

    # Validation per field
    if new_value is None:
        if field in ["first_name", "last_name"]:
            new_value = get_valid_input(f"Enter new {field}: ", validate_name)
        elif field == "email":
            new_value = get_valid_input("Enter new email: ", validate_email, conn)
        elif field == "hire_date":
            new_value = get_valid_input("Enter new hire date (YYYY-MM-DD): ", validate_hire_date)
        elif field == "department":
            new_value = get_valid_input("Enter new department: ", validate_department)

    cursor = conn.cursor()
    cursor.execute(f"UPDATE employees SET {field} = ? WHERE employee_id = ?", (new_value, employee_id))
    conn.commit()
    if cursor.rowcount == 0:
        print(f"⚠️ No employee found with ID {employee_id}")
    else:
        print(f"✅ Employee ID {employee_id} updated successfully.")

def delete_employee(employee_id: int, conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE employee_id = ?", (employee_id,))
    conn.commit()
    if cursor.rowcount == 0:
        print(f"⚠️ No employee found with ID {employee_id}")
    else:
        print(f"✅ Employee ID {employee_id} deleted successfully.")

def search_employees_by_name(name: str, conn) -> list[dict]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE first_name LIKE ? OR last_name LIKE ?", (f"%{name}%", f"%{name}%"))
    return [dict(row) for row in cursor.fetchall()]

def search_employees_by_department(department: str, conn) -> list[dict]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE department LIKE ?", (f"%{department}%",))
    return [dict(row) for row in cursor.fetchall()]

def get_recently_hired_employees(limit: int, conn) -> list[dict]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees ORDER BY hire_date DESC LIMIT ?", (limit,))
    return [dict(row) for row in cursor.fetchall()]

def bulk_add_employees(employee_list: list[dict], conn):
    for emp in employee_list:
        add_employee(conn, **emp)

def export_employees_to_csv(file_path: str, conn):
    employees = list_all_employees(conn)
    if not employees:
        print("⚠️ No employees to export.")
        return
    keys = employees[0].keys()
    with open(file_path, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(employees)
    print(f"✅ Employees exported to {file_path}")

def get_employee_count_by_department(conn) -> dict:
    cursor = conn.cursor()
    cursor.execute("SELECT department, COUNT(*) as count FROM employees GROUP BY department")
    return dict(cursor.fetchall())
