import requests
import json
import pytest

BASE_URL = "http://127.0.0.1:8001"

def execute_query(database_name, query):
    url = f"{BASE_URL}/databases/{database_name}/query"
    payload = {"query": query}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Query: {query}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success')}")
            print(f"Message: {result.get('message')}")
            if 'data' in result and result['data']:
                print("Data:")
                for row in result['data']:
                    print(f"  {row}")
            if 'affectedRows' in result:
                print(f"Affected Rows: {result['affectedRows']}")
        else:
            print(f"Error: {response.text}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Exception: {e}")
        return False

# First, try to drop the test database if it exists
print("Dropping test database if exists...")
response = requests.delete(f"{BASE_URL}/databases/test_db")
print(f"Drop DB Status: {response.status_code}")

# Create the test database
print("Creating test database...")
response = requests.post(f"{BASE_URL}/databases", json={"name": "test_db"})
print(f"Create DB Status: {response.status_code}")
if response.status_code == 200:
    print("Database created successfully")
else:
    print(f"Error creating database: {response.text}")

# Test queries
queries = [
    # Create tables
    ("test_db", """CREATE TABLE users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );"""),
    ("test_db", """CREATE TABLE orders (
        order_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        amount DECIMAL(10, 2),
        order_date DATE,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    );"""),
    # Alter table
    ("test_db", "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;"),
    # Insert data
    ("test_db", """INSERT INTO users (username, email) VALUES
    ('alice_dev', 'alice@example.com'),
    ('bob_builder', 'bob@example.com'),
    ('charlie_test', 'charlie@example.com');"""),
    ("test_db", """INSERT INTO orders (user_id, amount, order_date) VALUES
    (1, 50.00, '2023-10-01'),
    (1, 120.50, '2023-10-05'),
    (2, 25.00, '2023-10-02');"""),
    # Select all users
    ("test_db", "SELECT * FROM users;"),
    # Update data
    ("test_db", "UPDATE users SET email = 'alice_new@example.com' WHERE username = 'alice_dev';"),
    # Select with WHERE
    ("test_db", "SELECT * FROM orders WHERE amount > 40 AND user_id = 1;"),
    # Select with LIKE
    ("test_db", "SELECT * FROM users WHERE email LIKE '%@example.com';"),
    # Select with ORDER BY and LIMIT
    ("test_db", "SELECT * FROM orders ORDER BY amount DESC LIMIT 2;"),
    # Delete data
    ("test_db", "DELETE FROM users WHERE username = 'charlie_test';"),
    # Final select to verify
    ("test_db", "SELECT * FROM users;"),
    ("test_db", "SELECT * FROM orders;")
]

def test_where_clause_compound_conditions():
    """Test compound WHERE conditions with AND/OR logic"""
    print("\nTesting Compound WHERE Conditions...")
    print("=" * 60)

    # Test data setup - use the existing test_db
    setup_queries = [
        ("test_db", """CREATE TABLE test_orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            amount DECIMAL(10, 2),
            status VARCHAR(20)
        );"""),
        ("test_db", """INSERT INTO test_orders (user_id, amount, status) VALUES
            (1, 50.00, 'completed'),
            (1, 120.50, 'pending'),
            (2, 25.00, 'completed'),
            (2, 75.00, 'completed'),
            (3, 30.00, 'cancelled');""")
    ]

    # Execute setup
    for db_name, query in setup_queries:
        success = execute_query(db_name, query)
        if not success:
            print(f"Setup failed: {query}")
            return False

    # Test cases for compound WHERE conditions
    test_cases = [
        # AND conditions - should return only rows that satisfy BOTH conditions
        {
            "query": "SELECT * FROM test_orders WHERE amount > 40 AND user_id = 1;",
            "expected_rows": 2,  # user_id=1, amount=50.00 and user_id=1, amount=120.50
            "description": "AND condition: amount > 40 AND user_id = 1"
        },
        {
            "query": "SELECT * FROM test_orders WHERE amount > 100 AND status = 'pending';",
            "expected_rows": 1,  # user_id=1, amount=120.50, status='pending'
            "description": "AND condition: amount > 100 AND status = 'pending'"
        },
        {
            "query": "SELECT * FROM test_orders WHERE amount < 60 AND status = 'completed';",
            "expected_rows": 2,  # user_id=1, amount=50.00 and user_id=2, amount=25.00
            "description": "AND condition: amount < 60 AND status = 'completed'"
        },

        # OR conditions - should return rows that satisfy EITHER condition
        {
            "query": "SELECT * FROM test_orders WHERE user_id = 1 OR amount > 100;",
            "expected_rows": 2,  # user_id=1 matches 2 rows, amount>100 matches 1 row (already included)
            "description": "OR condition: user_id = 1 OR amount > 100"
        },
        {
            "query": "SELECT * FROM test_orders WHERE status = 'cancelled' OR status = 'pending';",
            "expected_rows": 2,  # status='cancelled' and status='pending'
            "description": "OR condition: status = 'cancelled' OR status = 'pending'"
        },

        # Mixed conditions (though simplified implementation treats as AND)
        {
            "query": "SELECT * FROM test_orders WHERE amount > 30 AND user_id = 2 AND status = 'completed';",
            "expected_rows": 1,  # user_id=2, amount=75.00, status='completed'
            "description": "Multiple AND conditions"
        },

        # Edge case: conditions that should return no rows
        {
            "query": "SELECT * FROM test_orders WHERE amount > 200 AND user_id = 1;",
            "expected_rows": 0,  # No rows satisfy both conditions
            "description": "AND condition with no matching rows: amount > 200 AND user_id = 1"
        },
        {
            "query": "SELECT * FROM test_orders WHERE user_id = 999 OR amount < 0;",
            "expected_rows": 0,  # No rows satisfy either condition
            "description": "OR condition with no matching rows: user_id = 999 OR amount < 0"
        }
    ]

    all_passed = True
    for test_case in test_cases:
        print(f"\nTesting: {test_case['description']}")
        print(f"Query: {test_case['query']}")

        # Execute query
        url = f"{BASE_URL}/databases/test_db/query"
        payload = {"query": test_case['query']}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                actual_rows = len(result.get('data', []))
                expected_rows = test_case['expected_rows']

                if actual_rows == expected_rows:
                    print(f"✓ PASS: Expected {expected_rows} rows, got {actual_rows}")
                else:
                    print(f"✗ FAIL: Expected {expected_rows} rows, got {actual_rows}")
                    print(f"Data returned: {result.get('data', [])}")
                    all_passed = False
            else:
                print(f"✗ FAIL: Query failed with status {response.status_code}")
                print(f"Error: {response.text}")
                all_passed = False
        except Exception as e:
            print(f"✗ FAIL: Exception {e}")
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("Testing RDBMS Challenge System...")
    print("=" * 60)

    # Run main test suite
    main_success = True
    for db_name, query in queries:
        success = execute_query(db_name, query)
        if not success:
            print(f"Query failed: {query}")
            main_success = False
            break

    # Run compound WHERE condition tests
    where_tests_success = test_where_clause_compound_conditions()

    if main_success and where_tests_success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        if not main_success:
            print("- Main test suite failed")
        if not where_tests_success:
            print("- Compound WHERE condition tests failed")
