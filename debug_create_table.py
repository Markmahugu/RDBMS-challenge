#!/usr/bin/env python3
import requests

base_url = "http://localhost:8000"

# Test CREATE TABLE in DemoDB
query = """
CREATE TABLE test_orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    amount DECIMAL(10, 2),
    order_date DATE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
"""

print(f"Executing: {query.strip()}")
try:
    response = requests.post(f"{base_url}/databases/DemoDB/query",
                           json={"query": query})
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        if result.get('data'):
            print(f"Data: {result['data']}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
