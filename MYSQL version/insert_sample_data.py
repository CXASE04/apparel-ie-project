import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="passwordhere",
    database="apparel_ie",
)
cur = conn.cursor()

for table in [
    "Production_Records",
    "Line_Allocation",
    "Production_Line",
    "Operation_Details",
    "Machine_Details",
    "Employee_Details",
]:
    cur.execute(f"DELETE FROM {table}")


def insert_rows(table, columns, rows):
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    cur.executemany(sql, rows)  # inserts every row in the list
    print(f"{table}: inserted {len(rows)} rows")

insert_rows(
    "Employee_Details",
    ["Employee_ID", "Employee_Name", "Gender", "Designation", "Department",
     "Skill_Level", "Joining_Date", "Contact_No"],
    [
        (101, "Rahul", "Male", "Operator", "Sewing", "Semi-skilled", "2024-03-01", "9800000101"),
        (102, "Priya", "Female", "Operator", "Sewing", "Skilled", "2023-07-15", "9800000102"),
        (103, "Amit", "Male", "Supervisor", "Sewing", "Skilled", "2021-01-10", "9800000103"),
        (104, "Sneha", "Female", "IE Executive", "Industrial Engineering", "Skilled", "2022-05-20", "9800000104"),
    ],
)

insert_rows(
    "Production_Line",
    ["Line_ID", "Line_Name", "Product_Type", "Style_Number", "Working_Shift",
     "Available_Minutes", "Line_Supervisor_ID"],
    [
        (1, "Line 01", "Men's formal shirts", "SHRT-201", "Day", 480, 103),
        (2, "Line 02", "Trousers", "TRS-310", "Day", 480, 103),
    ],
)

insert_rows(
    "Machine_Details",
    ["Machine_ID", "Machine_Type", "Machine_Category", "Machine_Brand",
     "Machine_Model", "Machine_Status"],
    [
        (301, "Single Needle Lockstitch", "Lockstitch", "Juki", "DDL-8700", "Active"),
        (302, "Overlock Machine", "Overlock", "Brother", "M-3000", "Active"),
        (303, "Button Attach Machine", "Specialty", "Juki", "LBH-1790", "Under Maintenance"),
    ],
)

insert_rows(
    "Operation_Details",
    ["Operation_ID", "Operation_Name", "Operation_Description", "Machine_Type",
     "SAM", "Operation_Sequence", "Skill_Required"],
    [
        (201, "Shoulder Joining", "Joining front and back shoulder panels", "Single Needle Lockstitch", 0.45, 1, "Basic"),
        (202, "Sleeve Attaching", "Attaching sleeve to armhole", "Single Needle Lockstitch", 0.80, 2, "Intermediate"),
        (203, "Side Seam", "Closing side seams", "Overlock Machine", 0.65, 3, "Basic"),
        (204, "Button Attaching", "Attaching buttons to placket", "Button Attach Machine", 0.40, 4, "Basic"),
    ],
)

insert_rows(
    "Line_Allocation",
    ["Allocation_ID", "Line_ID", "Employee_ID", "Operation_ID", "Machine_ID",
     "Allocation_Date", "Target_Per_Hour"],
    [
        (1, 1, 101, 201, 301, "2026-11-23", 60),
        (2, 1, 102, 202, 301, "2026-11-23", 45),
        (3, 2, 101, 203, 302, "2026-11-23", 70),
    ],
)

insert_rows(
    "Production_Records",
    ["Production_ID", "Production_Date", "Line_ID", "Employee_ID", "Operation_ID",
     "Target_Quantity", "Actual_Quantity", "Shift"],
    [
        (1, "2026-11-23", 1, 101, 201, 120, 115, "Day"),
        (2, "2026-11-23", 1, 102, 202, 120, 105, "Day"),
        (3, "2026-11-23", 2, 101, 203, 120, 118, "Day"),
        (4, "2026-11-24", 1, 101, 201, 120, 122, "Day"),
        (5, "2026-11-24", 1, 102, 202, 120, 98, "Day"),
        (6, "2026-11-24", 2, 101, 203, 120, 110, "Day"),
    ],
)

conn.commit()
cur.close()
conn.close()
print("Sample data loaded.")