# WebRDBMS - Relational Database Management System

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2.3-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8.2-3178C6.svg)](https://www.typescriptlang.org/)

A complete relational database management system implementation featuring both a **React frontend** for database management and a **Python FastAPI backend** for database operations. Built from scratch using only standard libraries where possible, demonstrating core database concepts and full-stack development.

## 🎯 Project Overview

WebRDBMS is an educational and functional relational database management system that showcases:

- **Database Engine Design**: Complete RDBMS implementation using Python standard library
- **SQL Query Processing**: Manual SQL parsing and execution engine
- **RESTful API Design**: Modern API architecture with FastAPI
- **Frontend Architecture**: React-based database management interface
- **Full-Stack Integration**: Seamless communication between frontend and backend

The system provides all essential RDBMS features while maintaining simplicity and educational value.

## ✨ Features

### Database Engine (Python Backend)
- 🔄 **In-memory relational database** using Python standard library
- 📊 **SQL query execution** (SELECT, INSERT, UPDATE, DELETE, JOIN, WHERE, LIMIT)
- 🏗️ **Table management** with column definitions (INT, VARCHAR, TEXT, DATE, DATETIME, DECIMAL, BOOLEAN)
- 🔑 **Primary keys and foreign keys** with referential integrity
- 📈 **Basic indexing** support (BTREE, HASH, UNIQUE)
- 📋 **Execution planning** with cost estimation
- 🌐 **RESTful API** with FastAPI and automatic OpenAPI documentation

### Frontend (React/TypeScript)
- 💻 **Interactive SQL editor** with syntax highlighting and query execution
- 🎨 **Table designer** for creating/editing table schemas with drag-and-drop
- 📊 **Schema visualizer** with relationship diagrams and D3.js rendering
- 📝 **Data viewer/editor** for browsing and modifying table contents
- 📑 **Tabbed interface** for multiple concurrent operations
- 🌙 **Dark/light mode** theming with smooth transitions
- 📜 **Query history** and execution logging
- 🎯 **Real-time feedback** with execution times and result counts

### Sample Database
Pre-loaded with a comprehensive demo database:
- **🏢 Departments** table: Company department information
- **👥 Employees** table: Staff details with department relationships
- **📁 Projects** table: Project management data

## 🏗️ Architecture

```
webrdbms/                      # Monorepo Root
├── frontend/                  # React/TypeScript UI Application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   │   ├── SQLEditor.tsx    # SQL query interface
│   │   │   ├── TableDesigner.tsx # Table schema designer
│   │   │   ├── SchemaVisualizer.tsx # Database diagram
│   │   │   ├── TableDataViewer.tsx # Data browser/editor
│   │   │   └── Sidebar.tsx      # Navigation panel
│   │   ├── services/         # API client services
│   │   │   └── DatabaseEngine.ts # DatabaseAPI client
│   │   ├── App.tsx          # Main application component
│   │   ├── index.tsx        # Application entry point
│   │   └── types.ts         # TypeScript type definitions
│   ├── public/              # Static assets
│   ├── package.json         # Frontend dependencies
│   ├── tsconfig.json        # TypeScript configuration
│   └── vite.config.ts       # Vite build configuration
├── backend/                  # Python FastAPI Server
│   ├── app/                 # Main application package
│   │   ├── __init__.py      # Package initialization
│   │   ├── main.py          # FastAPI application & routes
│   │   ├── database.py      # Database engine implementation
│   │   └── models.py        # Pydantic data models
│   ├── tests/               # Test suite (structure ready)
│   ├── pyproject.toml       # Modern Python packaging
│   ├── requirements.txt     # Legacy dependencies
│   └── README.md           # Backend-specific documentation
├── docker/                  # Containerization
│   ├── Dockerfile.frontend  # Frontend container
│   └── Dockerfile.backend   # Backend container
├── docs/                    # Additional documentation
├── scripts/                 # Utility scripts (structure ready)
├── .github/                 # GitHub configuration (structure ready)
├── docker-compose.yml       # Multi-service orchestration
├── Makefile                # Development automation
├── package.json            # Root monorepo configuration
├── .gitignore              # Comprehensive ignore rules
├── .pre-commit-config.yaml # Code quality hooks
├── CONTRIBUTING.md         # Contribution guidelines
└── README.md              # This documentation
```

### Data Flow
1. **User Interaction** → React components handle UI events
2. **API Requests** → DatabaseAPI client sends HTTP requests to backend
3. **Query Processing** → FastAPI routes receive requests and delegate to database engine
4. **SQL Execution** → Database engine parses and executes SQL queries
5. **Result Return** → Processed data flows back through the API to the frontend
6. **UI Update** → React components update with new data and provide user feedback

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** with pip package manager
- **Node.js 18+** with npm package manager
- **Git** for cloning the repository
- **Make** (optional, for streamlined commands)

### Installation & Setup

#### Option 1: Using Makefile (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd webrdbms

# Set up everything automatically
make setup

# Start both services
make dev
```

#### Option 2: Manual Setup

**1. Clone and Install Dependencies**
```bash
git clone <repository-url>
cd webrdbms

# Install root dependencies
npm install

# Install frontend dependencies
cd frontend && npm install && cd ..

# Install backend dependencies
cd backend && pip install -r requirements.txt && cd ..
```

**2. Start the Backend**
```bash
# Terminal 1: Start FastAPI server
cd backend && python -m app.main
```
Backend available at `http://localhost:8000`

**3. Start the Frontend**
```bash
# Terminal 2: Start React development server
cd frontend && npm run dev
```
Frontend available at `http://localhost:3000`

#### Option 3: Using Docker
```bash
# Build and start services
docker-compose up --build

# Or use Makefile
make docker-up
```

### Access the Application
Open `http://localhost:3000` in your browser to use WebRDBMS!

### Health Check
```bash
# Check if both services are running
make check-health
```

## 📖 Usage Guide

### Getting Started
1. **Database Overview**: The main interface shows the current database with available tables
2. **SQL Queries**: Click "SQL Query" tab or use the sidebar to start writing queries
3. **Table Management**: Use "New Table" to design custom table schemas
4. **Data Exploration**: Click on table names in the sidebar to browse data

### SQL Query Examples

#### Basic SELECT Queries
```sql
-- View all employees
SELECT * FROM employees;

-- Filter by department
SELECT * FROM employees WHERE department_id = 1;

-- Limit results
SELECT * FROM employees LIMIT 3;
```

#### JOIN Operations
```sql
-- Employees with department names
SELECT e.name, e.role, d.name as department
FROM employees e
JOIN departments d ON e.department_id = d.id;

-- Projects with budgets over 50k
SELECT p.name, p.budget
FROM projects p
WHERE p.budget > 50000;
```

#### Data Modification
```sql
-- Insert new employee
INSERT INTO employees (name, role, department_id, salary)
VALUES ('Jane Smith', 'Designer', 4, 75000);

-- Update existing record
UPDATE employees
SET salary = salary * 1.1
WHERE role = 'Engineer';

-- Delete record
DELETE FROM employees WHERE id = 106;
```

### Table Design
1. Click "New Table" in the sidebar
2. Define table name and columns:
   - **Column Name**: Identifier for the column
   - **Type**: Data type (INT, VARCHAR, DECIMAL, etc.)
   - **Length**: Size constraint for VARCHAR columns
   - **Nullable**: Whether the column can contain NULL values
   - **PK**: Primary key designation
3. Add/remove columns as needed
4. Save the table schema

### Schema Visualization
- Click "Schema Diagram" tab to view database relationships
- Interactive diagram shows tables and their connections
- Click table nodes to edit schemas
- Visual representation of foreign key relationships

## 🔌 API Documentation

### Base URL
```
http://localhost:8000
```

### Core Endpoints

#### Database Management
```http
GET    /databases              # List all databases
POST   /databases              # Create new database
GET    /databases/{name}       # Get database state
POST   /databases/{name}/reset # Reset database to demo data
```

#### Table Operations
```http
POST   /databases/{name}/tables           # Create table
PUT    /databases/{name}/tables/{table}   # Update table schema
DELETE /databases/{name}/tables/{table}   # Drop table
```

#### Data Operations
```http
POST   /databases/{name}/query            # Execute SQL query
PUT    /databases/{name}/cells/{table}    # Update cell value
```

### Request/Response Examples

#### Execute SQL Query
```bash
curl -X POST http://localhost:8000/databases/DemoDB/query \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * FROM employees LIMIT 2"}'
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 101,
      "name": "Alice Johnson",
      "role": "Senior Engineer",
      "department_id": 1,
      "salary": 95000
    }
  ],
  "columns": ["id", "name", "role", "department_id", "salary"],
  "executionTime": 0.0012,
  "plan": {
    "type": "SCAN",
    "tableName": "employees",
    "cost": 0.5,
    "details": "Full Table Scan on employees",
    "children": []
  }
}
```

#### Create Table
```bash
curl -X POST http://localhost:8000/databases/DemoDB/tables \
  -H "Content-Type: application/json" \
  -d '{
    "table": {
      "id": "users",
      "name": "users",
      "columns": [
        {
          "id": "u1",
          "name": "id",
          "type": "INT",
          "nullable": false,
          "isPrimaryKey": true
        },
        {
          "id": "u2",
          "name": "username",
          "type": "VARCHAR",
          "length": 50,
          "nullable": false
        }
      ],
      "rows": [],
      "indexes": []
    }
  }'
```

### Data Types Supported
- `INT`: Integer values
- `VARCHAR`: Variable-length strings (requires length)
- `TEXT`: Long text content
- `DECIMAL`: Floating-point numbers
- `BOOLEAN`: True/false values
- `DATE`: Date values (YYYY-MM-DD)
- `DATETIME`: Date and time values

### Error Handling
All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad Request (validation errors)
- `404`: Not Found (database/table doesn't exist)
- `500`: Internal Server Error

Error responses include detailed error messages in the response body.

## 🔧 Development

### Backend Development
The backend is built with FastAPI and follows these principles:

- **Standard Library Only**: Database engine uses only Python standard library
- **Manual SQL Parsing**: No external SQL parsing libraries
- **Type Safety**: Full Pydantic model validation
- **Async/Await**: Modern Python async patterns

#### Key Files:
- `backend/database.py`: Core database engine with SQL execution
- `backend/models.py`: Pydantic models for API data validation
- `backend/main.py`: FastAPI application with route definitions

### Frontend Development
The frontend uses modern React patterns:

- **TypeScript**: Full type safety throughout the application
- **Component Architecture**: Modular, reusable components
- **API Abstraction**: Clean separation between UI and data fetching
- **State Management**: React hooks for local component state

#### Key Technologies:
- React 19 with modern hooks
- TypeScript for type safety
- Tailwind CSS for styling
- Lucide React for icons
- D3.js for data visualization

### Running Tests
```bash
# Backend tests (if implemented)
cd backend
python -m pytest

# Frontend tests (if implemented)
npm test
```

### Building for Production
```bash
# Build frontend
npm run build

# Backend runs with uvicorn in production
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🎓 Educational Value

This project demonstrates:

### Database Concepts
- **Relational Model**: Tables, relationships, constraints
- **SQL Processing**: Lexical analysis, parsing, execution planning
- **Indexing**: B-tree and hash index implementations
- **Query Optimization**: Cost-based execution planning

### Software Engineering
- **API Design**: RESTful principles, HTTP status codes, error handling
- **Type Safety**: TypeScript and Pydantic integration
- **Component Design**: React patterns, state management
- **Full-Stack Architecture**: Frontend-backend communication

### Python Best Practices
- **Standard Library Usage**: Building complex systems without external dependencies
- **Async Programming**: Modern Python concurrency patterns
- **Data Structures**: Efficient use of dicts, lists, and dataclasses

### Web Development
- **Modern React**: Hooks, context, component composition
- **Responsive Design**: Mobile-friendly interfaces
- **User Experience**: Loading states, error handling, feedback

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines
- Follow existing code style and patterns
- Add tests for new features
- Update documentation for API changes
- Ensure type safety in both Python and TypeScript code
- Test both frontend and backend functionality

### Areas for Enhancement
- Persistent storage (file-based or database backend)
- Advanced SQL features (subqueries, aggregations, views)
- User authentication and authorization
- Query optimization and performance improvements
- Additional data types and constraints
- Export/import functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built as an educational project to demonstrate RDBMS concepts
- Inspired by real-world database management systems
- Uses modern web technologies for the user interface
- Follows best practices in both Python and JavaScript ecosystems

## 📞 Support

If you have questions or need help:

1. Check the [Issues](../../issues) page for common problems
2. Review the API documentation above
3. Create a new issue with detailed information

---

**Happy querying!** 🎉
