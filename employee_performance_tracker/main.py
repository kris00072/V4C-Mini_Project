from employee_manager import add_employee, get_employee_by_id, list_all_employees, update_employee, delete_employee
import re
from datetime import datetime

def print_menu():
    print("\n=== Employee Management System ===")
    print("1. Add Employee")
    print("2. List All Employees")
    print("3. Get Employee by ID")
    print("4. Update Employee Details")
    print("5. Delete Employee")
    print("6. Exit")

# Validation helpers
def input_non_empty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("⚠️ This field cannot be empty. Please enter a value.")

def input_email(prompt):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    while True:
        email = input(prompt).strip()
        if not email:
            print("⚠️ Email cannot be empty. Please enter a value.")
            continue
        if not re.match(pattern, email):
            print("⚠️ Invalid email format. Please enter again.")
        else:
            return email

def input_date(prompt):
    while True:
        date_str = input(prompt).strip()
        if not date_str:
            print("⚠️ Date cannot be empty. Please enter a value.")
            continue
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("⚠️ Invalid date format. Use YYYY-MM-DD. Please enter again.")

def main():
    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            # Add Employee
            first_name = input_non_empty("First Name: ")
            last_name = input_non_empty("Last Name: ")
            email = input_email("Email: ")
            hire_date = input_date("Hire Date (YYYY-MM-DD): ")
            department = input_non_empty("Department: ")
            emp_id = add_employee(first_name, last_name, email, hire_date, department)
            print(f"✅ Employee added with ID: {emp_id}")

        elif choice == "2":
            # List All Employees
            employees = list_all_employees()
            if not employees:
                print("No employees found.")
            else:
                # Simple tabular output
                print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Email':<30} {'Hire Date':<12} {'Department':<15}")
                print("-" * 95)
                for emp in employees:
                    print(f"{emp['employee_id']:<5} {emp['first_name']:<15} {emp['last_name']:<15} {emp['email']:<30} {emp['hire_date']:<12} {emp['department']:<15}")

        elif choice == "3":
            emp_id = input_non_empty("Enter Employee ID: ")
            try:
                emp_id = int(emp_id)
                emp = get_employee_by_id(emp_id)
                print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Email':<30} {'Hire Date':<12} {'Department':<15}")
                print("-" * 95)
                print(f"{emp['employee_id']:<5} {emp['first_name']:<15} {emp['last_name']:<15} {emp['email']:<30} {emp['hire_date']:<12} {emp['department']:<15}")
            except ValueError:
                print("⚠️ Invalid ID entered.")
            except Exception as e:
                print(f"⚠️ {e}")

        elif choice == "4":
            emp_id = input_non_empty("Enter Employee ID to update: ")
            try:
                emp_id = int(emp_id)
                field = input_non_empty("Field to update (first_name, last_name, email, hire_date, department): ")
                if field == "email":
                    new_value = input_email(f"New value for {field}: ")
                elif field == "hire_date":
                    new_value = input_date(f"New value for {field}: ")
                else:
                    new_value = input_non_empty(f"New value for {field}: ")
                update_employee(emp_id, field, new_value)
                print("✅ Employee updated successfully.")
            except ValueError:
                print("⚠️ Invalid ID entered.")
            except Exception as e:
                print(f"⚠️ {e}")

        elif choice == "5":
            emp_id = input_non_empty("Enter Employee ID to delete: ")
            try:
                emp_id = int(emp_id)
                delete_employee(emp_id)
                print("✅ Employee deleted successfully.")
            except ValueError:
                print("⚠️ Invalid ID entered.")
            except Exception as e:
                print(f"⚠️ {e}")

        elif choice == "6":
            print("Exiting program.")
            break

        else:
            print("⚠️ Invalid choice. Please enter a number from 1 to 6.")

if __name__ == "__main__":
    main()
