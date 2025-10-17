"""
Main file to interact with Employee, Project, and Performance Reviewer Modules
"""

from tabulate import tabulate
from database_connections import get_sqlite_connection, get_mongo_collection
from employee_manager import *
from project_manager import *
from performance_reviewer import *
import performance_reviewer as pr
from reports import (
    report_all_employees,
    report_employee_detail,
    report_all_projects,
    report_project_detail,
    report_top_performers,
    report_reviews_by_date_range,
)


# -------------------------
# Display Helpers
# -------------------------
def display_table(records, title="Records"):
    """Pretty-print records as a table."""
    if not records:
        print(f"\n[WARNING] No {title.lower()} found.\n")
        return
    headers = records[0].keys()
    rows = [r.values() for r in records]
    print(f"\n--- {title} ---")
    print(tabulate(rows, headers=headers, tablefmt="grid"))


def display_reviews_table(reviews, title="Performance Reviews"):
    """Pretty-print reviews with normalized fields and readable columns."""
    if not reviews:
        print(f"\n[WARNING] No {title.lower()} found.\n")
        return
    def normalize_list_field(value):
        if value is None:
            return ""
        if isinstance(value, list):
            return ", ".join(str(v) for v in value if str(v).strip())
        return str(value)
    def short(text, max_len=40):
        s = str(text) if text is not None else ""
        return s if len(s) <= max_len else s[:max_len - 1] + "…"
    headers = [
        "Review ID",
        "Employee ID",
        "Reviewer",
        "Rating",
        "Review Date",
        "Strengths",
        "Areas",
        "Comments",
        "Goals",
    ]
    rows = []
    for r in reviews:
        rows.append([
            r.get("review_id") or r.get("_id"),
            r.get("employee_id"),
            r.get("reviewer_name"),
            r.get("overall_rating"),
            r.get("review_date"),
            short(normalize_list_field(r.get("strengths"))),
            short(normalize_list_field(r.get("areas_for_improvement"))),
            short(r.get("comments")),
            short(normalize_list_field(r.get("goals_for_next_period"))),
        ])
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
        print("3. Performance Review Menu")
        print("4. Reports Menu")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            employee_menu(conn)
        elif choice == "2":
            project_menu(conn)
        elif choice == "3":
            performance_review_menu(collection)
        elif choice == "4":
            reports_submenu()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("[WARNING] Invalid choice. Try again.")

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
            print("[WARNING] Invalid choice. Try again.")


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
                    print("[WARNING] Invalid input format. Use employee_id,project_id,role")
                    continue
                try:
                    assignments.append({
                        "employee_id": int(parts[0].strip()),
                        "project_id": int(parts[1].strip()),
                        "role": parts[2].strip()
                    })
                except ValueError:
                    print("[WARNING] Employee ID and Project ID must be integers.")
            bulk_assign_employees(assignments, conn)
        elif choice == "13":
            file_path = input("Enter CSV file path to export: ")
            export_projects_to_csv(file_path, conn)
        elif choice == "14":
            break
        else:
            print("[WARNING] Invalid choice. Try again.")


