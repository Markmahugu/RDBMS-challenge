#!/usr/bin/env python3
import requests

base_url = "http://localhost:8000"

# Test system functions
queries = [
    "SELECT VERSION();",
    "SELECT USER();",
    "SELECT DATABASE();",
    "SELECT NOW();"
]

for query in queries:
    print(f"\nExecuting: {query}")
    try:
        response = requests.post(f"{base_url}/databases/my_company/query",
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
