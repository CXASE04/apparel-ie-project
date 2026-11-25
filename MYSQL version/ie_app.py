import mysql.connector
from datetime import datetime


def get_connection():
    # Opens a new connection to the apparel_ie database
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="apparel_ie",
    )

# Allowed values. Change these lists to match your organisation.
GENDERS = ["Male", "Female", "Other"]
DESIGNATIONS = ["Operator", "Helper", "Supervisor", "Quality Inspector",
                "IE Executive", "Production Manager"]
DEPARTMENTS = ["Sewing", "Cutting", "Finishing", "Quality Control",
               "Industrial Engineering", "Administration"]
SKILL_LEVELS = ["Basic", "Semi-skilled", "Skilled", "Expert"]


def choose_from(label, options):
    # Shows a numbered list and keeps asking until a valid number is entered
    print(f"\n{label}:")
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")
    while True:
        pick = input("Enter the number: ").strip()
        if pick.isdigit() and 1 <= int(pick) <= len(options):
            return options[int(pick) - 1]
        print("Please enter a number from the list.")


def ask_required(label):
    # Keeps asking until something other than blank is entered
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("This field cannot be empty.")


def ask_date(label):
    while True:
        value = ask_required(f"{label} (YYYY-MM-DD)")
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            print("Use the format YYYY-MM-DD, for example 2026-11-24.")


def ask_contact():
    while True:
        value = ask_required("Contact number (10 digits)")
        if value.isdigit() and len(value) == 10:
            return value
        print("Contact number must be exactly 10 digits.")

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
    print("\n--- Add new employee (every field is required) ---")
    name = ask_required("Name")
    gender = choose_from("Gender", GENDERS)
    designation = choose_from("Designation", DESIGNATIONS)
    department = choose_from("Department", DEPARTMENTS)
    skill = choose_from("Skill level", SKILL_LEVELS)
    joining = ask_date("Joining date")
    contact = ask_contact()

    # No Employee_ID here: MySQL fills it in automatically
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO Employee_Details
               (Employee_Name, Gender, Designation, Department,
                Skill_Level, Joining_Date, Contact_No)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (name, gender, designation, department, skill, joining, contact),
        )
        conn.commit()
        print(f"Employee added with ID {cur.lastrowid}.")
    except mysql.connector.Error as err:
        print("Could not add employee:", err)
    finally:
        cur.close()
        conn.close()


# Fields that can be edited. Each entry is: (column name, label, function that asks for the new value)
EDITABLE_FIELDS = {
    "1": ("Designation", "Designation", lambda: choose_from("Designation", DESIGNATIONS)),
    "2": ("Department", "Department", lambda: choose_from("Department", DEPARTMENTS)),
    "3": ("Skill_Level", "Skill level", lambda: choose_from("Skill level", SKILL_LEVELS)),
    "4": ("Contact_No", "Contact number", ask_contact),
}


def update_employee():
    emp_id = input("Employee ID to update: ").strip()
    if not emp_id.isdigit():
        print("Employee ID must be a number.")
        return

    # First check that the employee exists
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT Employee_Name FROM Employee_Details WHERE Employee_ID = %s",
        (int(emp_id),),
    )
    found = cur.fetchone()
    cur.close()
    conn.close()
    if found is None:
        print("No employee found with that ID.")
        return

    print(f"\nEditing employee {emp_id}: {found[0]}")

    # Keep offering changes until the user chooses 0
    while True:
        print("\nWhat do you want to change?")
        for key, (column, label, ask) in EDITABLE_FIELDS.items():
            print(f"  {key}. {label}")
        print("  0. Finished")

        pick = input("Choose: ").strip()
        if pick == "0":
            break
        if pick not in EDITABLE_FIELDS:
            print("Please choose a number from the list.")
            continue

        column, label, ask = EDITABLE_FIELDS[pick]
        new_value = ask()

        conn = get_connection()
        cur = conn.cursor()
        try:
            # column comes from our fixed list above, never from user typing,
            # so putting it into the SQL text is safe. The value uses %s.
            cur.execute(
                f"UPDATE Employee_Details SET {column} = %s WHERE Employee_ID = %s",
                (new_value, int(emp_id)),
            )
            conn.commit()
            print(f"{label} updated.")
        except mysql.connector.Error as err:
            print("Could not update:", err)
        finally:
            cur.close()
            conn.close()

    print("Update finished.")


