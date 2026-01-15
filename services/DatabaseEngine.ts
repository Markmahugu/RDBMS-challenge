import { DatabaseState, TableSchema, ColumnSchema, QueryResult, ExecutionPlanNode } from '../types';

export class MockDatabase {
  private databases: Record<string, DatabaseState>;
  private currentDbName: string;

  constructor() {
    this.currentDbName = 'DemoDB';
    this.databases = {};
    this.resetDatabase();
  }

  public resetDatabase() {
    this.databases = {
      'DemoDB': {
        name: 'DemoDB',
        tables: []
      }
    };
    this.seedData('DemoDB');
  }

  private seedData(dbName: string) {
    // Departments
    const deptTable: TableSchema = {
      id: 'departments',
      name: 'departments',
      columns: [
        { id: 'd1', name: 'id', type: 'INT', nullable: false, isPrimaryKey: true },
        { id: 'd2', name: 'name', type: 'VARCHAR', length: 100, nullable: false, isPrimaryKey: false },
        { id: 'd3', name: 'location', type: 'VARCHAR', length: 100, nullable: true, isPrimaryKey: false }
      ],
      indexes: [],
      rows: [
        { id: 1, name: 'Engineering', location: 'Building A' },
        { id: 2, name: 'HR', location: 'Building B' },
        { id: 3, name: 'Sales', location: 'Building C' },
        { id: 4, name: 'Marketing', location: 'Building A' }
      ]
    };

    // Employees
    const empTable: TableSchema = {
      id: 'employees',
      name: 'employees',
      columns: [
        { id: 'e1', name: 'id', type: 'INT', nullable: false, isPrimaryKey: true },
        { id: 'e2', name: 'name', type: 'VARCHAR', length: 100, nullable: false, isPrimaryKey: false },
        { id: 'e3', name: 'role', type: 'VARCHAR', length: 50, nullable: false, isPrimaryKey: false },
        { id: 'e4', name: 'department_id', type: 'INT', nullable: true, isPrimaryKey: false, isForeignKey: true, references: { tableId: 'departments', columnId: 'd1' } },
        { id: 'e5', name: 'salary', type: 'DECIMAL', nullable: false, isPrimaryKey: false }
      ],
      indexes: [{ id: 'idx_emp_dept', name: 'idx_department_id', columnIds: ['e4'], type: 'BTREE' }],
      rows: [
        { id: 101, name: 'Alice Johnson', role: 'Senior Engineer', department_id: 1, salary: 95000 },
        { id: 102, name: 'Bob Smith', role: 'Product Manager', department_id: 1, salary: 105000 },
        { id: 103, name: 'Charlie Brown', role: 'HR Specialist', department_id: 2, salary: 65000 },
        { id: 104, name: 'Diana Prince', role: 'Sales Lead', department_id: 3, salary: 85000 },
        { id: 105, name: 'Evan Wright', role: 'Engineer', department_id: 1, salary: 75000 }
      ]
    };

    // Projects
    const projTable: TableSchema = {
      id: 'projects',
      name: 'projects',
      columns: [
        { id: 'p1', name: 'id', type: 'INT', nullable: false, isPrimaryKey: true },
        { id: 'p2', name: 'name', type: 'VARCHAR', length: 100, nullable: false, isPrimaryKey: false },
        { id: 'p3', name: 'budget', type: 'DECIMAL', nullable: true, isPrimaryKey: false }
      ],
      indexes: [],
      rows: [
        { id: 1, name: 'Project Alpha', budget: 50000 },
        { id: 2, name: 'Project Beta', budget: 120000 },
        { id: 3, name: 'Website Redesign', budget: 30000 }
      ]
    };

    this.databases[dbName].tables = [deptTable, empTable, projTable];
  }

  public getDatabaseState(): DatabaseState {
    return this.databases[this.currentDbName];
  }

  public createDatabase(name: string) {
    if (this.databases[name]) throw new Error(`Database '${name}' already exists.`);
    this.databases[name] = { name, tables: [] };
    this.currentDbName = name;
  }

  public createTable(table: TableSchema) {
    const db = this.getDatabaseState();
    if (db.tables.find(t => t.name === table.name)) {
      throw new Error(`Table '${table.name}' already exists.`);
    }
    db.tables.push(table);
  }

