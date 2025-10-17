"""
Reports Module

Responsibilities:
- Generate detailed reports based on employee, project, and performance data.
- Combine data from SQLite (employees, projects) and MongoDB (performance reviews).
- Provide both interactive CLI and programmatic access.
- Support sorting, filtering, and aggregation.

Dependencies:
- employee_manager.py
- project_manager.py
- performance_reviewer.py
- database_connections.py
- tabulate for formatted output
"""

from datetime import datetime
from typing import List, Dict, Optional, Any

from tabulate import tabulate

from database_connections import get_sqlite_connection, get_mongo_collection
from employee_manager import list_all_employees, get_employee_by_id
from project_manager import (
    list_all_projects,
    get_project_by_id,
    get_projects_for_employee,
    get_employees_for_project,
)
from performance_reviewer import (
    get_performance_reviews_for_employee,
    get_average_rating_for_employee,
    aggregate_strengths,
    aggregate_areas_for_improvement,
    get_top_goals,
)

# Ensure we read from the same MongoDB collection namespace used by main.py
def _get_reviews_collection():
    try:
        base_collection = get_mongo_collection()
        # main.py uses: collection = get_mongo_collection()["performance_reviews"]
        return base_collection["performance_reviews"]
    except Exception as e:
        print(f"[WARNING] Failed to connect to MongoDB: {e}")
        return None

# -------------------------
# Employee Reports
# -------------------------

def report_all_employees():
    """Generate a table of all employees with basic details."""
    conn = get_sqlite_connection()
    employees = list_all_employees(conn)
    conn.close()
    
    if not employees:
        print("[INFO] No employees found.")
        return
    
    table = []
    for emp in employees:
        table.append([
            emp.get('employee_id'),
            f"{emp.get('first_name')} {emp.get('last_name')}",
            emp.get('email'),
            emp.get('department'),
            emp.get('hire_date')
        ])
    
    print("\n=== All Employees ===")
    print(tabulate(table, headers=["ID", "Name", "Email", "Department", "Hire Date"], tablefmt="fancy_grid"))


def report_employee_detail(employee_id: int):
    """Generate detailed report for a single employee, including projects and performance."""
    conn = get_sqlite_connection()
    emp = get_employee_by_id(employee_id, conn)
    
    if not emp:
        conn.close()
        print(f"[WARNING] Employee ID {employee_id} not found.")
        return
    
    print(f"\n=== Employee Detail: {emp['first_name']} {emp['last_name']} (ID: {employee_id}) ===")
    print(f"Email: {emp['email']}")
    print(f"Department: {emp['department']}")
    print(f"Hire Date: {emp['hire_date']}")
    
    # Projects: query assignments from SQLite
    emp_projects = get_projects_for_employee(employee_id, conn)
    if emp_projects:
        print("\nProjects Assigned:")
        for proj in emp_projects:
            print(f"- {proj.get('project_name')} (Role: {proj.get('role', 'N/A')})")
    else:
        print("\n[INFO] No projects assigned.")
    
    # Performance
    collection = _get_reviews_collection()
    reviews = get_performance_reviews_for_employee(collection=collection, employee_id=employee_id)
    avg_rating = get_average_rating_for_employee(collection=collection, employee_id=employee_id)
    print(f"\nPerformance Reviews Found: {len(reviews)}")
    print(f"Average Rating: {avg_rating if avg_rating else 'N/A'}")
    
    # Aggregated insights
    strengths = aggregate_strengths(collection=collection, employee_id=employee_id)
    areas = aggregate_areas_for_improvement(collection=collection, employee_id=employee_id)
    goals = get_top_goals(collection=collection, employee_id=employee_id)
    
    if strengths:
        print("\nTop Strengths:")
        for s, count in strengths.items():
            print(f"- {s} ({count})")
    
    if areas:
        print("\nAreas for Improvement:")
        for a, count in areas.items():
            print(f"- {a} ({count})")
    
    if goals:
        print("\nTop Goals for Next Period:")
        for g in goals:
            print(f"- {g}")


# -------------------------
# Project Reports
# -------------------------

def report_all_projects():
    """Generate a table of all projects with assigned employees."""
    conn = get_sqlite_connection()
    projects = list_all_projects(conn)
    conn.close()
    
    if not projects:
        print("[INFO] No projects found.")
        return
    
    table = []
    for proj in projects:
        emp_count = len(proj.get('employee_ids', []))
        table.append([
            proj.get('project_id'),
            proj.get('project_name'),
            proj.get('start_date'),
            proj.get('end_date'),
            emp_count
        ])
    
    print("\n=== All Projects ===")
    print(tabulate(table, headers=["ID", "Project Name", "Start Date", "End Date", "Employees Assigned"], tablefmt="fancy_grid"))


