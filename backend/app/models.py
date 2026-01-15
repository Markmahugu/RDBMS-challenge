from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel


DataType = Literal['INT', 'VARCHAR', 'TEXT', 'DATE', 'DATETIME', 'DECIMAL', 'BOOLEAN']


class ColumnSchema(BaseModel):
    id: str
    name: str
    type: DataType
    length: Optional[int] = None
    nullable: bool = True
    defaultValue: Optional[str] = None
    isPrimaryKey: bool = False
    isUnique: Optional[bool] = None
    isForeignKey: Optional[bool] = None
    autoIncrement: Optional[bool] = None
    references: Optional[Dict[str, str]] = None


class IndexSchema(BaseModel):
    id: str
    name: str
    columnIds: List[str]
    type: Literal['BTREE', 'HASH', 'UNIQUE'] = 'BTREE'


class TableSchema(BaseModel):
    id: str
    name: str
    columns: List[ColumnSchema]
    rows: List[Dict[str, Any]]
    indexes: List[IndexSchema]


class DatabaseState(BaseModel):
    name: str
    tables: List[TableSchema]


class ExecutionPlanNode(BaseModel):
    type: Literal['SCAN', 'SEEK', 'JOIN', 'FILTER', 'PROJECTION', 'SORT', 'LIMIT']
    tableName: Optional[str] = None
    cost: float
    details: str
    children: Optional[List['ExecutionPlanNode']] = None


class QueryResult(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    columns: Optional[List[str]] = None
    executionTime: Optional[float] = None
    affectedRows: Optional[int] = None
    plan: Optional[ExecutionPlanNode] = None


class CreateDatabaseRequest(BaseModel):
    name: str


class CreateTableRequest(BaseModel):
    table: TableSchema


class UpdateTableRequest(BaseModel):
    table: TableSchema
    oldName: Optional[str] = None


class ExecuteSQLRequest(BaseModel):
    query: str
