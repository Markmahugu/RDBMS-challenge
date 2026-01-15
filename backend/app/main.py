from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import DatabaseEngine
from .models import (
    DatabaseState, QueryResult, CreateDatabaseRequest,
    CreateTableRequest, UpdateTableRequest, ExecuteSQLRequest
)

app = FastAPI(title="RDBMS Challenge API", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database engine instance
db_engine = DatabaseEngine()


@app.get("/")
async def root():
    """API root endpoint"""
    suggested_query = """
-- Welcome to RDBMS Challenge! Here's a suggested query to get you started:
-- This will create a sample database with tables for you to explore.
-- Copy and paste this into the SQL editor and run it.

CREATE DATABASE sample_db;

CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

INSERT INTO users (id, name, email) VALUES (1, 'John Doe', 'john@example.com');
INSERT INTO users (id, name, email) VALUES (2, 'Jane Smith', 'jane@example.com');

-- Or create your own database and tables!
    """.strip()
    return {
        "message": "RDBMS Challenge API",
        "version": "1.0.0",
        "suggestedQuery": suggested_query
    }


@app.get("/databases")
async def list_databases():
    """List all databases"""
    return list(db_engine.databases.keys())


@app.post("/databases")
async def create_database(request: CreateDatabaseRequest):
    """Create a new database"""
    try:
        db_engine.create_database(request.name)
        return {"message": f"Database '{request.name}' created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/databases/{name}")
async def get_database(name: str) -> DatabaseState:
    """Get database state"""
    if name not in db_engine.databases:
        raise HTTPException(status_code=404, detail=f"Database '{name}' not found")

    # Switch to the requested database
    db_engine.current_db_name = name
    return db_engine.get_database_state()


@app.post("/databases/{name}/tables")
async def create_table(name: str, request: CreateTableRequest):
    """Create a new table in the database"""
    if name not in db_engine.databases:
        raise HTTPException(status_code=404, detail=f"Database '{name}' not found")

    db_engine.current_db_name = name
    try:
        db_engine.create_table(request.table)
        return {"message": f"Table '{request.table.name}' created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/databases/{name}/tables/{table_name}")
async def update_table(name: str, table_name: str, request: UpdateTableRequest):
    """Update an existing table"""
    if name not in db_engine.databases:
        raise HTTPException(status_code=404, detail=f"Database '{name}' not found")

    db_engine.current_db_name = name
    try:
        old_name = request.oldName or table_name
        db_engine.update_table(old_name, request.table)
        return {"message": f"Table '{old_name}' updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/databases/{name}/tables/{table_name}")
async def drop_table(name: str, table_name: str):
    """Drop a table"""
    if name not in db_engine.databases:
        raise HTTPException(status_code=404, detail=f"Database '{name}' not found")

    db_engine.current_db_name = name
    try:
        db_engine.drop_table(table_name)
        return {"message": f"Table '{table_name}' dropped successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/databases/{name}/query")
async def execute_query(name: str, request: ExecuteSQLRequest) -> QueryResult:
    """Execute SQL query"""
    if name not in db_engine.databases:
        raise HTTPException(status_code=404, detail=f"Database '{name}' not found")

    db_engine.current_db_name = name
    result = db_engine.execute_sql(request.query)

    # Convert the result to a dict for JSON response
    return result


@app.post("/databases/{name}/reset")
async def reset_database(name: str):
    """Reset database to empty state"""
    if name not in db_engine.databases:
        raise HTTPException(status_code=404, detail=f"Database '{name}' not found")

    db_engine.current_db_name = name
    db_engine.reset_database()
    return {"message": f"Database '{name}' reset to empty state"}


@app.put("/databases/{name}/cells/{table_name}")
async def update_cell(name: str, table_name: str, row_index: int, column: str, value: str):
    """Update a specific cell in a table"""
    if name not in db_engine.databases:
        raise HTTPException(status_code=404, detail=f"Database '{name}' not found")

    db_engine.current_db_name = name
    db = db_engine.databases[name]
    table = next((t for t in db.tables if t.name == table_name), None)
    if not table:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")

    if row_index >= len(table.rows):
        raise HTTPException(status_code=400, detail="Row index out of bounds")

    # Convert value based on column type
    col_def = next((c for c in table.columns if c.name == column), None)
    final_value = value
    if col_def and col_def.type in ['INT', 'DECIMAL']:
        try:
            final_value = int(float(value))
        except ValueError:
            final_value = value

    table.rows[row_index][column] = final_value

    return {"message": f"Updated {table_name} row {row_index}, column {column}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
