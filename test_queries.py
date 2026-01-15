import requests

base_url = "http://localhost:8001"

# Test queries
queries = [
    "INSERT INTO employees (name, role, department_id, salary) VALUES ('Jane Smith', 'Designer', 4, 75000);",
    "UPDATE employees SET salary = salary * 1.1 WHERE role = 'Engineer';",
    "DELETE FROM employees WHERE id = 106;",
    "SELECT * FROM employees;",
    "SELECT * FROM departments;"
]

for query in queries:
    print(f"\nExecuting: {query}")
    response = requests.post(f"{base_url}/databases/my_company/query",
                           json={"query": query})
    result = response.json()
    print(f"Success: {result.get('success')}")
    print(f"Message: {result.get('message')}")
    if result.get('data'):
        print(f"Rows returned: {len(result['data'])}")
        for row in result['data'][:3]:  # Show first 3 rows
            print(f"  {row}")
