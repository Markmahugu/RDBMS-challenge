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

    def _load_state_from_disk(self) -> None:
        """Loads the entire database state from the JSON storage file."""
        if not os.path.exists(self.storage_path):
            self.current_db_name = 'DemoDB'
            self.reset_database()
            return

        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            self.databases = {name: DatabaseState(**db_data) for name, db_data in data.items()}
            if self.databases:
                self.current_db_name = list(self.databases.keys())[0]
            else:
                self.current_db_name = 'DemoDB'
                self.reset_database()
        except (json.JSONDecodeError, TypeError):
            self.current_db_name = 'DemoDB'
            self.reset_database()

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
        """Processes SELECT queries, including joins, filters, and limits."""
        db = self.databases[self.current_db_name]

        # Parse FROM clause
        from_match = re.search(r'FROM\s+(\w+)', query, re.IGNORECASE)
        if not from_match:
            raise ValueError("Missing FROM clause")

        table_name = from_match.group(1)
        table = next((t for t in db.tables if t.name == table_name), None)
        if not table:
            raise ValueError(f"Table '{table_name}' not found")

        result_data = table.rows.copy()
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
            r'JOIN\s+(\w+)\s+ON\s+([\w.]+)\s*=\s*([\w.]+)',
            query,
            re.IGNORECASE
        )
        if join_match:
            join_table_name = join_match.group(1)
            left_col = join_match.group(2).split('.')[-1]
            right_col = join_match.group(3).split('.')[-1]

            join_table = next((t for t in db.tables if t.name == join_table_name), None)
            if not join_table:
                raise ValueError(f"Joined table '{join_table_name}' not found")

            joined_data = []
            for row1 in result_data:
                for row2 in join_table.rows:
                    if str(row1[left_col]) == str(row2[right_col]):
                        joined_row = {**row1, **row2}
                        joined_data.append(joined_row)

            result_data = joined_data
            columns.extend([c.name for c in join_table.columns])

            plan = ExecutionPlanNode(
                type='JOIN',
                details=f"Inner Join ({table_name}, {join_table_name})",
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

        # Handle WHERE clause
        where_match = re.search(
            r'WHERE\s+([\w.]+)\s*([=<>]+)\s*([^;\s]+)',
            query,
            re.IGNORECASE
        )
        if where_match:
            col_name = where_match.group(1)
            op = where_match.group(2)
            val = where_match.group(3).strip("'\"")

            filtered_data = []
            for row in result_data:
                row_val = row.get(col_name.split('.')[-1])
                if row_val is not None:
                    if op == '=' and str(row_val) == val:
                        filtered_data.append(row)
                    elif op == '>' and float(row_val) > float(val):
                        filtered_data.append(row)
                    elif op == '<' and float(row_val) < float(val):
                        filtered_data.append(row)
                    elif op.upper() == 'LIKE' and val in str(row_val):
                        filtered_data.append(row)

            result_data = filtered_data

            plan = ExecutionPlanNode(
                type='FILTER',
                details=f"Filter by {col_name} {op} {val}",
                cost=len(result_data) * 0.01,
                children=[plan]
            )

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
                        else:
                            new_row[col_name] = val
                    else:
                        new_row[col_name] = val

            # Auto-generate ID if not provided and column has autoIncrement
            auto_inc_col = next((c for c in table.columns if getattr(c, 'autoIncrement', False)), None)
            if auto_inc_col and auto_inc_col.name not in new_row:
                existing_ids = [r.get(auto_inc_col.name, 0) for r in table.rows if r.get(auto_inc_col.name) is not None]
                new_row[auto_inc_col.name] = max(existing_ids, default=0) + 1

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
        match = re.search(r'CREATE\s+DATABASE\s+(\w+)', query, re.IGNORECASE)
        if not match:
            raise ValueError("Invalid CREATE DATABASE syntax")

        db_name = match.group(1)
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

        # Parse column definitions
        columns = []
        column_defs = [col.strip() for col in columns_str.split(',') if col.strip()]

        for i, col_def in enumerate(column_defs):
            col_parts = col_def.split()
            if len(col_parts) < 2:
                raise ValueError(f"Invalid column definition: {col_def}")

            col_name = col_parts[0]
            col_type_str = col_parts[1].upper()

            # Parse data type
            if col_type_str.startswith('VARCHAR'):
                # Extract length from VARCHAR(50)
                length_match = re.search(r'VARCHAR\((\d+)\)', col_type_str)
                col_type = 'VARCHAR'
                length = int(length_match.group(1)) if length_match else None
            elif col_type_str == 'INT':
                col_type = 'INT'
                length = None
            else:
                raise ValueError(f"Unsupported data type: {col_type_str}")

            # Check for PRIMARY KEY
            is_primary_key = 'PRIMARY KEY' in col_def.upper()
            nullable = not is_primary_key  # Primary keys are typically not nullable

            # Auto-increment for INT primary keys only
            auto_increment = is_primary_key and col_type == 'INT'

            # Create column schema
            column = ColumnSchema(
                id=f"{table_name}_col_{i}",
                name=col_name,
                type=col_type,
                length=length,
                nullable=nullable,
                isPrimaryKey=is_primary_key,
                autoIncrement=auto_increment
            )
            columns.append(column)

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
