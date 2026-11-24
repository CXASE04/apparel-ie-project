import sqlite3

conn = sqlite3.connect("apparel_ie.db")  # creates the file if it doesn't exist
conn.execute("PRAGMA foreign_keys = ON")  # SQLite needs this to enforce links

conn.executescript("""
DROP TABLE IF EXISTS Production_Records;
DROP TABLE IF EXISTS Line_Allocation;
DROP TABLE IF EXISTS Production_Line;
DROP TABLE IF EXISTS Operation_Details;
DROP TABLE IF EXISTS Machine_Details;
DROP TABLE IF EXISTS Employee_Details;

CREATE TABLE Employee_Details (
    Employee_ID    INTEGER PRIMARY KEY,
    Employee_Name  TEXT NOT NULL,
    Gender         TEXT,
    Designation    TEXT,
    Department     TEXT,
    Skill_Level    TEXT,
    Joining_Date   TEXT,
    Contact_No     TEXT
);

CREATE TABLE Production_Line (
    Line_ID             INTEGER PRIMARY KEY,
    Line_Name           TEXT NOT NULL,
    Product_Type        TEXT,
    Style_Number        TEXT,
    Working_Shift       TEXT,
    Available_Minutes   INTEGER,
    Line_Supervisor_ID  INTEGER REFERENCES Employee_Details(Employee_ID)
);

CREATE TABLE Machine_Details (
    Machine_ID        INTEGER PRIMARY KEY,
    Machine_Type      TEXT NOT NULL,
    Machine_Category  TEXT,
    Machine_Brand     TEXT,
    Machine_Model     TEXT,
    Machine_Status    TEXT
);

CREATE TABLE Operation_Details (
    Operation_ID           INTEGER PRIMARY KEY,
    Operation_Name         TEXT NOT NULL,
    Operation_Description  TEXT,
    Machine_Type           TEXT,
    SAM                    REAL,
    Operation_Sequence     INTEGER,
    Skill_Required         TEXT
);

CREATE TABLE Line_Allocation (
    Allocation_ID    INTEGER PRIMARY KEY,
    Line_ID          INTEGER REFERENCES Production_Line(Line_ID),
    Employee_ID      INTEGER REFERENCES Employee_Details(Employee_ID),
    Operation_ID     INTEGER REFERENCES Operation_Details(Operation_ID),
    Machine_ID       INTEGER REFERENCES Machine_Details(Machine_ID),
    Allocation_Date  TEXT,
    Target_Per_Hour  INTEGER
);

CREATE TABLE Production_Records (
    Production_ID    INTEGER PRIMARY KEY,
    Production_Date  TEXT,
    Line_ID          INTEGER REFERENCES Production_Line(Line_ID),
    Employee_ID      INTEGER REFERENCES Employee_Details(Employee_ID),
    Operation_ID     INTEGER REFERENCES Operation_Details(Operation_ID),
    Target_Quantity  INTEGER,
    Actual_Quantity  INTEGER,
    Shift            TEXT
);

INSERT INTO Employee_Details VALUES
 (101, 'Rahul', 'Male', 'Operator', 'Sewing', 'Semi-skilled', '2024-03-01', '9800000101'),
 (102, 'Priya', 'Female', 'Operator', 'Sewing', 'Skilled', '2023-07-15', '9800000102'),
 (103, 'Amit', 'Male', 'Supervisor', 'Sewing', 'Skilled', '2021-01-10', '9800000103'),
 (104, 'Sneha', 'Female', 'IE Executive', 'Industrial Engineering', 'Skilled', '2022-05-20', '9800000104');

INSERT INTO Production_Line VALUES
 (1, 'Line 01', 'Men''s formal shirts', 'SHRT-201', 'Day', 480, 103),
 (2, 'Line 02', 'Trousers', 'TRS-310', 'Day', 480, 103);

INSERT INTO Machine_Details VALUES
 (301, 'Single Needle Lockstitch', 'Lockstitch', 'Juki', 'DDL-8700', 'Active'),
 (302, 'Overlock Machine', 'Overlock', 'Brother', 'M-3000', 'Active'),
 (303, 'Button Attach Machine', 'Specialty', 'Juki', 'LBH-1790', 'Under Maintenance');

INSERT INTO Operation_Details VALUES
 (201, 'Shoulder Joining', 'Joining front and back shoulder panels', 'Single Needle Lockstitch', 0.45, 1, 'Basic'),
 (202, 'Sleeve Attaching', 'Attaching sleeve to armhole', 'Single Needle Lockstitch', 0.80, 2, 'Intermediate'),
 (203, 'Side Seam', 'Closing side seams', 'Overlock Machine', 0.65, 3, 'Basic'),
 (204, 'Button Attaching', 'Attaching buttons to placket', 'Button Attach Machine', 0.40, 4, 'Basic');

INSERT INTO Line_Allocation VALUES
 (1, 1, 101, 201, 301, '2026-11-23', 60),
 (2, 1, 102, 202, 301, '2026-11-23', 45),
 (3, 2, 101, 203, 302, '2026-11-23', 70);

INSERT INTO Production_Records VALUES
 (1, '2026-11-23', 1, 101, 201, 120, 115, 'Day'),
 (2, '2026-11-23', 1, 102, 202, 120, 105, 'Day'),
 (3, '2026-11-23', 2, 101, 203, 120, 118, 'Day'),
 (4, '2026-11-24', 1, 101, 201, 120, 122, 'Day'),
 (5, '2026-11-24', 1, 102, 202, 120, 98, 'Day'),
 (6, '2026-11-24', 2, 101, 203, 120, 110, 'Day');
""")

conn.commit()
conn.close()
print("Done: apparel_ie.db created with 6 tables and sample data.")