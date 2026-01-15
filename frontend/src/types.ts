export type DataType = 'INT' | 'VARCHAR' | 'TEXT' | 'DATE' | 'DATETIME' | 'DECIMAL' | 'BOOLEAN';

export interface ColumnSchema {
  id: string;
  name: string;
  type: DataType;
  length?: number;
  nullable: boolean;
  defaultValue?: string;
  isPrimaryKey: boolean;
  isUnique?: boolean;
  isForeignKey?: boolean;
  autoIncrement?: boolean;
  references?: {
    tableId: string;
    columnId: string;
  };
}

export interface TableSchema {
  id: string;
  name: string;
  columns: ColumnSchema[];
  rows: Record<string, any>[];
  indexes: IndexSchema[];
}

export interface IndexSchema {
  id: string;
  name: string;
  columnIds: string[];
  type: 'BTREE' | 'HASH' | 'UNIQUE';
}

export interface DatabaseState {
  name: string;
  tables: TableSchema[];
}

export interface QueryResult {
  success: boolean;
  message?: string;
  data?: any[];
  columns?: string[];
  executionTime?: number;
  affectedRows?: number;
  plan?: ExecutionPlanNode;
}

export interface ExecutionPlanNode {
  type: 'SCAN' | 'SEEK' | 'JOIN' | 'FILTER' | 'PROJECTION' | 'SORT' | 'LIMIT';
  tableName?: string;
  cost: number;
  details: string;
  children?: ExecutionPlanNode[];
}

export interface TabItem {
  id: string;
  type: 'sql' | 'designer' | 'schema' | 'explorer' | 'table-data';
  title: string;
  active: boolean;
  data?: any;
}

export interface LogEntry {
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'error';
  details?: string;
}
