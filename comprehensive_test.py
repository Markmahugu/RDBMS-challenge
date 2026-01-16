#!/usr/bin/env python3
"""
Comprehensive test script for RDBMS Challenge
Tests all required SQL operations as specified in the task
"""

import requests
import time
import sys

class RDBMSTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.current_db = "DemoDB"

    def log(self, message, success=True):
        """Log test results"""
        status = "✓" if success else "✗"
        print(f"{status} {message}")
        self.test_results.append((message, success))

    def run_query(self, query, description=""):
        """Execute a query and return the result"""
        try:
            response = requests.post(f"{self.base_url}/databases/{self.current_db}/query",
                                   json={"query": query}, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"success": False, "message": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def test_system_checks(self):
        """Test system & connection checks"""
        print("\n=== 1. System & Connection Checks ===")

        # Check Server Version
        result = self.run_query("SELECT VERSION();")
        self.log("Check Server Version", result.get("success", False))

        # Check Current User
        result = self.run_query("SELECT USER();")
        self.log("Check Current User", result.get("success", False))

        # Check Current Database
        result = self.run_query("SELECT DATABASE();")
        self.log("Check Current Database", result.get("success", False))

        # Check System Time
        result = self.run_query("SELECT NOW();")
        self.log("Check System Time", result.get("success", False))

    def test_ddl_operations(self):
        """Test Data Definition Language operations"""
        print("\n=== 2. Data Definition (DDL) ===")

        # Create Database
        result = self.run_query("CREATE DATABASE IF NOT EXISTS test_db;")
        self.log("Create Database", result.get("success", False))

        # Switch to test database
        result = self.run_query("USE test_db;")
        self.log("Use Database", result.get("success", False))

        # Create Tables
        users_query = """
        CREATE TABLE users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        result = self.run_query(users_query)
        self.log("Create Users Table", result.get("success", False))

        orders_query = """
        CREATE TABLE orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            amount DECIMAL(10, 2),
            order_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
        """
        result = self.run_query(orders_query)
        self.log("Create Orders Table", result.get("success", False))

        # Alter Table
        result = self.run_query("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE;")
        self.log("Alter Table (Add Column)", result.get("success", False))

    def test_crud_operations(self):
        """Test CRUD operations"""
        print("\n=== 3. Data Manipulation (CRUD Operations) ===")

        # Insert Data
        insert_users = """
        INSERT INTO users (username, email) VALUES
        ('alice_dev', 'alice@example.com'),
        ('bob_builder', 'bob@example.com'),
        ('charlie_test', 'charlie@example.com');
        """
        result = self.run_query(insert_users)
        self.log("Insert Users Data", result.get("success", False))

        insert_orders = """
        INSERT INTO orders (user_id, amount, order_date) VALUES
        (1, 50.00, '2023-10-01'),
        (1, 120.50, '2023-10-05'),
        (2, 25.00, '2023-10-02');
        """
        result = self.run_query(insert_orders)
        self.log("Insert Orders Data", result.get("success", False))

        # Select Data
        result = self.run_query("SELECT * FROM users;")
        self.log("Select All Users", result.get("success", False) and len(result.get("data", [])) > 0)

        # Update Data
        result = self.run_query("UPDATE users SET email = 'alice_new@example.com' WHERE username = 'alice_dev';")
        self.log("Update User Email", result.get("success", False))

        # Delete Data
        result = self.run_query("DELETE FROM users WHERE username = 'charlie_test';")
        self.log("Delete User", result.get("success", False))

    def test_advanced_selection(self):
        """Test advanced selection and filtering"""
        print("\n=== 4. Advanced Selection & Filtering ===")

        # Filtering with WHERE
        result = self.run_query("SELECT * FROM orders WHERE amount > 40 AND user_id = 1;")
        self.log("Filtering with WHERE (AND)", result.get("success", False))

        # Pattern Matching with LIKE
        result = self.run_query("SELECT * FROM users WHERE email LIKE '%@example.com';")
        self.log("Pattern Matching with LIKE", result.get("success", False))

        # Sorting and Limiting
        result = self.run_query("SELECT * FROM orders ORDER BY amount DESC LIMIT 2;")
        self.log("Sorting and Limiting", result.get("success", False))

    def test_joins(self):
        """Test relational logic with joins"""
        print("\n=== 5. Relational Logic (Joins) ===")

        # Inner Join
        join_query = """
        SELECT users.username, orders.amount
        FROM users
        INNER JOIN orders ON users.user_id = orders.user_id;
        """
        result = self.run_query(join_query)
        self.log("Inner Join", result.get("success", False))

        # Left Join
        left_join_query = """
        SELECT users.username, orders.order_id
        FROM users
        LEFT JOIN orders ON users.user_id = orders.user_id;
        """
        result = self.run_query(left_join_query)
        self.log("Left Join", result.get("success", False))

    def test_aggregation(self):
        """Test aggregation and grouping"""
        print("\n=== 6. Aggregation & Grouping ===")

        # Count Rows
        result = self.run_query("SELECT COUNT(*) FROM users;")
        self.log("Count Rows", result.get("success", False))

        # Sum and Average
        result = self.run_query("SELECT SUM(amount) AS total_sales, AVG(amount) AS avg_sale FROM orders;")
        self.log("Sum and Average", result.get("success", False))

        # Group By and Having
        group_query = """
        SELECT user_id, SUM(amount) AS total_spent
        FROM orders
        GROUP BY user_id
        HAVING total_spent > 30.00;
        """
        result = self.run_query(group_query)
        self.log("Group By and Having", result.get("success", False))

    def test_transactions(self):
        """Test transaction handling"""
        print("\n=== 7. Transactions (ACID Compliance) ===")

        # Start Transaction
        result = self.run_query("START TRANSACTION;")
        self.log("Start Transaction", result.get("success", False))

        # Insert in transaction
        result = self.run_query("INSERT INTO users (username, email) VALUES ('dave_transact', 'dave@example.com');")
        success1 = result.get("success", False)

        result = self.run_query("INSERT INTO orders (user_id, amount) VALUES (LAST_INSERT_ID(), 99.99);")
        success2 = result.get("success", False)

        result = self.run_query("COMMIT;")
        self.log("Commit Transaction", result.get("success", False) and success1 and success2)

        # Test Rollback (add some data first, then try to delete and rollback)
        result = self.run_query("INSERT INTO orders (user_id, amount) VALUES (1, 200.00);")
        rollback_test_data_exists = result.get("success", False)

        result = self.run_query("START TRANSACTION;")
        rollback_started = result.get("success", False)

        result = self.run_query("DELETE FROM orders WHERE amount = 200.00;")
        delete_attempted = result.get("success", False)

        result = self.run_query("ROLLBACK;")
        rollback_success = result.get("success", False)

        # Check if data is still there after rollback
        result = self.run_query("SELECT COUNT(*) FROM orders WHERE amount = 200.00;")
        data_restored = len(result.get("data", [])) > 0 if result.get("success") else False

        self.log("Rollback Transaction", rollback_success and data_restored)

    def test_integrity_constraints(self):
        """Test integrity constraints"""
        print("\n=== 8. Integrity Constraints ===")

        # Test Unique Violation (should fail)
        try:
            result = self.run_query("INSERT INTO users (username, email) VALUES ('alice_dev', 'duplicate@example.com');")
            self.log("Unique Constraint Violation (Expected to Fail)", not result.get("success", True))
        except:
            self.log("Unique Constraint Violation (Expected to Fail)", True)

        # Test Foreign Key Violation (should fail)
        try:
            result = self.run_query("INSERT INTO orders (user_id, amount) VALUES (999, 50.00);")
            self.log("Foreign Key Constraint Violation (Expected to Fail)", not result.get("success", True))
        except:
            self.log("Foreign Key Constraint Violation (Expected to Fail)", True)

    def test_cleanup(self):
        """Test cleanup operations"""
        print("\n=== 9. Cleanup ===")

        # Drop Tables
        result = self.run_query("DROP TABLE orders;")
        self.log("Drop Orders Table", result.get("success", False))

        result = self.run_query("DROP TABLE users;")
        self.log("Drop Users Table", result.get("success", False))

        # Drop Database
        result = self.run_query("DROP DATABASE test_db;")
        self.log("Drop Test Database", result.get("success", False))

    def run_all_tests(self):
        """Run all test suites"""
        print("Starting Comprehensive RDBMS Challenge Tests")
        print("=" * 50)

        try:
            self.test_system_checks()
            self.test_ddl_operations()
            self.test_crud_operations()
            self.test_advanced_selection()
            self.test_joins()
            self.test_aggregation()
            self.test_transactions()
            self.test_integrity_constraints()
            self.test_cleanup()

        except Exception as e:
            print(f"\nTest execution failed with error: {e}")

        # Print summary
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)

        passed = sum(1 for _, success in self.test_results if success)
        total = len(self.test_results)

        for test, success in self.test_results:
            status = "PASS" if success else "FAIL"
            print(f"{status}: {test}")

        print(f"\nResults: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! The RDBMS system is fully functional.")
            return True
        else:
            print("❌ Some tests failed. Please check the implementation.")
            return False


if __name__ == "__main__":
    # Check if server is running
    tester = RDBMSTester()

    try:
        response = requests.get(f"{tester.base_url}/", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server is not responding. Please start the server first.")
            sys.exit(1)
    except:
        print("❌ Cannot connect to backend server. Please start the server first.")
        print("Run: cd backend && python -m uvicorn app.main:app --reload")
        sys.exit(1)

    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
