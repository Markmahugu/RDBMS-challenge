import { DatabaseState, TableSchema, ColumnSchema, QueryResult, ExecutionPlanNode } from '../types';

export class DatabaseAPI {
  private baseUrl: string;
  private currentDbName: string;
  private dbState: DatabaseState | null = null;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.currentDbName = 'DemoDB';
  }

  private async apiRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${error}`);
    }

    return response.json();
  }

  public async getDatabaseState(forceRefresh: boolean = false): Promise<DatabaseState> {
    if (!this.dbState || forceRefresh) {
      this.dbState = await this.apiRequest<DatabaseState>(`/databases/${this.currentDbName}`);
    }
    return this.dbState;
  }

  public async createDatabase(name: string): Promise<void> {
    await this.apiRequest('/databases', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
    this.currentDbName = name;
    this.dbState = null; // Force refresh
  }

  public async listDatabases(): Promise<string[]> {
    return this.apiRequest<string[]>('/databases');
  }

  public async switchDatabase(name: string): Promise<void> {
    this.currentDbName = name;
    this.dbState = null; // Force refresh
  }

  public async createTable(table: TableSchema): Promise<void> {
    await this.apiRequest(`/databases/${this.currentDbName}/tables`, {
      method: 'POST',
      body: JSON.stringify({ table }),
    });
    this.dbState = null; // Force refresh
  }

  public async updateTable(oldName: string, newSchema: TableSchema): Promise<void> {
    await this.apiRequest(`/databases/${this.currentDbName}/tables/${oldName}`, {
      method: 'PUT',
      body: JSON.stringify({ table: newSchema, oldName }),
    });
    this.dbState = null; // Force refresh
  }

  public async dropTable(tableName: string): Promise<void> {
    await this.apiRequest(`/databases/${this.currentDbName}/tables/${tableName}`, {
      method: 'DELETE',
    });
    this.dbState = null; // Force refresh
  }

  public async resetDatabase(): Promise<void> {
    await this.apiRequest(`/databases/${this.currentDbName}/reset`, {
      method: 'POST',
    });
    this.dbState = null; // Force refresh
  }

  public async updateCell(tableName: string, rowIndex: number, colName: string, value: any): Promise<QueryResult> {
    const result = await this.apiRequest<{message: string}>(`/databases/${this.currentDbName}/cells/${tableName}`, {
      method: 'PUT',
      body: JSON.stringify({ row_index: rowIndex, column: colName, value }),
    });
    this.dbState = null; // Force refresh
    return {
      success: true,
      message: result.message,
      executionTime: 0
    };
  }

  public async executeSQL(query: string): Promise<QueryResult> {
    const result = await this.apiRequest<QueryResult>(`/databases/${this.currentDbName}/query`, {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
    return result;
  }

  // For compatibility with existing code that expects synchronous methods
  public async togglePrimaryKey(tableName: string, columnName: string): Promise<void> {
    // This is a frontend-only operation for schema visualization
    // In a real implementation, this would update the schema on the backend
    const state = await this.getDatabaseState();
    const table = state.tables.find(t => t.name === tableName);
    if (table) {
      const col = table.columns.find(c => c.name === columnName);
      if (col) {
        col.isPrimaryKey = !col.isPrimaryKey;
      }
    }
  }
}
