"""
Main file to interact with Employee, Project, and Performance Reviewer Modules
"""

from tabulate import tabulate
from database_connections import get_sqlite_connection, get_mongo_collection
from employee_manager import *
from project_manager import *
from performance_reviewer import *


# -------------------------
# Display Helpers
# -------------------------
def display_table(records, title="Records"):
    """Pretty-print records as a table."""
    if not records:
        print(f"\n⚠️ No {title.lower()} found.\n")
        return
    headers = records[0].keys()
    rows = [r.values() for r in records]
    print(f"\n--- {title} ---")
    print(tabulate(rows, headers=headers, tablefmt="grid"))


# -------------------------
# Main Menu
# -------------------------
def main():
    conn = get_sqlite_connection()
    mongo_db = get_mongo_collection()
    collection = mongo_db["performance_reviews"]

    while True:
        print("\n=== Main Menu ===")
        print("1. Employee Menu")
        print("2. Project Menu")
        print("4. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            employee_menu(conn)
        elif choice == "2":
            project_menu(conn)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("⚠️ Invalid choice. Try again.")

    conn.close()


# -------------------------
# Employee Submenu
# -------------------------
def employee_menu(conn):
    while True:
        print("\n--- Employee Menu ---")
        print("1. Add Employee")
        print("2. List All Employees")
        print("3. Update Employee")
        print("4. Delete Employee")
        print("5. Search by Name")
        print("6. Search by Department")
        print("7. Recently Hired Employees")
        print("8. Export Employees to CSV")
        print("9. Back to Main Menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_employee(conn)
        elif choice == "2":
            display_table(list_all_employees(conn), "Employees")
        elif choice == "3":
            emp_id = int(input("Enter employee ID to update: "))
            update_employee(emp_id, conn)
        elif choice == "4":
            emp_id = int(input("Enter employee ID to delete: "))
            delete_employee(emp_id, conn)
        elif choice == "5":
            name = input("Enter name to search: ")
            display_table(search_employees_by_name(name, conn), "Employees")
        elif choice == "6":
            dept = input("Enter department to search: ")
            display_table(search_employees_by_department(dept, conn), "Employees")
        elif choice == "7":
            limit = int(input("How many recent hires to show? "))
            display_table(get_recently_hired_employees(limit, conn), "Employees")
        elif choice == "8":
            file_path = input("Enter CSV file path to export: ")
            export_employees_to_csv(file_path, conn)
        elif choice == "9":
            break
        else:
            print("⚠️ Invalid choice. Try again.")


# -------------------------
# Project Submenu
# -------------------------
def project_menu(conn):
    while True:
        print("\n--- Project Menu ---")
        print("1. Add Project")
        print("2. List All Projects")
        print("3. Update Project")
        print("4. Delete Project")
        print("5. Assign Employee to Project")
        print("6. Unassign Employee from Project")
        print("7. Get Projects for Employee")
        print("8. Get Employees for Project")
        print("9. Search Projects by Name")
        print("10. Get Projects by Status")
        print("11. Get Project Count by Status")
        print("12. Bulk Assign Employees")
        print("13. Export Projects to CSV")
        print("14. Back to Main Menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_project(conn)
        elif choice == "2":
            display_table(list_all_projects(conn), "Projects")
        elif choice == "3":
            pid = int(input("Enter project ID to update: "))
            update_project(pid, conn)
        elif choice == "4":
            pid = int(input("Enter project ID to delete: "))
            delete_project(pid, conn)
        elif choice == "5":
            eid = int(input("Enter employee ID: "))
            pid = int(input("Enter project ID: "))
            role = input("Enter role: ")
            assign_employee_to_project(eid, pid, role, conn)
        elif choice == "6":
            eid = int(input("Enter employee ID: "))
            pid = int(input("Enter project ID: "))
            unassign_employee_from_project(eid, pid, conn)
        elif choice == "7":
            eid = int(input("Enter employee ID: "))
            display_table(get_projects_for_employee(eid, conn), f"Projects for Employee {eid}")
        elif choice == "8":
            pid = int(input("Enter project ID: "))
            display_table(get_employees_for_project(pid, conn), f"Employees for Project {pid}")
        elif choice == "9":
            name = input("Enter project name to search: ")
            display_table(search_projects_by_name(name, conn), "Projects")
        elif choice == "10":
            status = input(f"Enter status {ALLOWED_STATUSES}: ")
            display_table(get_projects_by_status(status, conn), f"Projects with status {status}")
        elif choice == "11":
            counts = get_project_count_by_status(conn)
            print("\nProject counts by status:")
            for status, count in counts.items():
                print(f"{status}: {count}")
        elif choice == "12":
            print("Enter assignments (employee_id, project_id, role) one per line. Type 'done' to finish.")
            assignments = []
            while True:
                line = input("Assignment: ")
                if line.lower() == "done":
                    break
                parts = line.split(",")
                if len(parts) != 3:
                    print("⚠️ Invalid input format. Use employee_id,project_id,role")
                    continue
                try:
                    assignments.append({
                        "employee_id": int(parts[0].strip()),
                        "project_id": int(parts[1].strip()),
                        "role": parts[2].strip()
                    })
                except ValueError:
                    print("⚠️ Employee ID and Project ID must be integers.")
            bulk_assign_employees(assignments, conn)
        elif choice == "13":
            file_path = input("Enter CSV file path to export: ")
            export_projects_to_csv(file_path, conn)
        elif choice == "14":
            break
        else:
            print("⚠️ Invalid choice. Try again.")


# -------------------------
# Entry Point
# -------------------------
if __name__ == "__main__":
    main()