# -------------------------
# Performance Review Submenu
# -------------------------
def performance_review_menu(collection):
    # Ensure integer review_id exists for all documents
    try:
        updated = pr.ensure_review_ids(collection)
        if updated:
            print(f"[INFO] Migrated {updated} reviews to integer review_id.")
    except Exception:
        pass
    while True:
        print("\n--- Performance Review Menu ---")
        print("1. Submit Performance Review (Interactive)")
        print("2. Submit Performance Review (Comprehensive Form)")
        print("3. Get Reviews for Employee")
        print("4. Get Average Rating for Employee")
        print("5. Update Performance Review")
        print("6. Delete Performance Review")
        print("7. Get Recent Reviews")
        print("8. Get Reviews by Reviewer")
        print("9. Get Reviews by Date Range")
        print("10. Aggregate Strengths")
        print("11. Aggregate Areas for Improvement")
        print("12. Get Top Goals")
        print("13. Back to Main Menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            submit_performance_review(collection=collection)
        elif choice == "2":
            from performance_reviewer import get_comprehensive_review_input
            review_data = get_comprehensive_review_input()
            if review_data:
                submit_performance_review(collection=collection, **review_data)
        elif choice == "3":
            reviews = get_performance_reviews_for_employee(collection=collection)
            display_reviews_table(reviews, "Performance Reviews")
        elif choice == "4":
            avg_rating = get_average_rating_for_employee(collection=collection)
            if avg_rating is not None:
                print(f"\n[SUCCESS] Average rating: {avg_rating}")
        elif choice == "5":
            print("\n=== Update Performance Review ===")
            print("Available fields to update:")
            print("- employee_id")
            print("- reviewer_name") 
            print("- overall_rating")
            print("- review_date")
            print("- strengths")
            print("- areas_for_improvement")
            print("- comments")
            print("- goals_for_next_period")
            print("\nEnter fields to update (leave blank to skip):")
            fields = {}
            
            # Get review ID first
            review_id = input("Enter review ID to update: ").strip()
            if not review_id:
                print("[WARNING] Review ID is required.")
                continue
            
            # Get fields to update
            while True:
                field = input("Field name (or 'done' to finish): ").strip()
                if field.lower() == 'done':
                    break
                if field:
                    value = input(f"New value for {field}: ").strip()
                    if value:
                        fields[field] = value
            
            if fields:
                update_performance_review(collection=collection, review_id=review_id, **fields)
            else:
                print("[WARNING] No fields provided for update.")
        elif choice == "6":
            # Prompt specifically for integer review_id by default
            review_id = input("Enter review ID to delete (integer): ").strip()
            pr.delete_performance_review(collection=collection, review_id=review_id)
        elif choice == "7":
            limit = input("Enter limit (default 5): ").strip()
            limit = int(limit) if limit.isdigit() else 5
            reviews = get_recent_reviews(collection=collection, limit=limit)
            display_reviews_table(reviews, "Recent Reviews")
        elif choice == "8":
            reviews = get_reviews_by_reviewer(collection=collection)
            display_reviews_table(reviews, "Reviews by Reviewer")
        elif choice == "9":
            reviews = get_reviews_by_date_range(collection=collection)
            display_reviews_table(reviews, "Reviews by Date Range")
        elif choice == "10":
            strengths = aggregate_strengths(collection=collection)
            if strengths:
                print("\n--- Strengths Frequency ---")
                for strength, count in strengths.items():
                    print(f"{strength}: {count}")
            else:
                print("[WARNING] No strengths found.")
        elif choice == "11":
            areas = aggregate_areas_for_improvement(collection=collection)
            if areas:
                print("\n--- Areas for Improvement Frequency ---")
                for area, count in areas.items():
                    print(f"{area}: {count}")
            else:
                print("[WARNING] No improvement areas found.")
        elif choice == "12":
            limit = input("Enter limit (default 5): ").strip()
            limit = int(limit) if limit.isdigit() else 5
            goals = get_top_goals(collection=collection, limit=limit)
            if goals:
                print(f"\n--- Top {limit} Goals ---")
                for i, goal in enumerate(goals, 1):
                    print(f"{i}. {goal}")
            else:
                print("[WARNING] No goals found.")
        elif choice == "13":
            break
        else:
            print("[WARNING] Invalid choice. Try again.")


# -------------------------
# Reports Submenu
# -------------------------
def reports_submenu():
    while True:
        print("\n=== Reports Menu ===")
        print("1. List all employees")
        print("2. Employee detailed report")
        print("3. List all projects")
        print("4. Project detailed report")
        print("5. Top performers")
        print("6. Reviews by date range")
        print("7. Back to Main Menu")

        choice = input("Select an option: ").strip()

        if choice == "1":
            report_all_employees()
        elif choice == "2":
            eid = input("Enter employee ID: ").strip()
            if eid.isdigit():
                report_employee_detail(int(eid))
            else:
                print("[WARNING] Invalid employee ID.")
        elif choice == "3":
            report_all_projects()
        elif choice == "4":
            pid = input("Enter project ID: ").strip()
            if pid.isdigit():
                report_project_detail(int(pid))
            else:
                print("[WARNING] Invalid project ID.")
        elif choice == "5":
            limit = input("Enter number of top performers to list (default 5): ").strip()
            limit = int(limit) if limit.isdigit() else 5
            report_top_performers(limit)
        elif choice == "6":
            start = input("Enter start date (YYYY-MM-DD): ").strip()
            end = input("Enter end date (YYYY-MM-DD): ").strip()
            report_reviews_by_date_range(start, end)
        elif choice == "7":
            break
        else:
            print("[WARNING] Invalid option. Try again.")


# -------------------------
# Entry Point
# -------------------------
if __name__ == "__main__":
    main()
