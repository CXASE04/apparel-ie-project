import sqlite3
from flask import Flask, request, redirect, url_for, flash, render_template_string

app = Flask(__name__)
app.secret_key = "apparel-ie-dev"  # needed for the short messages shown after actions
DB = "apparel_ie.db"


def get_conn():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def run_query(sql, params=()):
    # Runs a SELECT and returns the column names and rows
    conn = get_conn()
    cur = conn.execute(sql, params)
    headers = [col[0] for col in cur.description]
    rows = cur.fetchall()
    conn.close()
    return headers, rows


def run_write(sql, params=()):
    # Runs INSERT, UPDATE or DELETE and returns how many rows changed
    conn = get_conn()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def render_page(page, title, headers=None, rows=None):
    return render_template_string(PAGE, page=page, title=title, headers=headers, rows=rows)


PAGE = """
<!doctype html>
<html>
<head>
  <title>{{ title }}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 30px; }
    nav a { margin-right: 14px; }
    table { border-collapse: collapse; margin: 15px 0; }
    th, td { border: 1px solid #999; padding: 6px 12px; text-align: left; }
    th { background: #eee; }
    fieldset { margin: 12px 0; max-width: 750px; }
    input, button { margin: 3px; padding: 4px; }
    .msg { color: green; }
    .err { color: red; }
  </style>
</head>
<body>
  <h2>Apparel IE System</h2>
  <nav>
    <a href="/">Home</a>
    <a href="/employees">Employees</a>
    <a href="/line-efficiency">Line efficiency</a>
    <a href="/operator-efficiency">Operator efficiency</a>
    <a href="/production-by-date">Production by date</a>
    <a href="/production/add">Add production</a>
  </nav>
  <h3>{{ title }}</h3>

  {% for message in get_flashed_messages() %}
    <p class="{{ 'err' if message.startswith('Error') else 'msg' }}">{{ message }}</p>
  {% endfor %}

  {% if page == 'home' %}
    <p>Choose a page from the menu above.</p>
  {% endif %}

  {% if page == 'employees' %}
    <fieldset>
      <legend>Add employee</legend>
      <form method="post" action="/employees/add">
        <input name="emp_id" placeholder="Employee ID" required>
        <input name="name" placeholder="Name" required>
        <input name="designation" placeholder="Designation">
        <input name="department" placeholder="Department">
        <input name="skill" placeholder="Skill level">
        <input name="joining" type="date">
        <input name="contact" placeholder="Contact no">
        <button type="submit">Add</button>
      </form>
    </fieldset>
    <fieldset>
      <legend>Update designation</legend>
      <form method="post" action="/employees/update">
        <input name="emp_id" placeholder="Employee ID" required>
        <input name="designation" placeholder="New designation" required>
        <button type="submit">Update</button>
      </form>
    </fieldset>
    <fieldset>
      <legend>Delete employee</legend>
      <form method="post" action="/employees/delete">
        <input name="emp_id" placeholder="Employee ID" required>
        <button type="submit">Delete</button>
      </form>
    </fieldset>
  {% endif %}

  {% if page == 'production_by_date' %}
    <form method="get" action="/production-by-date">
      <input type="date" name="date" required>
      <button type="submit">Show</button>
    </form>
  {% endif %}

  {% if page == 'production_add' %}
    <fieldset>
      <legend>Add production record</legend>
      <form method="post" action="/production/add">
        <input name="prod_id" placeholder="Production ID (new, e.g. 7)" required><br>
        <input name="date" type="date" required><br>
        <input name="line_id" placeholder="Line ID (1 or 2)" required><br>
        <input name="emp_id" placeholder="Employee ID" required><br>
        <input name="op_id" placeholder="Operation ID (201-204)" required><br>
        <input name="target" placeholder="Target quantity" required><br>
        <input name="actual" placeholder="Actual quantity" required><br>
        <input name="shift" placeholder="Shift (Day/Night)" required><br>
        <button type="submit">Add record</button>
      </form>
    </fieldset>
  {% endif %}

  {% if headers %}
    <table>
      <tr>{% for h in headers %}<th>{{ h }}</th>{% endfor %}</tr>
      {% for row in rows %}
        <tr>{% for v in row %}<td>{{ v }}</td>{% endfor %}</tr>
      {% endfor %}
    </table>
    <p>({{ rows|length }} rows)</p>
  {% endif %}
</body>
</html>
"""


@app.route("/")
def home():
    return render_page("home", "Home")


