"""
Project Manager Module
----------------------
Handles all operations related to projects and employee-project assignments in SQLite database.
"""

import sqlite3
import csv
from datetime import datetime
from database_connections import get_sqlite_connection
from tabulate import tabulate

# -------------------------
# Validation Helpers
# -------------------------
ALLOWED_STATUSES = ["Planning", "Active", "Completed", "On Hold"]

def validate_project_name(project_name: str, conn, project_id=None) -> bool:
    project_name = project_name.strip()
    if not project_name:
        print("⚠️ Project name cannot be empty.")
        return False
    cursor = conn.cursor()
    if project_id:
        cursor.execute(
            "SELECT project_id FROM projects WHERE project_name = ? AND project_id != ?",
            (project_name, project_id)
        )
    else:
        cursor.execute("SELECT project_id FROM projects WHERE project_name = ?", (project_name,))
    if cursor.fetchone():
        print(f"⚠️ Project '{project_name}' already exists.")
        return False
    return True

def validate_date(date_str: str, allow_empty=False) -> bool:
    if allow_empty and not date_str.strip():
        return True
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        print("⚠️ Date must be in YYYY-MM-DD format.")
        return False

def validate_status(status: str) -> bool:
    if status not in ALLOWED_STATUSES:
        print(f"⚠️ Status must be one of {ALLOWED_STATUSES}.")
        return False
    return True

def validate_role(role: str) -> bool:
    if not role.strip():
        print("⚠️ Role cannot be empty.")
        return False
    return True

def get_valid_input(prompt: str, validate_func, conn=None, **kwargs):
    while True:
        value = input(prompt)
        if conn:
            if validate_func(value, conn, **kwargs):
                return value
        else:
            if validate_func(value, **kwargs):
                return value

def validate_project_data(project_name, start_date, end_date, status, conn, project_id=None) -> bool:
    if not validate_project_name(project_name, conn, project_id):
        return False
    if not validate_date(start_date):
        return False
    if end_date and not validate_date(end_date, allow_empty=True):
        return False
    if end_date and start_date and end_date < start_date:
        print("⚠️ End date cannot be before start date.")
        return False
    if not validate_status(status):
        return False
    return True

# -------------------------
# Project Operations
# -------------------------
def add_project(conn, project_name=None, start_date=None, end_date=None, status=None) -> int:
    if project_name is None:
        project_name = get_valid_input("Enter project name: ", validate_project_name, conn)
    if start_date is None:
        start_date = get_valid_input("Enter start date (YYYY-MM-DD): ", validate_date)
    if end_date is None:
        end_date_input = input("Enter end date (YYYY-MM-DD) or leave blank: ").strip()
        end_date = end_date_input if end_date_input else None
        if end_date and not validate_date(end_date):
            end_date = get_valid_input("Enter valid end date (YYYY-MM-DD) or leave blank: ", validate_date)
    if status is None:
        # Prompt user for status if not provided
        status = get_valid_input(f"Enter project status {ALLOWED_STATUSES}: ", validate_status)

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (project_name, start_date, end_date, status) VALUES (?, ?, ?, ?)",
            (project_name, start_date, end_date, status)
        )
        conn.commit()
        print(f"✅ Project '{project_name}' added with ID {cursor.lastrowid}.")
        return cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        print(f"⚠️ Database error: {e}")
        return -1


def update_project(project_id: int, conn, **kwargs):
    valid_fields = ["project_name", "start_date", "end_date", "status"]
    fields_to_update = {}
    for field in valid_fields:
        if field in kwargs:
            value = kwargs[field]
        else:
            value = input(f"Enter new value for {field} (leave blank to skip): ").strip()
            if not value:
                continue
        # Validate input
        if field == "project_name" and not validate_project_name(value, conn, project_id):
            value = get_valid_input(f"Enter valid project name: ", validate_project_name, conn, project_id=project_id)
        elif field in ["start_date", "end_date"]:
            if not validate_date(value, allow_empty=(field=="end_date")):
                value = get_valid_input(f"Enter valid {field} (YYYY-MM-DD): ", validate_date, allow_empty=(field=="end_date"))
        elif field == "status" and not validate_status(value):
            value = get_valid_input(f"Enter valid status {ALLOWED_STATUSES}: ", validate_status)
        fields_to_update[field] = value

    if not fields_to_update:
        print("⚠️ No fields to update.")
        return

    set_clause = ", ".join(f"{k} = ?" for k in fields_to_update.keys())
    params = list(fields_to_update.values()) + [project_id]
    cursor = conn.cursor()
    cursor.execute(f"UPDATE projects SET {set_clause} WHERE project_id = ?", params)
    conn.commit()
    if cursor.rowcount == 0:
        print(f"⚠️ No project found with ID {project_id}.")
    else:
        print(f"✅ Project ID {project_id} updated successfully.")