def report_project_detail(project_id: int):
    """Generate detailed report for a single project, including assigned employees and performance stats."""
    conn = get_sqlite_connection()
    proj = get_project_by_id(project_id, conn)
    
    if not proj:
        print(f"[WARNING] Project ID {project_id} not found.")
        return
    
    print(f"\n=== Project Detail: {proj['project_name']} (ID: {project_id}) ===")
    print(f"Start Date: {proj['start_date']}")
    print(f"End Date: {proj['end_date']}")
    
    # Assigned employees via junction table
    employees = get_employees_for_project(project_id, conn)
    if employees:
        print("\nAssigned Employees:")
        for rec in employees:
            print(f"- {rec['first_name']} {rec['last_name']} (Role: {rec.get('role', 'N/A')})")
    else:
        print("\n[INFO] No employees assigned.")
    
    # Average ratings for assigned employees
    print("\nEmployee Performance Ratings:")
    collection = _get_reviews_collection()
    for rec in employees:
        eid = rec['employee_id']
        avg_rating = get_average_rating_for_employee(collection=collection, employee_id=eid)
        print(f"- Employee ID {eid}: {avg_rating if avg_rating else 'N/A'}")

    # Close the connection after all SQLite operations are complete
    conn.close()


# -------------------------
# Performance Reports
# -------------------------

def report_top_performers(limit: int = 5):
    """List top N employees by average rating."""
    conn = get_sqlite_connection()
    employees = list_all_employees(conn)
    conn.close()
    
    ratings = []
    collection = _get_reviews_collection()
    for emp in employees:
        eid = emp.get('employee_id')
        avg_rating = get_average_rating_for_employee(collection=collection, employee_id=eid)
        if avg_rating is not None:
            ratings.append((eid, f"{emp['first_name']} {emp['last_name']}", avg_rating))
    
    ratings.sort(key=lambda x: x[2], reverse=True)
    top_ratings = ratings[:limit]
    
    print(f"\n=== Top {limit} Performers ===")
    table = [[eid, name, rating] for eid, name, rating in top_ratings]
    print(tabulate(table, headers=["Employee ID", "Name", "Average Rating"], tablefmt="fancy_grid"))


def report_reviews_by_date_range(start_date: str, end_date: str):
    """Generate report of all reviews in a given date range."""
    collection = _get_reviews_collection()
    
    reviews = []
    try:
        from performance_reviewer import get_reviews_by_date_range
        reviews = get_reviews_by_date_range(collection=collection, start_date=start_date, end_date=end_date)
    except Exception as e:
        print(f"[WARNING] Failed to retrieve reviews: {e}")
        return
    
    if not reviews:
        print(f"[INFO] No reviews found between {start_date} and {end_date}.")
        return
    
    table = []
    for r in reviews:
        table.append([
            r.get('review_id') or r.get('_id'),
            r.get('employee_id'),
            r.get('reviewer_name'),
            r.get('overall_rating'),
            r.get('review_date')
        ])
    
    print(f"\n=== Performance Reviews from {start_date} to {end_date} ===")
    print(tabulate(table, headers=["Review ID", "Employee ID", "Reviewer", "Rating", "Review Date"], tablefmt="fancy_grid"))


''' # -------------------------
# Interactive CLI
# -------------------------

def reports_menu():
    """Interactive CLI menu for generating reports."""
    while True:
        print("\n=== Reports Menu ===")
        print("1. List all employees")
        print("2. Employee detailed report")
        print("3. List all projects")
        print("4. Project detailed report")
        print("5. Top performers")
        print("6. Reviews by date range")
        print("0. Exit")
        
        choice = input("Select an option: ").strip()
        
        if choice == "1":
            report_all_employees()
        elif choice == "2":
            eid = input("Enter employee ID: ").strip()
            if eid.isdigit():
                report_employee_detail(int(eid))
        elif choice == "3":
            report_all_projects()
        elif choice == "4":
            pid = input("Enter project ID: ").strip()
            if pid.isdigit():
                report_project_detail(int(pid))
        elif choice == "5":
            limit = input("Enter number of top performers to list (default 5): ").strip()
            limit = int(limit) if limit.isdigit() else 5
            report_top_performers(limit)
        elif choice == "6":
            start = input("Enter start date (YYYY-MM-DD): ").strip()
            end = input("Enter end date (YYYY-MM-DD): ").strip()
            report_reviews_by_date_range(start, end)
        elif choice == "0":
            print("Exiting reports menu.")
            break
        else:
            print("[WARNING] Invalid option. Try again.")


# -------------------------
# Self-test
# -------------------------
if __name__ == "__main__":
    print("Reports module self-test...")
    reports_menu() '''
