# main.py
from employee_manager import add_employee, get_employee_by_id, list_all_employees, update_employee, delete_employee

def print_menu():
    print("\n=== Employee Management System ===")
    print("1. Add Employee")
    print("2. List All Employees")
    print("3. Get Employee by ID")
    print("4. Update Employee Details")
    print("5. Delete Employee")
    print("6. Exit")


def main():
    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            # Add Employee
            try:
                first_name = input("First Name: ").strip()
                last_name = input("Last Name: ").strip()
                email = input("Email: ").strip()
                hire_date = input("Hire Date (YYYY-MM-DD): ").strip()
                department = input("Department: ").strip()
                emp_id = add_employee(first_name, last_name, email, hire_date, department)
                print(f"✅ Employee added with ID: {emp_id}")
            except Exception as e:
                print("❌ Error:", e)

        elif choice == "2":
            # List All Employees
            try:
                employees = list_all_employees()
                if not employees:
                    print("No employees found.")
                else:
                    for emp in employees:
                        print(emp)
            except Exception as e:
                print("❌ Error:", e)

        elif choice == "3":
            # Get Employee by ID
            try:
                emp_id = int(input("Enter Employee ID: "))
                emp = get_employee_by_id(emp_id)
                print(emp)
            except Exception as e:
                print("❌ Error:", e)

        elif choice == "4":
            # Update Employee
            try:
                emp_id = int(input("Enter Employee ID to update: "))
                field = input("Field to update (first_name, last_name, email, hire_date, department): ").strip()
                new_value = input(f"New value for {field}: ").strip()
                update_employee(emp_id, field, new_value)
                print("✅ Employee updated successfully.")
            except Exception as e:
                print("❌ Error:", e)

        elif choice == "5":
            # Delete Employee
            try:
                emp_id = int(input("Enter Employee ID to delete: "))
                delete_employee(emp_id)
                print("✅ Employee deleted successfully.")
            except Exception as e:
                print("❌ Error:", e)

        elif choice == "6":
            print("Exiting program.")
            break

        else:
            print("❌ Invalid choice. Please enter a number from 1 to 6.")


if __name__ == "__main__":
    main()