@app.route("/employees")
def employees():
    headers, rows = run_query(
        "SELECT Employee_ID, Employee_Name, Designation, Department "
        "FROM Employee_Details ORDER BY Employee_ID"
    )
    return render_page("employees", "Employees", headers, rows)


@app.route("/employees/add", methods=["POST"])
def add_employee():
    f = request.form
    try:
        run_write(
            """INSERT INTO Employee_Details
               (Employee_ID, Employee_Name, Designation, Department,
                Skill_Level, Joining_Date, Contact_No)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (f["emp_id"], f["name"], f["designation"], f["department"],
             f["skill"], f["joining"], f["contact"]),
        )
        flash("Employee added.")
    except sqlite3.Error as err:
        flash(f"Error: could not add employee ({err})")
    return redirect(url_for("employees"))


@app.route("/employees/update", methods=["POST"])
def update_employee():
    try:
        changed = run_write(
            "UPDATE Employee_Details SET Designation = ? WHERE Employee_ID = ?",
            (request.form["designation"], request.form["emp_id"]),
        )
        flash("Designation updated." if changed else "Error: no employee found with that ID.")
    except sqlite3.Error as err:
        flash(f"Error: {err}")
    return redirect(url_for("employees"))


@app.route("/employees/delete", methods=["POST"])
def delete_employee():
    try:
        changed = run_write(
            "DELETE FROM Employee_Details WHERE Employee_ID = ?",
            (request.form["emp_id"],),
        )
        flash("Employee deleted." if changed else "Error: no employee found with that ID.")
    except sqlite3.Error as err:
        # Happens when the employee is still used in other tables
        flash(f"Error: could not delete employee ({err})")
    return redirect(url_for("employees"))


@app.route("/line-efficiency")
def line_efficiency():
    headers, rows = run_query("""
        SELECT pl.Line_Name, pl.Available_Minutes,
               ROUND(SUM(pr.Actual_Quantity * od.SAM), 2) AS Earned_Minutes,
               ROUND(SUM(pr.Actual_Quantity * od.SAM) * 100.0 / pl.Available_Minutes, 2)
                   AS Line_Efficiency_Pct
        FROM Production_Records pr
        JOIN Production_Line pl ON pr.Line_ID = pl.Line_ID
        JOIN Operation_Details od ON pr.Operation_ID = od.Operation_ID
        GROUP BY pl.Line_ID, pl.Line_Name, pl.Available_Minutes
    """)
    return render_page("line_efficiency", "Line efficiency", headers, rows)


@app.route("/operator-efficiency")
def operator_efficiency():
    headers, rows = run_query("""
        SELECT e.Employee_Name, pr.Production_Date,
               ROUND(SUM(pr.Actual_Quantity * od.SAM), 2) AS Earned_Minutes,
               ROUND(SUM(pr.Actual_Quantity * od.SAM) * 100.0 / 480, 2)
                   AS Operator_Efficiency_Pct
        FROM Production_Records pr
        JOIN Employee_Details e ON pr.Employee_ID = e.Employee_ID
        JOIN Operation_Details od ON pr.Operation_ID = od.Operation_ID
        GROUP BY e.Employee_Name, pr.Production_Date
        ORDER BY e.Employee_Name, pr.Production_Date
    """)
    return render_page("operator_efficiency", "Operator efficiency", headers, rows)


@app.route("/production-by-date")
def production_by_date():
    date = request.args.get("date")
    headers, rows = None, None
    if date:
        headers, rows = run_query("""
            SELECT e.Employee_Name, od.Operation_Name,
                   pr.Target_Quantity, pr.Actual_Quantity
            FROM Production_Records pr
            JOIN Employee_Details e ON pr.Employee_ID = e.Employee_ID
            JOIN Operation_Details od ON pr.Operation_ID = od.Operation_ID
            WHERE pr.Production_Date = ?
        """, (date,))
    return render_page("production_by_date", "Production by date", headers, rows)


@app.route("/production/add", methods=["GET", "POST"])
def add_production():
    if request.method == "POST":
        f = request.form
        try:
            run_write(
                """INSERT INTO Production_Records
                   (Production_ID, Production_Date, Line_ID, Employee_ID,
                    Operation_ID, Target_Quantity, Actual_Quantity, Shift)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (f["prod_id"], f["date"], f["line_id"], f["emp_id"],
                 f["op_id"], f["target"], f["actual"], f["shift"]),
            )
            flash("Production record added.")
        except sqlite3.Error as err:
            flash(f"Error: could not add production record ({err})")
        return redirect(url_for("add_production"))
    return render_page("production_add", "Add production record")


if __name__ == "__main__":
    app.run(debug=True)