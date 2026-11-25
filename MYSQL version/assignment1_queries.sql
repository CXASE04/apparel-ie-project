

USE apparel_ie;

-- Query 1: all employees
SELECT * FROM Employee_Details;

-- Query 2: selected columns, filtered by department
SELECT Employee_Name, Designation
FROM Employee_Details
WHERE Department = 'Sewing';

-- Query 3: employees sorted by joining date, newest first
SELECT Employee_Name, Joining_Date
FROM Employee_Details
ORDER BY Joining_Date DESC;

-- Query 4: achievement percentage per production record
SELECT
    e.Employee_Name,
    pr.Target_Quantity,
    pr.Actual_Quantity,
    ROUND(pr.Actual_Quantity * 100.0 / pr.Target_Quantity, 2) AS Achievement_Pct
FROM Production_Records pr
JOIN Employee_Details e
    ON pr.Employee_ID = e.Employee_ID
ORDER BY Achievement_Pct DESC;

-- Query 5: average achievement per employee
SELECT
    e.Employee_Name,
    COUNT(*) AS Records,
    ROUND(AVG(pr.Actual_Quantity * 100.0 / pr.Target_Quantity), 2) AS Avg_Achievement_Pct
FROM Production_Records pr
JOIN Employee_Details e
    ON pr.Employee_ID = e.Employee_ID
GROUP BY e.Employee_Name
ORDER BY Avg_Achievement_Pct DESC;

-- Query 6: Line Efficiency per production line
SELECT
    pl.Line_Name,
    pl.Available_Minutes,
    ROUND(SUM(pr.Actual_Quantity * od.SAM), 2) AS Earned_Minutes,
    ROUND(SUM(pr.Actual_Quantity * od.SAM) * 100.0 / pl.Available_Minutes, 2) AS Line_Efficiency_Pct
FROM Production_Records pr
JOIN Production_Line pl
    ON pr.Line_ID = pl.Line_ID
JOIN Operation_Details od
    ON pr.Operation_ID = od.Operation_ID
GROUP BY pl.Line_ID, pl.Line_Name, pl.Available_Minutes;

-- Query 7: Operator Efficiency per employee per day
SELECT
    e.Employee_Name,
    pr.Production_Date,
    ROUND(SUM(pr.Actual_Quantity * od.SAM), 2) AS Earned_Minutes,
    ROUND(SUM(pr.Actual_Quantity * od.SAM) * 100.0 / 480, 2) AS Operator_Efficiency_Pct
FROM Production_Records pr
JOIN Employee_Details e
    ON pr.Employee_ID = e.Employee_ID
JOIN Operation_Details od
    ON pr.Operation_ID = od.Operation_ID
GROUP BY e.Employee_Name, pr.Production_Date
ORDER BY e.Employee_Name, pr.Production_Date;

-- Query 8: production records that missed target
SELECT
    e.Employee_Name,
    od.Operation_Name,
    pr.Production_Date,
    pr.Target_Quantity,
    pr.Actual_Quantity,
    pr.Target_Quantity - pr.Actual_Quantity AS Shortfall
FROM Production_Records pr
JOIN Employee_Details e
    ON pr.Employee_ID = e.Employee_ID
JOIN Operation_Details od
    ON pr.Operation_ID = od.Operation_ID
WHERE pr.Actual_Quantity < pr.Target_Quantity
ORDER BY Shortfall DESC;

-- Query 9: average output per operation (uses HAVING)
SELECT
    od.Operation_Name,
    od.SAM,
    COUNT(*) AS Times_Run,
    ROUND(AVG(pr.Actual_Quantity), 1) AS Avg_Output
FROM Production_Records pr
JOIN Operation_Details od
    ON pr.Operation_ID = od.Operation_ID
GROUP BY od.Operation_Name, od.SAM
HAVING COUNT(*) >= 1
ORDER BY Avg_Output DESC;

-- Query 10: allocations per operation, including operations with none (LEFT JOIN)
SELECT
    od.Operation_Name,
    COUNT(la.Allocation_ID) AS Allocated_Count
FROM Operation_Details od
LEFT JOIN Line_Allocation la
    ON od.Operation_ID = la.Operation_ID
GROUP BY od.Operation_ID, od.Operation_Name
ORDER BY Allocated_Count DESC, od.Operation_Name;

--Query 11: auto increment of employee id  
ALTER TABLE Employee_Details MODIFY Employee_ID INT NOT NULL AUTO_INCREMENT;
Employee_ID    INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
