import time
import re
import os
import json
from typing import Dict, List, Any, Optional
from .models import (
    DatabaseState, TableSchema, ColumnSchema, QueryResult,
    ExecutionPlanNode, DataType, IndexSchema
)


class DatabaseEngine:
    def __init__(self):
        self.storage_path = 'rdbms_storage.json'
        self.databases: Dict[str, DatabaseState] = {}
        self.current_db_name: Optional[str] = None
        self._load_state_from_disk()

    def _clean_sql_query(self, query: str) -> str:
        """Removes SQL comments and normalizes whitespace in the query string."""
        # Remove single-line comments (--)
        query = re.sub(r'--.*', '', query)
        # Remove multi-line comments (/* */)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        # Remove extra whitespace and empty lines
        lines = [line.strip() for line in query.split('\n') if line.strip()]
        return '\n'.join(lines)

    def reset_database(self) -> None:
        """Resets the database to an empty state."""
        self.databases = {
            'DemoDB': DatabaseState(
                name='DemoDB',
                tables=[]
            )
        }
        self._save_state_to_disk()

    def _initialize_default_database(self) -> None:
        """Creates the default my_company database with departments and employees tables."""
        # Create the database
        self.databases = {
            'my_company': DatabaseState(
                name='my_company',
                tables=[]
            )
        }

        # Get the database
        db = self.databases['my_company']

        # Departments table
        dept_table = TableSchema(
            id='departments',
            name='departments',
            columns=[
                ColumnSchema(id='dept_id', name='dept_id', type='INT', nullable=False, isPrimaryKey=True, autoIncrement=True),
                ColumnSchema(id='dept_name', name='dept_name', type='VARCHAR', length=50, nullable=False)
            ],
            indexes=[],
            rows=[
                {'dept_id': 101, 'dept_name': 'Engineering'},
                {'dept_id': 102, 'dept_name': 'Marketing'},
                {'dept_id': 103, 'dept_name': 'HR'}
            ]
        )

        # Employees table - with correct column names to match user's queries
        emp_table = TableSchema(
            id='employees',
            name='employees',
            columns=[
                ColumnSchema(id='emp_id', name='id', type='INT', nullable=False, isPrimaryKey=True, autoIncrement=True),
                ColumnSchema(id='emp_name', name='name', type='VARCHAR', length=50, nullable=False),
                ColumnSchema(id='emp_role', name='role', type='VARCHAR', length=50, nullable=False),
                ColumnSchema(id='emp_dept_id', name='department_id', type='INT', nullable=True),
                ColumnSchema(id='emp_salary', name='salary', type='DECIMAL', nullable=False)
            ],
            indexes=[],
            rows=[]
        )

        db.tables = [dept_table, emp_table]
        self._save_state_to_disk()

    def _load_state_from_disk(self) -> None:
        """Loads the entire database state from the JSON storage file."""
        if not os.path.exists(self.storage_path):
            self._initialize_default_database()
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            self.databases = {name: DatabaseState(**db_data) for name, db_data in data.items()}
            if self.databases:
                self.current_db_name = list(self.databases.keys())[0]
            else:
                self._initialize_default_database()
        except (json.JSONDecodeError, TypeError):
            self._initialize_default_database()

    def _save_state_to_disk(self) -> None:
        """Serializes the entire database state and writes it to the JSON file."""
        serializable_data = {name: db.model_dump() for name, db in self.databases.items()}
        with open(self.storage_path, 'w') as f:
            json.dump(serializable_data, f, indent=4)

    def _seed_demo_data(self, db_name: str) -> None:
        """Creates demonstration tables populated with sample data for testing purposes."""
        db = self.databases[db_name]

        # Departments table
        dept_table = TableSchema(
            id='departments',
            name='departments',
            columns=[
                ColumnSchema(id='d1', name='id', type='INT', nullable=False, isPrimaryKey=True),
                ColumnSchema(id='d2', name='name', type='VARCHAR', length=100, nullable=False),
                ColumnSchema(id='d3', name='location', type='VARCHAR', length=100, nullable=True)
            ],
            indexes=[],
            rows=[
                {'id': 1, 'name': 'Engineering', 'location': 'Building A'},
                {'id': 2, 'name': 'HR', 'location': 'Building B'},
                {'id': 3, 'name': 'Sales', 'location': 'Building C'},
                {'id': 4, 'name': 'Marketing', 'location': 'Building A'}
            ]
        )

        # Employees table
        emp_table = TableSchema(
            id='employees',
            name='employees',
            columns=[
                ColumnSchema(id='e1', name='id', type='INT', nullable=False, isPrimaryKey=True),
                ColumnSchema(id='e2', name='name', type='VARCHAR', length=100, nullable=False),
                ColumnSchema(id='e3', name='role', type='VARCHAR', length=50, nullable=False),
                ColumnSchema(id='e4', name='department_id', type='INT', nullable=True, isForeignKey=True,
                           references={'tableId': 'departments', 'columnId': 'd1'}),
                ColumnSchema(id='e5', name='salary', type='DECIMAL', nullable=False)
            ],
            indexes=[IndexSchema(id='idx_emp_dept', name='idx_department_id', columnIds=['e4'], type='BTREE')],
            rows=[
                {'id': 101, 'name': 'Alice Johnson', 'role': 'Senior Engineer', 'department_id': 1, 'salary': 95000},
                {'id': 102, 'name': 'Bob Smith', 'role': 'Product Manager', 'department_id': 1, 'salary': 105000},
                {'id': 103, 'name': 'Charlie Brown', 'role': 'HR Specialist', 'department_id': 2, 'salary': 65000},
                {'id': 104, 'name': 'Diana Prince', 'role': 'Sales Lead', 'department_id': 3, 'salary': 85000},
                {'id': 105, 'name': 'Evan Wright', 'role': 'Engineer', 'department_id': 1, 'salary': 75000}
            ]
        )

        # Projects table
        proj_table = TableSchema(
            id='projects',
            name='projects',
            columns=[
                ColumnSchema(id='p1', name='id', type='INT', nullable=False, isPrimaryKey=True),
                ColumnSchema(id='p2', name='name', type='VARCHAR', length=100, nullable=False),
                ColumnSchema(id='p3', name='budget', type='DECIMAL', nullable=True)
            ],
            indexes=[],
            rows=[
                {'id': 1, 'name': 'Project Alpha', 'budget': 50000},
                {'id': 2, 'name': 'Project Beta', 'budget': 120000},
                {'id': 3, 'name': 'Website Redesign', 'budget': 30000}
            ]
        )

        db.tables = [dept_table, emp_table, proj_table]

    def get_database_state(self) -> DatabaseState:
        """Retrieves the current state of the database."""
        return self.databases[self.current_db_name]

    def create_database(self, name: str) -> None:
        """Creates a new database with the specified name."""
        if name in self.databases:
            raise ValueError(f"Database '{name}' already exists")
        self.databases[name] = DatabaseState(name=name, tables=[])
        self.current_db_name = name
        self._save_state_to_disk()

    def drop_database(self, name: str) -> None:
        """Drops (deletes) the specified database."""
        if name not in self.databases:
            raise ValueError(f"Database '{name}' does not exist")
        if name == self.current_db_name:
            # Switch to another database if we're deleting the current one
            remaining_dbs = [db_name for db_name in self.databases.keys() if db_name != name]
            if remaining_dbs:
                self.current_db_name = remaining_dbs[0]
            else:
                # If no databases left, create a default one
                self.current_db_name = 'DemoDB'
                self.reset_database()
                return
        del self.databases[name]
        self._save_state_to_disk()

    def create_table(self, table: TableSchema) -> None:
        """Creates a new table in the current database."""
        db = self.databases[self.current_db_name]
        if any(t.name == table.name for t in db.tables):
            raise ValueError(f"Table '{table.name}' already exists")

        # Validate initial rows for integrity constraints
        for row in table.rows:
            self._check_integrity_constraints(table, row, is_insert=False)

        db.tables.append(table)
        self._save_state_to_disk()

    def update_table(self, old_name: str, new_table: TableSchema) -> None:
        """Updates an existing table schema and migrates existing data accordingly."""
        db = self.databases[self.current_db_name]
        table_index = next((i for i, t in enumerate(db.tables) if t.name == old_name), -1)

        if table_index == -1:
            # Create if not exists
            self.create_table(new_table)
            return

        old_table = db.tables[table_index]

        # Check for name conflicts
        if old_name != new_table.name and any(t.name == new_table.name for t in db.tables):
            raise ValueError(f"Table '{new_table.name}' already exists")

        # Migrate data based on column IDs and names
        new_rows = []
        for old_row in old_table.rows:
            new_row = {}
            for new_col in new_table.columns:
                # Try to match by ID first, then by name
                old_col = next((c for c in old_table.columns if c.id == new_col.id), None)
                if old_col:
                    new_row[new_col.name] = old_row[old_col.name]
                elif new_col.name in old_row:
                    new_row[new_col.name] = old_row[new_col.name]
                else:
                    new_row[new_col.name] = new_col.defaultValue if new_col.defaultValue is not None else None
            new_rows.append(new_row)

        new_table.rows = new_rows

        # Validate migrated rows for integrity constraints
        for row in new_table.rows:
            self._check_integrity_constraints(new_table, row, is_insert=False)

        db.tables[table_index] = new_table
        self._save_state_to_disk()

    def drop_table(self, table_name: str) -> None:
        """Removes the specified table from the current database."""
        db = self.databases[self.current_db_name]
        db.tables = [t for t in db.tables if t.name != table_name]
        self._save_state_to_disk()

    def execute_sql(self, query: str) -> QueryResult:
        """Executes the provided SQL query and returns the result."""
        start_time = time.time()

        try:
            # Clean the query by removing comments
            query = self._clean_sql_query(query)

            # Split query into individual statements
            statements = [stmt.strip() for stmt in query.split(';') if stmt.strip()]

            results = []
            for stmt in statements:
                stmt = stmt.strip()
                if not stmt:
                    continue

                q = stmt.upper()

                if q.startswith('SELECT'):
                    result = self._handle_select(stmt, start_time)
                elif q.startswith('INSERT'):
                    result = self._handle_insert(stmt, start_time)
                elif q.startswith('UPDATE'):
                    result = self._handle_update(stmt, start_time)
                elif q.startswith('DELETE'):
                    result = self._handle_delete(stmt, start_time)
                elif q.startswith('CREATE DATABASE'):
                    result = self._handle_create_database(stmt, start_time)
                elif q.startswith('CREATE TABLE'):
                    result = self._handle_create_table(stmt, start_time)
                elif q.startswith('ALTER TABLE'):
                    result = self._handle_alter_table(stmt, start_time)
                elif q.startswith('DROP DATABASE'):
                    result = self._handle_drop_database(stmt, start_time)
                elif q.startswith('DROP TABLE'):
                    parts = stmt.split()
                    table_name = parts[2].replace(';', '').strip()
                    self.drop_table(table_name)
                    result = QueryResult(
                        success=True,
                        message=f'Table {table_name} dropped',
                        executionTime=time.time() - start_time
                    )
                elif q.startswith('USE'):
                    result = self._handle_use_database(stmt, start_time)
                elif q.startswith('START TRANSACTION'):
                    result = self._handle_start_transaction(stmt, start_time)
                elif q.startswith('COMMIT'):
                    result = self._handle_commit(stmt, start_time)
                elif q.startswith('ROLLBACK'):
                    result = self._handle_rollback(stmt, start_time)
                else:
                    raise ValueError("Unsupported SQL command")

                results.append(result)
                if not result.success:
                    break

            # Return the last result or a combined success message
            if len(results) == 1:
                return results[0]
            elif all(r.success for r in results):
                total_time = time.time() - start_time
                return QueryResult(
                    success=True,
                    message=f"{len(results)} statements executed successfully",
                    executionTime=total_time
                )
            else:
                failed_result = next((r for r in results if not r.success), None)
                return failed_result or QueryResult(
                    success=False,
                    message="Multiple statement execution failed",
                    executionTime=time.time() - start_time
                )

        except Exception as e:
            return QueryResult(
                success=False,
                message=str(e),
                executionTime=time.time() - start_time
            )

    def _handle_select(self, query: str, start_time: float) -> QueryResult:
        """Processes SELECT queries, including joins, filters, ordering, and limits."""
        db = self.databases[self.current_db_name]

        # Check for system functions first
        func_result = self._handle_select_functions(query, start_time)
        if func_result:
            return func_result

        # Parse FROM clause
        from_match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if not from_match:
            raise ValueError("Missing FROM clause")

        table_name = from_match.group(1)
        table = next((t for t in db.tables if t.name == table_name), None)
        if not table:
            raise ValueError(f"Table '{table_name}' not found")

        result_data = []
        for row in table.rows:
            new_row = row.copy()
            # Fill in defaults for missing columns
            for col in table.columns:
                if col.name not in new_row:
                    if col.defaultValue is not None:
                        new_row[col.name] = col.defaultValue
                    elif col.nullable:
                        new_row[col.name] = None
            result_data.append(new_row)
        columns = [c.name for c in table.columns]

        # Create execution plan
        plan = ExecutionPlanNode(
            type='SCAN',
            tableName=table_name,
            cost=len(table.rows) * 0.1,
            details=f"Full Table Scan on {table_name}",
            children=[]
        )

        # Handle JOIN
        join_match = re.search(
            r'(LEFT\s+)?JOIN\s+(\w+)\s+ON\s+([\w.]+)\s*=\s*([\w.]+)',
            query,
            re.IGNORECASE
        )
        if join_match:
            is_left_join = join_match.group(1) is not None
            join_table_name = join_match.group(2)
            left_col = join_match.group(3).split('.')[-1]
            right_col = join_match.group(4).split('.')[-1]

            join_table = next((t for t in db.tables if t.name == join_table_name), None)
            if not join_table:
                raise ValueError(f"Joined table '{join_table_name}' not found")

            joined_data = []
            if is_left_join:
                # LEFT JOIN: include all rows from left table
                for row1 in result_data:
                    found_match = False
                    for row2 in join_table.rows:
                        if str(row1[left_col]) == str(row2[right_col]):
                            joined_row = {**row1, **row2}
                            joined_data.append(joined_row)
                            found_match = True
                    if not found_match:
                        # Add row with NULL values for right table columns
                        joined_row = {**row1}
                        for col in join_table.columns:
                            joined_row[col.name] = None
                        joined_data.append(joined_row)
                join_type = "Left Join"
            else:
                # INNER JOIN
                for row1 in result_data:
                    for row2 in join_table.rows:
                        if str(row1[left_col]) == str(row2[right_col]):
                            joined_row = {**row1, **row2}
                            joined_data.append(joined_row)
                join_type = "Inner Join"

            result_data = joined_data
            columns.extend([c.name for c in join_table.columns])

            plan = ExecutionPlanNode(
                type='JOIN',
                details=f"{join_type} ({table_name}, {join_table_name})",
                cost=(len(table.rows) * len(join_table.rows)) * 0.05,
                children=[
                    plan,
                    ExecutionPlanNode(
                        type='SCAN',
                        tableName=join_table_name,
                        cost=len(join_table.rows) * 0.1,
                        details=f"Scan {join_table_name}",
                        children=[]
                    )
                ]
            )

        # Handle WHERE clause - enhanced to support AND/OR
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+(ORDER|GROUP|LIMIT|$))', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1).strip()
            result_data = self._apply_where_clause(result_data, where_clause)

            plan = ExecutionPlanNode(
                type='FILTER',
                details=f"Filter by {where_clause[:50]}...",
                cost=len(result_data) * 0.01,
                children=[plan]
            )

        # Handle ORDER BY
        order_match = re.search(r'ORDER\s+BY\s+([\w.]+)\s*(ASC|DESC)?', query, re.IGNORECASE)
        if order_match:
            order_col = order_match.group(1).split('.')[-1]
            order_dir = order_match.group(2).upper() if order_match.group(2) else 'ASC'

            def sort_key(row):
                val = row.get(order_col)
                if val is None:
                    return '' if order_dir == 'ASC' else 'z' * 100
                return val

            reverse = order_dir == 'DESC'
            result_data.sort(key=sort_key, reverse=reverse)

            plan = ExecutionPlanNode(
                type='SORT',
                details=f"Sort by {order_col} {order_dir}",
                cost=len(result_data) * 0.05,
                children=[plan]
            )

        # Handle aggregation functions (COUNT, SUM, AVG, etc.)
        select_match = re.search(r'SELECT\s+(.+?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if select_match:
            select_clause = select_match.group(1).strip()
            result_data, columns = self._handle_aggregation(result_data, select_clause, columns)

        # Handle GROUP BY
        group_match = re.search(r'GROUP\s+BY\s+([\w.]+)', query, re.IGNORECASE)
        if group_match:
            group_col = group_match.group(1).split('.')[-1]
            result_data = self._handle_group_by(result_data, group_col)

        # Handle HAVING
        having_match = re.search(r'HAVING\s+(.+?)(?:\s+(ORDER|LIMIT|$))', query, re.IGNORECASE | re.DOTALL)
        if having_match:
            having_clause = having_match.group(1).strip()
            result_data = self._apply_having_clause(result_data, having_clause)

        # Handle LIMIT
        limit_match = re.search(r'LIMIT\s+(\d+)', query, re.IGNORECASE)
        if limit_match:
            limit = int(limit_match.group(1))
            result_data = result_data[:limit]

        return QueryResult(
            success=True,
            data=result_data,
            columns=list(set(columns)),
            executionTime=time.time() - start_time,
            plan=plan
        )

    def _handle_aggregation(self, data: List[dict], select_clause: str, columns: List[str]) -> tuple:
        """Handle aggregation functions like COUNT, SUM, AVG"""
        # Check if this is a simple aggregation query (no GROUP BY)
        if '*' in select_clause and 'FROM' in select_clause.upper():
            # This is a SELECT * query, return as is
            return data, columns

        # Check for aggregation functions
        agg_functions = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX']
        has_agg = any(func in select_clause.upper() for func in agg_functions)

        if not has_agg:
            return data, columns

        # Parse aggregation functions
        result_row = {}
        new_columns = []

        # Handle COUNT(*)
        count_match = re.search(r'COUNT\s*\(\s*\*\s*\)', select_clause, re.IGNORECASE)
        if count_match:
            result_row['COUNT(*)'] = len(data)
            new_columns.append('COUNT(*)')

        # Handle SUM(column)
        sum_matches = re.findall(r'SUM\s*\(\s*(\w+)\s*\)', select_clause, re.IGNORECASE)
        for col in sum_matches:
            values = [row.get(col, 0) for row in data if row.get(col) is not None]
            try:
                numeric_values = [float(v) for v in values if str(v).replace('.', '').isdigit()]
                result_row[f'SUM({col})'] = sum(numeric_values) if numeric_values else 0
                new_columns.append(f'SUM({col})')
            except:
                result_row[f'SUM({col})'] = 0
                new_columns.append(f'SUM({col})')

        # Handle AVG(column)
        avg_matches = re.findall(r'AVG\s*\(\s*(\w+)\s*\)', select_clause, re.IGNORECASE)
        for col in avg_matches:
            values = [row.get(col, 0) for row in data if row.get(col) is not None]
            try:
                numeric_values = [float(v) for v in values if str(v).replace('.', '').isdigit()]
                result_row[f'AVG({col})'] = sum(numeric_values) / len(numeric_values) if numeric_values else 0
                new_columns.append(f'AVG({col})')
            except:
                result_row[f'AVG({col})'] = 0
                new_columns.append(f'AVG({col})')

        # Handle MIN/MAX if needed
        # For now, return the aggregated result
        return [result_row], new_columns if new_columns else columns

    def _handle_group_by(self, data: List[dict], group_col: str) -> List[dict]:
        """Handle GROUP BY clause"""
        if not data:
            return data

        # Group data by the specified column
        groups = {}
        for row in data:
            key = row.get(group_col)
            if key not in groups:
                groups[key] = []
            groups[key].append(row)

        # For now, return one row per group (simplified)
        # In a full implementation, this would work with aggregation functions
        result = []
        for key, group_rows in groups.items():
            if group_rows:
                result.append(group_rows[0])  # Take first row of each group

        return result

    def _apply_having_clause(self, data: List[dict], having_clause: str) -> List[dict]:
        """Apply HAVING clause filtering after GROUP BY"""
        # Simplified implementation - just filter based on the condition
        filtered_data = []
        for row in data:
            try:
                # Simple evaluation for conditions like "total_spent > 30.00"
                if '>' in having_clause:
                    parts = having_clause.split('>')
                    col = parts[0].strip()
                    val = float(parts[1].strip())
                    if row.get(col, 0) > val:
                        filtered_data.append(row)
                elif '<' in having_clause:
                    parts = having_clause.split('<')
                    col = parts[0].strip()
                    val = float(parts[1].strip())
                    if row.get(col, 0) < val:
                        filtered_data.append(row)
                elif '=' in having_clause:
                    parts = having_clause.split('=')
                    col = parts[0].strip()
                    val = parts[1].strip().strip("'\"")
                    if str(row.get(col, '')) == val:
                        filtered_data.append(row)
            except:
                continue

        return filtered_data

    def _apply_where_clause(self, data: List[dict], where_clause: str) -> List[dict]:
        """Apply WHERE clause filtering with support for AND/OR conditions."""
        # Simple implementation - split by AND/OR and evaluate each condition
        conditions = []
        current_condition = ""

        # Basic parsing of AND/OR conditions
        tokens = re.split(r'\s+(AND|OR)\s+', where_clause, flags=re.IGNORECASE)
        i = 0
        while i < len(tokens):
            if tokens[i].upper() in ['AND', 'OR']:
                if current_condition:
                    conditions.append(current_condition.strip())
                    conditions.append(tokens[i].upper())
                i += 1
            else:
                current_condition = tokens[i]
                i += 1

        if current_condition:
            conditions.append(current_condition.strip())

        # If no AND/OR found, treat as single condition
        if len(conditions) == 1:
            return self._filter_by_condition(data, conditions[0])

        # For simplicity, we'll handle basic AND/OR logic
        # This is a simplified implementation
        result = data
        i = 0
        while i < len(conditions):
            if i + 2 < len(conditions) and conditions[i+1] in ['AND', 'OR']:
                left_result = self._filter_by_condition(result, conditions[i])
                right_result = self._filter_by_condition(data, conditions[i+2])

                if conditions[i+1] == 'AND':
                    # Intersection of both results
                    left_ids = {id(row) for row in left_result}
                    result = [row for row in right_result if id(row) in left_ids]
                else:  # OR
                    # Union of both results
                    result = left_result + [row for row in right_result if row not in left_result]
                i += 3
            else:
                result = self._filter_by_condition(result, conditions[i])
                i += 1

        return result

    def _filter_by_condition(self, data: List[dict], condition: str) -> List[dict]:
        """Filter data by a single WHERE condition."""
        # Parse condition: col op value
        match = re.search(r'([\w.]+)\s*([=<>]+|LIKE)\s*([^;\s]+)', condition, re.IGNORECASE)
        if not match:
            return data

        col_name = match.group(1)
        op = match.group(2).upper()
        val = match.group(3).strip("'`\"")

        filtered_data = []
        for row in data:
            row_val = row.get(col_name.split('.')[-1])
            if row_val is None:
                continue

            try:
                if op == '=':
                    if str(row_val) == val:
                        filtered_data.append(row)
                elif op == '>':
                    if isinstance(row_val, (int, float)) and isinstance(float(val), (int, float)):
                        if float(row_val) > float(val):
                            filtered_data.append(row)
                elif op == '<':
                    if isinstance(row_val, (int, float)) and isinstance(float(val), (int, float)):
                        if float(row_val) < float(val):
                            filtered_data.append(row)
                elif op == 'LIKE':
                    if val in str(row_val):
                        filtered_data.append(row)
            except (ValueError, TypeError):
                continue

        return filtered_data

    def _handle_insert(self, query: str, start_time: float) -> QueryResult:
        """Processes INSERT queries to add new rows to tables."""
        db = self.databases[self.current_db_name]

        # Parse INSERT statement - handle multiple rows
        match = re.search(
            r'INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*(.+)$',
            query,
            re.IGNORECASE | re.DOTALL
        )
        if not match:
            raise ValueError("Invalid INSERT syntax")

        table_name = match.group(1)
        cols_str = match.group(2)
        values_part = match.group(3).strip()

        table = next((t for t in db.tables if t.name == table_name), None)
        if not table:
            raise ValueError(f"Table '{table_name}' not found")

        cols = [c.strip() for c in cols_str.split(',')]

        # Parse multiple value rows
        # Find all value tuples: (val1, val2, ...), (val3, val4, ...)
        value_tuples = re.findall(r'\(([^)]+)\)', values_part)

        rows_inserted = 0
        for tuple_str in value_tuples:
            vals = [v.strip().strip("'\"") for v in tuple_str.split(',')]

            new_row = {}
            for col_name, val in zip(cols, vals):
                # Handle NULL values
                if val.upper() == 'NULL':
                    new_row[col_name] = None
                else:
                    # Convert types
                    col_def = next((c for c in table.columns if c.name == col_name), None)
                    if col_def:
                        if col_def.type in ['INT', 'DECIMAL']:
                            try:
                                new_row[col_name] = int(float(val))
                            except:
                                new_row[col_name] = val
                        elif col_def.type == 'BOOLEAN':
                            new_row[col_name] = val.upper() in ['TRUE', '1', 'YES']
                        elif col_def.type == 'TIMESTAMP':
                            new_row[col_name] = val
                        else:
                            new_row[col_name] = val
                    else:
                        new_row[col_name] = val

            # Auto-generate ID if not provided and column has autoIncrement
            auto_inc_col = next((c for c in table.columns if getattr(c, 'autoIncrement', False)), None)
            if auto_inc_col and auto_inc_col.name not in new_row:
                existing_ids = [r.get(auto_inc_col.name, 0) for r in table.rows if r.get(auto_inc_col.name) is not None]
                new_row[auto_inc_col.name] = max(existing_ids, default=0) + 1

            # Apply defaults for columns not specified in INSERT
            for col in table.columns:
                if col.name not in new_row:
                    if col.defaultValue is not None:
                        new_row[col.name] = col.defaultValue
                    elif col.nullable:
                        new_row[col.name] = None
                    else:
                        raise ValueError(f"Column '{col.name}' cannot be NULL")

            # Check integrity constraints
            self._check_integrity_constraints(table, new_row, is_insert=True)

            table.rows.append(new_row)
            rows_inserted += 1

        self._save_state_to_disk()
        return QueryResult(
            success=True,
            message=f"{rows_inserted} row(s) inserted",
            affectedRows=rows_inserted,
            executionTime=time.time() - start_time
        )

    def _handle_update(self, query: str, start_time: float) -> QueryResult:
        """Processes UPDATE queries to modify existing rows in tables."""
        db = self.databases[self.current_db_name]

        # Parse UPDATE statement: UPDATE table SET col1=val1, col2=val2 WHERE condition
        match = re.search(
            r'UPDATE\s+(\w+)\s+SET\s+(.+?)(?:\s+WHERE\s+(.+))?$',
            query,
            re.IGNORECASE | re.DOTALL
        )
        if not match:
            raise ValueError("Invalid UPDATE syntax")

        table_name = match.group(1)
        set_clause = match.group(2).strip()
        where_clause = match.group(3).strip() if match.group(3) else None

        table = next((t for t in db.tables if t.name == table_name), None)
        if not table:
            raise ValueError(f"Table '{table_name}' not found")

        # Parse SET clause: col1=val1, col2=val2
        set_parts = [part.strip() for part in set_clause.split(',')]
        updates = {}
        for part in set_parts:
            if '=' not in part:
                raise ValueError(f"Invalid SET clause: {part}")
            col, val = part.split('=', 1)
            col = col.strip()
            val = val.strip().strip("'\"")

            # Verify column exists
            if not any(c.name == col for c in table.columns):
                raise ValueError(f"Column '{col}' not found in table '{table_name}'")

            # Handle NULL values
            if val.upper() == 'NULL':
                updates[col] = None
            else:
                # Convert types
                col_def = next((c for c in table.columns if c.name == col), None)
                if col_def and col_def.type in ['INT', 'DECIMAL']:
                    try:
                        updates[col] = int(float(val))
                    except:
                        updates[col] = val
                else:
                    updates[col] = val

        # Find rows to update
        rows_to_update = []
        if where_clause:
            # Parse WHERE clause (simplified: only supports col = value)
            where_match = re.search(r'(\w+)\s*=\s*([^;\s]+)', where_clause, re.IGNORECASE)
            if not where_match:
                raise ValueError("Unsupported WHERE clause in UPDATE")

            where_col = where_match.group(1)
            where_val = where_match.group(2).strip("'\"")

            # Convert where value type
            where_col_def = next((c for c in table.columns if c.name == where_col), None)
            if where_col_def and where_col_def.type in ['INT', 'DECIMAL']:
                try:
                    where_val = int(float(where_val))
                except:
                    pass

            # Find matching rows
            for i, row in enumerate(table.rows):
                if str(row.get(where_col, '')) == str(where_val):
                    rows_to_update.append(i)
        else:
            # Update all rows if no WHERE clause
            rows_to_update = list(range(len(table.rows)))

        # Apply updates
        updated_count = 0
        for row_index in rows_to_update:
            for col, val in updates.items():
                table.rows[row_index][col] = val
            updated_count += 1

        self._save_state_to_disk()
        return QueryResult(
            success=True,
            message=f"{updated_count} row(s) updated",
            affectedRows=updated_count,
            executionTime=time.time() - start_time
        )

    def _handle_delete(self, query: str, start_time: float) -> QueryResult:
        """Processes DELETE queries to remove rows from tables."""
        db = self.databases[self.current_db_name]

        match = re.search(r'DELETE\s+FROM\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DELETE syntax")

        table_name = match.group(1)
        table = next((t for t in db.tables if t.name == table_name), None)
        if not table:
            raise ValueError(f"Table '{table_name}' not found")

        original_count = len(table.rows)

        # Handle WHERE clause
        where_match = re.search(r'WHERE\s+([\w.]+)\s*=\s*([^;\s]+)', query, re.IGNORECASE)
        if where_match:
            col_name = where_match.group(1)
            val = where_match.group(2).strip("'\"")
            table.rows = [r for r in table.rows if str(r.get(col_name, '')) != val]
        else:
            table.rows = []

        self._save_state_to_disk()
        return QueryResult(
            success=True,
            message=f"{original_count - len(table.rows)} rows deleted",
            affectedRows=original_count - len(table.rows),
            executionTime=time.time() - start_time
        )

    def _handle_create_database(self, query: str, start_time: float) -> QueryResult:
        """Processes CREATE DATABASE queries."""
        # Check if IF NOT EXISTS is present
        has_if_not_exists = 'IF NOT EXISTS' in query.upper()

        match = re.search(r'CREATE\s+DATABASE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid CREATE DATABASE syntax")

        db_name = match.group(1)

        # If database already exists and IF NOT EXISTS is specified, succeed silently and switch to it
        if db_name in self.databases:
            if has_if_not_exists:
                self.current_db_name = db_name  # Switch to the existing database
                return QueryResult(
                    success=True,
                    message=f"Database '{db_name}' already exists",
                    executionTime=time.time() - start_time
                )
            else:
                raise ValueError(f"Database '{db_name}' already exists")

        self.create_database(db_name)

        return QueryResult(
            success=True,
            message=f"Database '{db_name}' created successfully",
            executionTime=time.time() - start_time
        )

    def _handle_drop_database(self, query: str, start_time: float) -> QueryResult:
        """Processes DROP DATABASE queries."""
        match = re.search(r'DROP\s+DATABASE\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid DROP DATABASE syntax")

        db_name = match.group(1)
        self.drop_database(db_name)

        return QueryResult(
            success=True,
            message=f"Database '{db_name}' dropped successfully",
            executionTime=time.time() - start_time
        )

    def _handle_create_table(self, query: str, start_time: float) -> QueryResult:
        """Processes CREATE TABLE queries."""
        # Parse table name
        table_match = re.search(r'CREATE\s+TABLE\s+(\w+)\s*\(', query, re.IGNORECASE)
        if not table_match:
            raise ValueError("Invalid CREATE TABLE syntax")

        table_name = table_match.group(1)

        # Extract column definitions between parentheses
        columns_part = re.search(r'CREATE\s+TABLE\s+\w+\s*\((.*)\)', query, re.IGNORECASE | re.DOTALL)
        if not columns_part:
            raise ValueError("Invalid CREATE TABLE syntax")

        columns_str = columns_part.group(1).strip()
        # Remove trailing semicolon if present
        columns_str = columns_str.rstrip(';').strip()

        # Parse column definitions - handle commas inside parentheses
        columns = []
        column_defs = []
        current_def = ""
        paren_depth = 0

        print(f"DEBUG: About to parse columns_str: '{columns_str}'")
        for i, char in enumerate(columns_str):
            print(f"DEBUG: Processing char '{char}' at position {i}, current paren_depth = {paren_depth}")
            if char == '(':
                paren_depth += 1
                print(f"DEBUG: Incremented paren_depth to {paren_depth}")
                current_def += char
            elif char == ')':
                paren_depth -= 1
                print(f"DEBUG: Decremented paren_depth to {paren_depth}")
                current_def += char
            elif char == ',' and paren_depth == 0:
                # Only split on comma if we're not inside parentheses
                print(f"DEBUG: Splitting at comma, current_def so far: '{current_def}'")
                if current_def.strip():
                    column_defs.append(current_def.strip())
                current_def = ""
            elif char == ',':
                print(f"DEBUG: NOT splitting at comma (inside parentheses), paren_depth = {paren_depth}")
                current_def += char
            else:
                current_def += char

        print(f"DEBUG: Final current_def: '{current_def}'")

        # Add the last definition
        if current_def.strip():
            column_defs.append(current_def.strip())

        print(f"DEBUG: Before filtering, column_defs = {column_defs}")

        # Process table-level constraints and filter out non-column definitions
        table_constraints = []
        filtered_column_defs = []
        for col_def in column_defs:
            col_def_stripped = col_def.strip()
            first_word = col_def_stripped.upper().split()[0] if col_def_stripped.split() else ""
            # Handle table-level constraints
            if first_word == 'FOREIGN':
                table_constraints.append(col_def_stripped)
                continue
            # Skip other table-level constraints for now
            elif first_word in ['PRIMARY', 'UNIQUE', 'CHECK', 'CONSTRAINT']:
                continue
            filtered_column_defs.append(col_def_stripped)

        column_defs = filtered_column_defs

        for i, col_def in enumerate(column_defs):
            # Parse column definition more carefully
            col_def_upper = col_def.upper()

            # Extract column name and type using regex
            name_match = re.match(r'(\w+)', col_def.strip())
            if not name_match:
                raise ValueError(f"Invalid column definition: {col_def}")

            col_name = name_match.group(1)

            # Find the data type - look for known data type keywords
            col_type_str = None
            data_types = ['VARCHAR', 'INT', 'DECIMAL', 'BOOLEAN', 'TIMESTAMP', 'DATE', 'DATETIME']
            for dtype in data_types:
                # More specific pattern for DECIMAL with parameters
                if dtype == 'DECIMAL':
                    pattern = r'\bDECIMAL(?:\(\d+(?:,\s*\d+)?\))?(\(\d+(?:,\s*\d+)?\))?'
                else:
                    pattern = rf'\b{dtype}(?:\((?:\d+(?:,\s*\d+)?)?\))?'
                match = re.search(pattern, col_def_upper)
                if match:
                    col_type_str = match.group(0)
                    break

            if not col_type_str:
                # Fallback: simple split and check
                parts = col_def.strip().split()
                if len(parts) >= 2:
                    for i, part in enumerate(parts):
                        if 'DECIMAL' in part.upper():
                            # Find the complete DECIMAL type
                            decimal_part = part
                            j = i + 1
                            while j < len(parts):
                                if parts[j].strip().endswith(')'):
                                    decimal_part += ' ' + parts[j]
                                    break
                                decimal_part += ' ' + parts[j]
                                j += 1
                            col_type_str = decimal_part.strip()
                            break

            if not col_type_str:
                raise ValueError(f"Unsupported data type in column definition: {col_def}")

            # Parse data type
            if col_type_str.upper().startswith('VARCHAR'):
                # Extract length from VARCHAR(50)
                length_match = re.search(r'VARCHAR\((\d+)\)', col_type_str)
                col_type = 'VARCHAR'
                length = int(length_match.group(1)) if length_match else None
            elif col_type_str.upper().startswith('DECIMAL'):
                # DECIMAL can be DECIMAL or DECIMAL(10,2)
                col_type = 'DECIMAL'
                length = None
            elif col_type_str.upper() in ['INT', 'BOOLEAN', 'TIMESTAMP', 'DATE', 'DATETIME']:
                col_type = col_type_str.upper()
                length = None
            else:
                raise ValueError(f"Unsupported data type: {col_type_str}")

            # Check for constraints
            is_primary_key = 'PRIMARY KEY' in col_def_upper
            is_auto_increment = 'AUTO_INCREMENT' in col_def_upper
            is_not_null = 'NOT NULL' in col_def_upper
            is_unique = 'UNIQUE' in col_def_upper

            # Nullable logic: primary keys and NOT NULL columns are not nullable
            nullable = not (is_primary_key or is_not_null)

            # Auto-increment only for INT primary keys
            auto_increment = is_auto_increment and col_type == 'INT'

            # Check for DEFAULT value
            default_value = None
            default_match = re.search(r'DEFAULT\s+([^,\s]+)', col_def, re.IGNORECASE)
            if default_match:
                default_val = default_match.group(1).strip()
                if default_val.upper() == 'CURRENT_TIMESTAMP':
                    from datetime import datetime
                    default_value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                elif default_val.upper() in ['TRUE', 'FALSE']:
                    default_value = default_val.upper() == 'TRUE'
                else:
                    try:
                        default_value = int(float(default_val))
                    except:
                        default_value = default_val.strip("'\"")

            # Check for REFERENCES (foreign key)
            references = None
            ref_match = re.search(r'REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)', col_def, re.IGNORECASE)
            if ref_match:
                ref_table = ref_match.group(1)
                ref_column = ref_match.group(2)
                references = {'tableId': ref_table, 'columnId': ref_column}

            # Create column schema
            column = ColumnSchema(
                id=f"{table_name}_col_{i}",
                name=col_name,
                type=col_type,
                length=length,
                nullable=nullable,
                isPrimaryKey=is_primary_key,
                isUnique=is_unique,
                autoIncrement=auto_increment,
                defaultValue=default_value,
                isForeignKey=references is not None,
                references=references
            )
            columns.append(column)

        # Process table-level foreign key constraints
        for constraint in table_constraints:
            # Parse FOREIGN KEY (column_name) REFERENCES table_name(column_name)
            fk_match = re.search(r'FOREIGN\s+KEY\s*\(\s*(\w+)\s*\)\s*REFERENCES\s+(\w+)\s*\(\s*(\w+)\s*\)', constraint, re.IGNORECASE)
            if fk_match:
                fk_col_name = fk_match.group(1)
                ref_table_name = fk_match.group(2)
                ref_col_name = fk_match.group(3)

                # Find the column in our columns list and update its foreign key properties
                for col in columns:
                    if col.name == fk_col_name:
                        col.isForeignKey = True
                        col.references = {'tableId': ref_table_name, 'columnId': ref_col_name}
                        break

        # Create table schema
        table_schema = TableSchema(
            id=table_name,
            name=table_name,
            columns=columns,
            indexes=[],
            rows=[]
        )

        # Create the table
        self.create_table(table_schema)

        return QueryResult(
            success=True,
            message=f"Table '{table_name}' created successfully",
            executionTime=time.time() - start_time
        )

    def _handle_select_functions(self, query: str, start_time: float) -> QueryResult:
        """Handles system functions like VERSION(), USER(), DATABASE(), NOW()"""
        query_upper = query.upper()

        # Check if this is a simple SELECT with just a function (no FROM clause)
        if 'FROM' not in query_upper:
            if 'VERSION()' in query_upper:
                return QueryResult(
                    success=True,
                    data=[{'VERSION()': 'RDBMS Challenge v1.0.0'}],
                    columns=['VERSION()'],
                    executionTime=time.time() - start_time
                )
            elif 'USER()' in query_upper:
                return QueryResult(
                    success=True,
                    data=[{'USER()': 'admin@localhost'}],
                    columns=['USER()'],
                    executionTime=time.time() - start_time
                )
            elif 'DATABASE()' in query_upper:
                return QueryResult(
                    success=True,
                    data=[{'DATABASE()': self.current_db_name or 'NULL'}],
                    columns=['DATABASE()'],
                    executionTime=time.time() - start_time
                )
            elif 'NOW()' in query_upper:
                from datetime import datetime
                now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return QueryResult(
                    success=True,
                    data=[{'NOW()': now_str}],
                    columns=['NOW()'],
                    executionTime=time.time() - start_time
                )

        return None

    def _handle_alter_table(self, query: str, start_time: float) -> QueryResult:
        """Processes ALTER TABLE queries."""
        match = re.search(r'ALTER\s+TABLE\s+(\w+)\s+ADD\s+COLUMN\s+(\w+)\s+(.+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Unsupported ALTER TABLE syntax. Only ADD COLUMN is supported.")

        table_name = match.group(1)
        col_name = match.group(2)
        col_def = match.group(3).strip()

        db = self.databases[self.current_db_name]
        table = next((t for t in db.tables if t.name == table_name), None)
        if not table:
            raise ValueError(f"Table '{table_name}' not found")

        # Check if column already exists
        if any(c.name == col_name for c in table.columns):
            raise ValueError(f"Column '{col_name}' already exists in table '{table_name}'")

        # Parse column type and constraints
        col_parts = col_def.split()
        col_type_str = col_parts[0].upper()

        # Parse data type
        if col_type_str.startswith('VARCHAR'):
            length_match = re.search(r'VARCHAR\((\d+)\)', col_type_str)
            col_type = 'VARCHAR'
            length = int(length_match.group(1)) if length_match else None
        elif col_type_str in ['INT', 'DECIMAL', 'BOOLEAN', 'TIMESTAMP']:
            col_type = col_type_str
            length = None
        else:
            raise ValueError(f"Unsupported data type: {col_type_str}")

        nullable = 'NOT NULL' not in col_def.upper()
        is_primary_key = 'PRIMARY KEY' in col_def.upper()
        default_value = None

        # Check for DEFAULT value
        default_match = re.search(r'DEFAULT\s+([^,\s]+)', col_def, re.IGNORECASE)
        if default_match:
            default_val = default_match.group(1).strip()
            if default_val.upper() == 'TRUE':
                default_value = True
            elif default_val.upper() == 'FALSE':
                default_value = False
            elif default_val.upper() == 'CURRENT_TIMESTAMP':
                from datetime import datetime
                default_value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                try:
                    default_value = int(float(default_val))
                except:
                    default_value = default_val.strip("'\"")

        # Create new column
        new_column = ColumnSchema(
            id=f"{table_name}_{col_name}",
            name=col_name,
            type=col_type,
            length=length,
            nullable=nullable,
            isPrimaryKey=is_primary_key,
            defaultValue=default_value
        )

        table.columns.append(new_column)

        # Add default values to existing rows
        for row in table.rows:
            row[col_name] = default_value

        self._save_state_to_disk()
        return QueryResult(
            success=True,
            message=f"Column '{col_name}' added to table '{table_name}'",
            executionTime=time.time() - start_time
        )

    def _handle_use_database(self, query: str, start_time: float) -> QueryResult:
        """Processes USE database queries."""
        match = re.search(r'USE\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid USE syntax")

        db_name = match.group(1)
        if db_name not in self.databases:
            raise ValueError(f"Database '{db_name}' does not exist")

        self.current_db_name = db_name
        return QueryResult(
            success=True,
            message=f"Database changed to '{db_name}'",
            executionTime=time.time() - start_time
        )

    def _handle_start_transaction(self, query: str, start_time: float) -> QueryResult:
        """Processes START TRANSACTION queries."""
        # For this simple implementation, we'll just acknowledge the transaction start
        # In a real RDBMS, this would begin a transaction context
        return QueryResult(
            success=True,
            message="Transaction started",
            executionTime=time.time() - start_time
        )

    def _handle_commit(self, query: str, start_time: float) -> QueryResult:
        """Processes COMMIT queries."""
        # For this simple implementation, all operations are auto-committed
        return QueryResult(
            success=True,
            message="Transaction committed",
            executionTime=time.time() - start_time
        )

    def _handle_rollback(self, query: str, start_time: float) -> QueryResult:
        """Processes ROLLBACK queries."""
        # For this simple implementation, we don't support rollbacks
        # In a real implementation, this would undo changes since START TRANSACTION
        return QueryResult(
            success=True,
            message="Transaction rolled back",
            executionTime=time.time() - start_time
        )

    def _check_integrity_constraints(self, table: TableSchema, new_row: dict, is_insert: bool = True) -> None:
        """Check integrity constraints for INSERT operations."""
        db = self.databases[self.current_db_name]

        # Check NOT NULL constraints
        for col in table.columns:
            # Skip NOT NULL check for auto-increment columns during INSERT if they don't have a value
            if is_insert and getattr(col, 'autoIncrement', False) and new_row.get(col.name) is None:
                continue
            if not col.nullable and new_row.get(col.name) is None:
                raise ValueError(f"Column '{col.name}' cannot be NULL")

        # Check UNIQUE constraints (primary keys are unique)
        for col in table.columns:
            if col.isPrimaryKey or getattr(col, 'isUnique', False):
                col_value = new_row.get(col.name)
                if col_value is not None:
                    # Check if value already exists in table
                    for existing_row in table.rows:
                        if existing_row.get(col.name) == col_value:
                            if col.isPrimaryKey:
                                raise ValueError(f"Duplicate entry '{col_value}' for key '{col.name}'")
                            else:
                                raise ValueError(f"Duplicate entry '{col_value}' for unique key '{col.name}'")

        # Check FOREIGN KEY constraints
        for col in table.columns:
            if getattr(col, 'isForeignKey', False) and col.references:
                fk_value = new_row.get(col.name)
                if fk_value is not None:
                    # Find referenced table
                    ref_table_name = col.references.get('tableId')
                    ref_col_name = col.references.get('columnId')

                    ref_table = next((t for t in db.tables if t.name == ref_table_name), None)
                    if ref_table:
                        # Check if referenced value exists
                        ref_exists = any(
                            row.get(ref_col_name) == fk_value
                            for row in ref_table.rows
                        )
                        if not ref_exists:
                            raise ValueError(f"Foreign key constraint fails: cannot add or update child row with value '{fk_value}'")
