#!/usr/bin/env python3

import re

def _clean_sql_query(query: str) -> str:
    """Remove SQL comments from query"""
    # Remove single-line comments (--)
    query = re.sub(r'--.*', '', query)
    # Remove multi-line comments (/* */)
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
    # Remove extra whitespace and empty lines
    lines = [line.strip() for line in query.split('\n') if line.strip()]
    return '\n'.join(lines)

# Test the cleaning function
test_query = """-- 1. Create the Department table
CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(50)
);

-- 2. Create the Employees table
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    dept_id INT -- This is the 'Foreign Key' that links to the table above
);

-- 3. Insert data
INSERT INTO departments (dept_id, dept_name)
VALUES (101, 'Engineering'), (102, 'Marketing'), (103, 'HR');

INSERT INTO employees (emp_id, first_name, dept_id)
VALUES
    (1, 'Alice', 101),   -- Alice is in Engineering
    (2, 'Bob', 102),     -- Bob is in Marketing
    (3, 'Charlie', 101), -- Charlie is in Engineering
    (4, 'David', NULL);  -- David has no department assigned yet"""

cleaned = _clean_sql_query(test_query)
print("CLEANED QUERY:")
print(repr(cleaned))
print("\nSTATEMENTS:")
statements = [stmt.strip() for stmt in cleaned.split(';') if stmt.strip()]
for i, stmt in enumerate(statements):
    print(f"{i+1}: {repr(stmt)}")