def delete_project(project_id: int, conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE project_id = ?", (project_id,))
    conn.commit()
    if cursor.rowcount == 0:
        print(f"⚠️ No project found with ID {project_id}.")
    else:
        print(f"✅ Project ID {project_id} deleted successfully.")

# -------------------------
# Assignment Operations
# -------------------------
def assign_employee_to_project(employee_id: int, project_id: int, role: str, conn) -> int:
    if not validate_role(role):
        role = get_valid_input("Enter valid role: ", validate_role)
    cursor = conn.cursor()
    # Check existence
    cursor.execute("SELECT 1 FROM employees WHERE employee_id = ?", (employee_id,))
    if not cursor.fetchone():
        print("⚠️ Employee ID not found.")
        return -1
    cursor.execute("SELECT 1 FROM projects WHERE project_id = ?", (project_id,))
    if not cursor.fetchone():
        print("⚠️ Project ID not found.")
        return -1
    # Check duplicate assignment
    cursor.execute("SELECT 1 FROM employee_projects WHERE employee_id = ? AND project_id = ?", (employee_id, project_id))
    if cursor.fetchone():
        print("⚠️ This employee is already assigned to this project.")
        return -1
    cursor.execute(
        "INSERT INTO employee_projects (employee_id, project_id, role) VALUES (?, ?, ?)",
        (employee_id, project_id, role)
    )
    conn.commit()
    print(f"✅ Employee {employee_id} assigned to Project {project_id} with role '{role}'.")
    return cursor.lastrowid

def unassign_employee_from_project(employee_id: int, project_id: int, conn):
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM employee_projects WHERE employee_id = ? AND project_id = ?",
        (employee_id, project_id)
    )
    conn.commit()
    if cursor.rowcount == 0:
        print("⚠️ Assignment not found.")
    else:
        print(f"✅ Employee {employee_id} unassigned from Project {project_id}.")

# -------------------------
# Query Operations
# -------------------------
def get_projects_for_employee(employee_id: int, conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ep.assignment_id, p.project_id, p.project_name, ep.role, ep.assigned_date
        FROM employee_projects ep
        JOIN projects p ON ep.project_id = p.project_id
        WHERE ep.employee_id = ?
        ORDER BY ep.assigned_date DESC
    """, (employee_id,))
    rows = cursor.fetchall()
    return [dict(r) for r in rows]

def get_employees_for_project(project_id: int, conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ep.assignment_id, e.employee_id, e.first_name, e.last_name, ep.role, ep.assigned_date
        FROM employee_projects ep
        JOIN employees e ON ep.employee_id = e.employee_id
        WHERE ep.project_id = ?
        ORDER BY ep.assigned_date DESC
    """, (project_id,))
    rows = cursor.fetchall()
    return [dict(r) for r in rows]

def list_all_projects(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY project_id")
    return [dict(r) for r in cursor.fetchall()]

def search_projects_by_name(project_name: str, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE project_name LIKE ?", (f"%{project_name}%",))
    return [dict(r) for r in cursor.fetchall()]

def get_projects_by_status(status: str, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE status = ?", (status,))
    return [dict(r) for r in cursor.fetchall()]

def get_project_count_by_status(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) as count FROM projects GROUP BY status")
    rows = cursor.fetchall()

    
    result = {}
    for row in rows:
        if isinstance(row, sqlite3.Row):
            result[row['status']] = row['count']
        else:
            
            result[row[0]] = row[1]

    
    for status in ALLOWED_STATUSES:
        if status not in result:
            result[status] = 0

    return result

# -------------------------
# Bulk & Export Operations
# -------------------------
def bulk_assign_employees(assignments_list: list, conn):
    success_count = 0
    for assignment in assignments_list:
        eid = assignment.get("employee_id")
        pid = assignment.get("project_id")
        role = assignment.get("role")

        if eid is None or pid is None or not role:
            print(f"⚠️ Skipping invalid assignment: {assignment}")
            continue

        result = assign_employee_to_project(eid, pid, role, conn)
        if result != -1:
            success_count += 1
        else:
            print(f"⚠️ Failed to assign: {assignment}")

    print(f"✅ Bulk assignment completed. Successfully assigned {success_count}/{len(assignments_list)} employees.")


def export_projects_to_csv(file_path: str, conn):
    projects = list_all_projects(conn)
    if not projects:
        print("⚠️ No projects to export.")
        return
    keys = projects[0].keys()
    with open(file_path, 'w', newline='') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(projects)
    print(f"✅ Projects exported to {file_path}")