  public updateTable(oldName: string, newSchema: TableSchema) {
    const db = this.getDatabaseState();
    const tableIndex = db.tables.findIndex(t => t.name === oldName);
    
    if (tableIndex === -1) {
        // Fallback: create if not exists
        this.createTable(newSchema);
        return;
    }

    const oldTable = db.tables[tableIndex];
    
    // Check if renaming to a name that already exists (and isn't self)
    if (oldName !== newSchema.name && db.tables.find(t => t.name === newSchema.name)) {
        throw new Error(`Table '${newSchema.name}' already exists.`);
    }

    // Migrate Data
    // We map old rows to new rows based on Column IDs primarily, or Name if ID not found (new col)
    const newRows = oldTable.rows.map(oldRow => {
        const newRow: any = {};
        newSchema.columns.forEach(newCol => {
            // Find corresponding column in old table by ID
            const oldCol = oldTable.columns.find(c => c.id === newCol.id);
            
            if (oldCol) {
                // Column exists (possibly renamed), copy data using old name
                newRow[newCol.name] = oldRow[oldCol.name];
            } else {
                // New column, try to match by name as fallback for loose migrations
                if (oldRow[newCol.name] !== undefined) {
                    newRow[newCol.name] = oldRow[newCol.name];
                } else {
                    newRow[newCol.name] = newCol.defaultValue !== undefined ? newCol.defaultValue : null;
                }
            }
        });
        return newRow;
    });

    newSchema.rows = newRows;
    db.tables[tableIndex] = newSchema;
  }

  public dropTable(tableName: string) {
    const db = this.getDatabaseState();
    db.tables = db.tables.filter(t => t.name !== tableName);
  }

  public togglePrimaryKey(tableName: string, columnName: string) {
    const db = this.getDatabaseState();
    const table = db.tables.find(t => t.name === tableName);
    if (!table) return;
    const col = table.columns.find(c => c.name === columnName);
    if (!col) return;
    col.isPrimaryKey = !col.isPrimaryKey;
  }

  public updateCell(tableName: string, rowIndex: number, colName: string, value: any): QueryResult {
    const db = this.getDatabaseState();
    const table = db.tables.find(t => t.name === tableName);
    if (!table) throw new Error("Table not found");
    
    if (!table.rows[rowIndex]) throw new Error("Row not found");
    
    const colDef = table.columns.find(c => c.name === colName);
    let finalValue = value;
    if (colDef?.type === 'INT' || colDef?.type === 'DECIMAL') {
        finalValue = Number(value);
        if (isNaN(finalValue)) finalValue = value;
    }
    
    table.rows[rowIndex][colName] = finalValue;

    return {
        success: true,
        message: `Updated ${tableName} row ${rowIndex}`,
        affectedRows: 1,
        executionTime: Math.random() * 10
    };
  }

