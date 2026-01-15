# WebRDBMS - Relational Database Management System

A complete relational database management system implementation featuring both a **React frontend** for database management and a **Python FastAPI backend** for database operations.

## Features

### Database Engine (Python Backend)
- **In-memory relational database** using Python standard library
- **SQL query execution** (SELECT, INSERT, UPDATE, DELETE, JOIN, WHERE, LIMIT)
- **Table management** with column definitions (INT, VARCHAR, TEXT, DATE, DATETIME, DECIMAL, BOOLEAN)
- **Primary keys and foreign keys** with referential integrity
- **Basic indexing** support (BTREE, HASH, UNIQUE)
- **Execution planning** with cost estimation
- **RESTful API** with FastAPI

### Frontend (React/TypeScript)
- **Interactive SQL editor** with query execution and results display
- **Table designer** for creating/editing table schemas
- **Schema visualizer** with relationship diagrams
- **Data viewer/editor** for table contents
- **Tabbed interface** for multiple concurrent operations
- **Dark/light mode** theming
- **Query history** and execution logging

### Demo Data
Pre-loaded with sample database containing:
- **Departments** table (id, name, location)
- **Employees** table (id, name, role, department_id, salary)
- **Projects** table (id, name, budget)

## Architecture

```
├── frontend/          # React/TypeScript UI
│   ├── components/    # UI components
│   ├── services/      # API client (DatabaseAPI)
│   └── types.ts       # TypeScript definitions
├── backend/           # Python FastAPI server
│   ├── database.py    # Database engine (standard library only)
│   ├── models.py      # Pydantic data models
│   └── main.py        # FastAPI application
└── README.md
```

## Prerequisites

- **Node.js** (for frontend)
- **Python 3.11+** (for backend)

## Run Locally

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```
The backend will start on `http://localhost:8000`

### Frontend Setup
```bash
npm install
npm run dev
```
The frontend will start on `http://localhost:3000`

### Access the Application
Open `http://localhost:3000` in your browser to use the database management interface.

## API Endpoints

- `GET /databases` - List databases
- `POST /databases` - Create database
- `GET /databases/{name}` - Get database state
- `POST /databases/{name}/tables` - Create table
- `PUT /databases/{name}/tables/{table}` - Update table
- `DELETE /databases/{name}/tables/{table}` - Drop table
- `POST /databases/{name}/query` - Execute SQL
- `POST /databases/{name}/reset` - Reset to demo data
- `PUT /databases/{name}/cells/{table}` - Update cell value

## SQL Features

### Supported Operations
- **SELECT** with JOIN, WHERE, LIMIT
- **INSERT** with column specification
- **UPDATE** (simplified)
- **DELETE** with WHERE conditions
- **DROP TABLE**

### Example Queries
```sql
SELECT * FROM employees WHERE department_id = 1;
SELECT e.name, d.name FROM employees e JOIN departments d ON e.department_id = d.id;
INSERT INTO employees (name, role, salary) VALUES ('John Doe', 'Developer', 80000);
DELETE FROM employees WHERE id = 101;
```

## Development Notes

- **Backend**: Pure Python standard library for database logic (no external DB engines or ORMs)
- **SQL Parsing**: Manual regex-based parsing (no external SQL libraries)
- **Data Storage**: In-memory (easily extensible to persistent storage)
- **Type Safety**: Full TypeScript on frontend, Pydantic on backend
