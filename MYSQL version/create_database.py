import mysql.connector

HOST = "localhost"
USER = "root"
PASSWORD = "passwordhere"  # Replace with your MySQL root password
DB_NAME = "apparel_ie"

# Step A: connect to the MySQL server and create the database
conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD)
cur = conn.cursor()
cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
conn.commit()
cur.close()
conn.close()

# Step B: connect to our database and create the six core tables
conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DB_NAME)
cur = conn.cursor()

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS Employee_Details (
        Employee_ID    INT PRIMARY KEY,
        Employee_Name  VARCHAR(100) NOT NULL,
        Gender         VARCHAR(10),
        Designation    VARCHAR(50),
        Department     VARCHAR(50),
        Skill_Level    VARCHAR(20),
        Joining_Date   DATE,
        Contact_No     VARCHAR(15)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Production_Line (
        Line_ID             INT PRIMARY KEY,
        Line_Name           VARCHAR(50) NOT NULL,
        Product_Type        VARCHAR(50),
        Style_Number        VARCHAR(30),
        Working_Shift       VARCHAR(20),
        Available_Minutes   INT,
        Line_Supervisor_ID  INT,
        FOREIGN KEY (Line_Supervisor_ID) REFERENCES Employee_Details(Employee_ID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Machine_Details (
        Machine_ID        INT PRIMARY KEY,
        Machine_Type      VARCHAR(60) NOT NULL,
        Machine_Category  VARCHAR(50),
        Machine_Brand     VARCHAR(50),
        Machine_Model     VARCHAR(50),
        Machine_Status    VARCHAR(20)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Operation_Details (
        Operation_ID           INT PRIMARY KEY,
        Operation_Name         VARCHAR(80) NOT NULL,
        Operation_Description  VARCHAR(255),
        Machine_Type           VARCHAR(60),
        SAM                    DECIMAL(5,2),
        Operation_Sequence     INT,
        Skill_Required         VARCHAR(50)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Line_Allocation (
        Allocation_ID    INT PRIMARY KEY,
        Line_ID          INT,
        Employee_ID      INT,
        Operation_ID     INT,
        Machine_ID       INT,
        Allocation_Date  DATE,
        Target_Per_Hour  INT,
        FOREIGN KEY (Line_ID)      REFERENCES Production_Line(Line_ID),
        FOREIGN KEY (Employee_ID)  REFERENCES Employee_Details(Employee_ID),
        FOREIGN KEY (Operation_ID) REFERENCES Operation_Details(Operation_ID),
        FOREIGN KEY (Machine_ID)   REFERENCES Machine_Details(Machine_ID)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS Production_Records (
        Production_ID    INT PRIMARY KEY,
        Production_Date  DATE,
        Line_ID          INT,
        Employee_ID      INT,
        Operation_ID     INT,
        Target_Quantity  INT,
        Actual_Quantity  INT,
        Shift            VARCHAR(20),
        FOREIGN KEY (Line_ID)      REFERENCES Production_Line(Line_ID),
        FOREIGN KEY (Employee_ID)  REFERENCES Employee_Details(Employee_ID),
        FOREIGN KEY (Operation_ID) REFERENCES Operation_Details(Operation_ID)
    )
    """,
]

for sql in TABLES:
    cur.execute(sql)

conn.commit()
cur.close()
conn.close()
print("Done: database apparel_ie and 6 tables created.")