def set_employee_status():
    emp_id = input("Employee ID: ").strip()
    if not emp_id.isdigit():
        print("Employee ID must be a number.")
        return
    emp_id = int(emp_id)

    print("\n1. Deactivate (resigned or left)")
    print("2. Reactivate")
    pick = input("Choose: ").strip()
    if pick == "1":
        new_status = "Inactive"
    elif pick == "2":
        new_status = "Active"
    else:
        print("Invalid choice.")
        return

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT Employee_Status FROM Employee_Details WHERE Employee_ID = %s",
            (emp_id,),
        )
        row = cur.fetchone()
        if row is None:
            print("No employee found with that ID.")
            return
        if row[0] == new_status:
            print(f"Employee {emp_id} is already {new_status}.")
            return

        if new_status == "Inactive":
            # Find lines this person supervises, and get a replacement for each
            cur.execute(
                "SELECT Line_ID, Line_Name FROM Production_Line "
                "WHERE Line_Supervisor_ID = %s",
                (emp_id,),
            )
            for line_id, line_name in cur.fetchall():
                print(f"\n{line_name} is supervised by employee {emp_id}.")
                new_sup = pick_record(
                    f"Choose a new supervisor for {line_name}",
                    "SELECT Employee_ID, Employee_Name, Designation "
                    "FROM Employee_Details "
                    "WHERE Employee_Status = 'Active' AND Employee_ID <> %s "
                    "ORDER BY Employee_ID",
                    (emp_id,),
                )
                if new_sup is None:
                    print("No replacement available. Deactivation cancelled.")
                    return
                cur.execute(
                    "UPDATE Production_Line SET Line_Supervisor_ID = %s WHERE Line_ID = %s",
                    (new_sup, line_id),
                )

        cur.execute(
            "UPDATE Employee_Details SET Employee_Status = %s WHERE Employee_ID = %s",
            (new_status, emp_id),
        )
        conn.commit()
        print(f"Employee {emp_id} is now {new_status}. Their records are kept.")
    except mysql.connector.Error as err:
        conn.rollback()
        print("Could not update status:", err)
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
    status = ask_status_filter()
    where = "WHERE e.Employee_Status = %s" if status else ""
    params = (status,) if status else ()
    show_query(
        f"""
        SELECT e.Employee_Name, pr.Production_Date,
               ROUND(SUM(pr.Actual_Quantity * od.SAM), 2) AS Earned_Minutes,
               ROUND(SUM(pr.Actual_Quantity * od.SAM) * 100.0 / 480, 2)
                   AS Operator_Efficiency_Pct
        FROM Production_Records pr
        JOIN Employee_Details e ON pr.Employee_ID = e.Employee_ID
        JOIN Operation_Details od ON pr.Operation_ID = od.Operation_ID
        {where}
        GROUP BY e.Employee_Name, pr.Production_Date
        ORDER BY e.Employee_Name, pr.Production_Date
        """,
        params,
    )


def view_production_by_date():
    date = ask_date("Date")
    status = ask_status_filter()
    sql = """
        SELECT e.Employee_Name, od.Operation_Name,
               pr.Target_Quantity, pr.Actual_Quantity
        FROM Production_Records pr
        JOIN Employee_Details e ON pr.Employee_ID = e.Employee_ID
        JOIN Operation_Details od ON pr.Operation_ID = od.Operation_ID
        WHERE pr.Production_Date = %s
    """
    params = [date]
    if status:
        sql += " AND e.Employee_Status = %s"
        params.append(status)
    show_query(sql, tuple(params))

def add_production_record():
    print("\n--- Add production record (Production ID is automatic) ---")
    date = ask_date("Production date")

    line_id = pick_record(
        "Choose a production line",
        "SELECT Line_ID, Line_Name, Product_Type FROM Production_Line ORDER BY Line_ID",
    )
    if line_id is None:
        return

    emp_id = pick_record(
        "Choose an active employee",
        "SELECT Employee_ID, Employee_Name, Designation FROM Employee_Details "
        "WHERE Employee_Status = 'Active' ORDER BY Employee_ID",
    )
    if emp_id is None:
        return

    op_id = pick_record(
        "Choose an operation",
        "SELECT Operation_ID, Operation_Name, SAM FROM Operation_Details "
        "ORDER BY Operation_Sequence",
    )
    if op_id is None:
        return

    target = ask_whole_number("Target quantity")
    actual = ask_whole_number("Actual quantity")
    shift = choose_from("Shift", ["Day", "Night"])

    # No Production_ID here: MySQL fills it in automatically
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO Production_Records
               (Production_Date, Line_ID, Employee_ID, Operation_ID,
                Target_Quantity, Actual_Quantity, Shift)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (date, line_id, emp_id, op_id, target, actual, shift),
        )
        conn.commit()
        print(f"Production record added with ID {cur.lastrowid}.")
    except mysql.connector.Error as err:
        print("Could not add production record:", err)
    finally:
        cur.close()
        conn.close()

def view_employees():
    show_query(
        "SELECT Employee_ID, Employee_Name, Gender, Designation, Department, "
        "Skill_Level, Joining_Date, Contact_No, Employee_Status "
        "FROM Employee_Details ORDER BY Employee_ID"
    )

def ask_whole_number(label):
    # Keeps asking until a whole number (0 or more) is entered
    while True:
        value = input(f"{label}: ").strip()
        if value.isdigit():
            return int(value)
        print("Please enter a whole number (0 or more).")


def pick_record(label, sql, params=()):
    # Shows a list from the database and returns the ID the user picks
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        print("Nothing available to choose from.")
        return None

    print(f"\n{label}:")
    for row in rows:
        details = " - ".join(str(value) for value in row[1:])
        print(f"  {row[0]}. {details}")

    valid_ids = {row[0] for row in rows}
    while True:
        pick = input("Enter the number shown: ").strip()
        if pick.isdigit() and int(pick) in valid_ids:
            return int(pick)
        print("Please enter one of the numbers listed.")


def ask_status_filter():
    # Lets the user choose whether reports include inactive employees
    print("\nShow which employees?")
    print("  1. Active only")
    print("  2. All (including inactive)")
    return "Active" if input("Choose: ").strip() == "1" else None

MENU = """
===== Apparel IE System =====
1. Add employee
2. Update employee 
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
        update_employee()
    elif choice == "3":
        set_employee_status()
    elif choice == "4":
        view_employees()
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