  public async executeSQL(query: string): Promise<QueryResult> {
    const start = performance.now();
    await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 500)); 

    const q = query.trim();
    const upperQ = q.toUpperCase();
    const db = this.getDatabaseState();

    try {
      if (upperQ.startsWith('SELECT')) {
        return this.handleSelect(q, start, db);
      } else if (upperQ.startsWith('INSERT')) {
        return this.handleInsert(q, start, db);
      } else if (upperQ.startsWith('DELETE')) {
        return this.handleDelete(q, start, db);
      } else if (upperQ.startsWith('UPDATE')) {
        return this.handleUpdate(q, start, db);
      } else if (upperQ.startsWith('CREATE TABLE')) {
        return { success: true, message: 'CREATE TABLE simulated (use Designer for full features)', executionTime: performance.now() - start };
      } else if (upperQ.startsWith('DROP TABLE')) {
        const parts = q.split(' ');
        const tableName = parts[2]?.replace(';', '');
        if (tableName) {
          this.dropTable(tableName);
          return { success: true, message: `Table ${tableName} dropped.`, executionTime: performance.now() - start };
        }
      }
      
      throw new Error("Syntax error: Unsupported command. Try SELECT, INSERT, UPDATE, DELETE.");

    } catch (e: any) {
      return {
        success: false,
        message: e.message,
        executionTime: performance.now() - start
      };
    }
  }

  // --- Handlers ---

  private handleSelect(query: string, start: number, db: DatabaseState): QueryResult {
    const fromMatch = query.match(/FROM\s+([a-zA-Z0-9_]+)/i);
    if (!fromMatch) throw new Error("Syntax Error: Missing FROM clause");
    
    const tableName = fromMatch[1];
    const table = db.tables.find(t => t.name === tableName);
    if (!table) throw new Error(`Table '${tableName}' not found`);

    let resultData = [...table.rows];
    let columns = table.columns.map(c => c.name);

    const joinMatch = query.match(/JOIN\s+([a-zA-Z0-9_]+)\s+ON\s+([a-zA-Z0-9_.]+)\s*=\s*([a-zA-Z0-9_.]+)/i);
    let plan: ExecutionPlanNode = {
      type: 'SCAN',
      tableName: tableName,
      cost: table.rows.length * 0.1,
      details: `Full Table Scan on ${tableName}`,
      children: []
    };

    if (joinMatch) {
      const joinTable = joinMatch[1];
      const leftCol = joinMatch[2].split('.')[1];
      const rightCol = joinMatch[3].split('.')[1];
      
      const table2 = db.tables.find(t => t.name === joinTable);
      if (!table2) throw new Error(`Joined table '${joinTable}' not found`);

      const joinedData: any[] = [];
      resultData.forEach(row1 => {
        table2.rows.forEach(row2 => {
          if (String(row1[leftCol]) === String(row2[rightCol])) {
            joinedData.push({ ...row1, [`${joinTable}.${rightCol}`]: row2[rightCol], ...row2 });
          }
        });
      });
      resultData = joinedData;
      columns = [...columns, ...table2.columns.map(c => c.name)]; 

      plan = {
        type: 'JOIN',
        details: `Inner Join (${tableName}, ${joinTable})`,
        cost: (table.rows.length * table2.rows.length) * 0.05,
        children: [
          plan,
          { type: 'SCAN', tableName: joinTable, cost: table2.rows.length * 0.1, details: `Scan ${joinTable}` }
        ]
      };
    }

    const whereMatch = query.match(/WHERE\s+([a-zA-Z0-9_.]+)\s*(=|>|<|LIKE)\s*(.+)/i);
    if (whereMatch) {
      const col = whereMatch[1];
      const op = whereMatch[2];
      let val = whereMatch[3].replace(/['";]/g, '').trim(); 

      const finalData = resultData.filter(row => {
        const rowVal = row[col] || row[col.split('.')[1]]; 
        if (op === '=') return String(rowVal) == val;
        if (op === '>') return Number(rowVal) > Number(val);
        if (op === '<') return Number(rowVal) < Number(val);
        if (op === 'LIKE') return String(rowVal).includes(val);
        return true;
      });
      resultData = finalData;

      plan = {
        type: 'FILTER',
        details: `Filter by ${col} ${op} ${val}`,
        cost: resultData.length * 0.01,
        children: [plan]
      }
    }

    const limitMatch = query.match(/LIMIT\s+(\d+)/i);
    if (limitMatch) {
      resultData = resultData.slice(0, parseInt(limitMatch[1]));
    }

    return {
      success: true,
      data: resultData,
      columns: Array.from(new Set(columns)), 
      executionTime: performance.now() - start,
      plan: plan
    };
  }

  private handleInsert(query: string, start: number, db: DatabaseState): QueryResult {
    const match = query.match(/INSERT\s+INTO\s+([a-zA-Z0-9_]+)\s*\((.+)\)\s*VALUES\s*\((.+)\)/i);
    if (!match) throw new Error("Syntax error in INSERT statement");

    const tableName = match[1];
    const cols = match[2].split(',').map(c => c.trim());
    const vals = match[3].split(',').map(v => v.trim().replace(/^['"]|['"]$/g, ''));

    const table = db.tables.find(t => t.name === tableName);
    if (!table) throw new Error(`Table '${tableName}' not found`);

    const newRow: any = {};
    cols.forEach((col, idx) => {
      newRow[col] = vals[idx];
    });

    if (!newRow['id']) newRow['id'] = Math.floor(Math.random() * 10000);

    table.rows.push(newRow);

    return {
      success: true,
      message: "1 row inserted",
      affectedRows: 1,
      executionTime: performance.now() - start
    };
  }

  private handleUpdate(query: string, start: number, db: DatabaseState): QueryResult {
    return { success: true, message: "Update simulated (0 rows affected)", executionTime: performance.now() - start };
  }

  private handleDelete(query: string, start: number, db: DatabaseState): QueryResult {
    const match = query.match(/DELETE\s+FROM\s+([a-zA-Z0-9_]+)/i);
     if (!match) throw new Error("Syntax error in DELETE statement");
     
     const tableName = match[1];
     const table = db.tables.find(t => t.name === tableName);
     if (!table) throw new Error(`Table '${tableName}' not found`);

     const originalCount = table.rows.length;
     
     const whereMatch = query.match(/WHERE\s+([a-zA-Z0-9_]+)\s*=\s*(.+)/i);
     if (whereMatch) {
        const col = whereMatch[1];
        const val = whereMatch[2].replace(/['";]/g, '').trim();
        table.rows = table.rows.filter(r => String(r[col]) !== val);
     } else {
         table.rows = [];
     }

     return {
         success: true,
         message: `${originalCount - table.rows.length} rows deleted`,
         affectedRows: originalCount - table.rows.length,
         executionTime: performance.now() - start
     };
  }
}