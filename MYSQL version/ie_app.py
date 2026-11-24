import mysql.connector


def get_connection():
    # Opens a new connection to the apparel_ie database
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="passwordhere",
        database="apparel_ie",
    )


def show_query(sql, params=()):
    # Runs any SELECT and prints the results as a simple table
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    headers = [col[0] for col in cur.description]

    print(" | ".join(headers))
    print("-" * 70)
    for row in rows:
        print(" | ".join(str(value) for value in row))
    print(f"({len(rows)} rows)")

    cur.close()
    conn.close()


def add_employee():
    emp_id = int(input("Employee ID: "))
    name = input("Name: ")
    designation = input("Designation: ")
    department = input("Department: ")
    skill = input("Skill level: ")
    joining = input("Joining date (YYYY-MM-DD): ")
    contact = input("Contact no: ")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO Employee_Details
               (Employee_ID, Employee_Name, Designation, Department,
                Skill_Level, Joining_Date, Contact_No)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (emp_id, name, designation, department, skill, joining, contact),
        )
        conn.commit()
        print("Employee added.")
    except mysql.connector.Error as err:
        print("Could not add employee:", err)
    finally:
        cur.close()
        conn.close()


def update_designation():
    emp_id = int(input("Employee ID to update: "))
    new_designation = input("New designation: ")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Employee_Details SET Designation = %s WHERE Employee_ID = %s",
        (new_designation, emp_id),
    )
    conn.commit()
    if cur.rowcount == 0:
        print("No employee found with that ID.")
    else:
        print("Designation updated.")
    cur.close()
    conn.close()


def delete_employee():
    emp_id = int(input("Employee ID to delete: "))

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Employee_Details WHERE Employee_ID = %s", (emp_id,))
        conn.commit()
        if cur.rowcount == 0:
            print("No employee found with that ID.")
        else:
            print("Employee deleted.")
    except mysql.connector.Error as err:
        # Happens when the employee is still referenced by other tables
        print("Could not delete employee:", err)
    finally:
        cur.close()
        conn.close()

def view_line_efficiency():
    show_query(
        """
        SELECT pl.Line_Name, pl.Available_Minutes,
               ROUND(SUM(pr.Actual_Quantity * od.SAM), 2) AS Earned_Minutes,
               ROUND(SUM(pr.Actual_Quantity * od.SAM) * 100.0 / pl.Available_Minutes, 2)
                   AS Line_Efficiency_Pct
        FROM Production_Records pr
        JOIN Production_Line pl ON pr.Line_ID = pl.Line_ID
        JOIN Operation_Details od ON pr.Operation_ID = od.Operation_ID
        GROUP BY pl.Line_ID, pl.Line_Name, pl.Available_Minutes
        """
    )


def view_operator_efficiency():
    show_query(
        """
        SELECT e.Employee_Name, pr.Production_Date,
               ROUND(SUM(pr.Actual_Quantity * od.SAM), 2) AS Earned_Minutes,
               ROUND(SUM(pr.Actual_Quantity * od.SAM) * 100.0 / 480, 2)
                   AS Operator_Efficiency_Pct
        FROM Production_Records pr
        JOIN Employee_Details e ON pr.Employee_ID = e.Employee_ID
        JOIN Operation_Details od ON pr.Operation_ID = od.Operation_ID
        GROUP BY e.Employee_Name, pr.Production_Date
        ORDER BY e.Employee_Name, pr.Production_Date
        """
    )


def view_production_by_date():
    # %s is filled with the date you type in
    date = input("Date (YYYY-MM-DD): ")
    show_query(
        """
        SELECT e.Employee_Name, od.Operation_Name,
               pr.Target_Quantity, pr.Actual_Quantity
        FROM Production_Records pr
        JOIN Employee_Details e ON pr.Employee_ID = e.Employee_ID
        JOIN Operation_Details od ON pr.Operation_ID = od.Operation_ID
        WHERE pr.Production_Date = %s
        """,
        (date,),
    )

def add_production_record():
    prod_id = int(input("Production ID (use a new number, e.g. 7): "))
    date = input("Production date (YYYY-MM-DD): ")
    line_id = int(input("Line ID (1 or 2): "))
    emp_id = int(input("Employee ID: "))
    op_id = int(input("Operation ID (201-204): "))
    target = int(input("Target quantity: "))
    actual = int(input("Actual quantity: "))
    shift = input("Shift (Day/Night): ")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO Production_Records
               (Production_ID, Production_Date, Line_ID, Employee_ID,
                Operation_ID, Target_Quantity, Actual_Quantity, Shift)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (prod_id, date, line_id, emp_id, op_id, target, actual, shift),
        )
        conn.commit()
        print("Production record added.")
    except mysql.connector.Error as err:
        # Catches duplicate IDs and IDs that don't exist in other tables
        print("Could not add production record:", err)
    finally:
        cur.close()
        conn.close()

MENU = """
===== Apparel IE System =====
1. Add employee
2. Update employee designation
3. Delete employee
4. View all employees
5. View line efficiency
6. View operator efficiency
7. View production by date
8. Add production record
0. Exit
"""

while True:
    print(MENU)
    choice = input("Choose an option: ")

    if choice == "1":
        add_employee()
    elif choice == "2":
        update_designation()
    elif choice == "3":
        delete_employee()
    elif choice == "4":
        show_query(
            "SELECT Employee_ID, Employee_Name, Designation, Department "
            "FROM Employee_Details ORDER BY Employee_ID"
        )
    elif choice == "5":
        view_line_efficiency()
    elif choice == "6":
        view_operator_efficiency()
    elif choice == "7":
        view_production_by_date()
    elif choice == "8":
        add_production_record()
    elif choice == "0":
        print("Goodbye.")
        break
    else:
        print("Invalid choice, try again.")