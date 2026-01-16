import requests
import json

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

if __name__ == "__main__":
    print("Testing RDBMS Challenge System...")
    print("=" * 60)

    for db_name, query in queries:
        success = execute_query(db_name, query)
        if not success:
            print(f"Query failed: {query}")
            break
