# WebRDBMS Backend

Python FastAPI backend for the WebRDBMS relational database management system.

## Overview

This backend provides a RESTful API for database operations, featuring:

- **In-memory RDBMS** built with Python standard library
- **Manual SQL parsing** for SELECT, INSERT, UPDATE, DELETE, JOIN operations
- **RESTful API** with FastAPI framework
- **Type safety** with Pydantic models
- **CORS support** for frontend integration

## Architecture

```
backend/
├── app/                    # Main application package
│   ├── __init__.py        # Package initialization
│   ├── main.py           # FastAPI application & routes
│   ├── database.py       # Database engine (standard library only)
│   └── models.py         # Pydantic data models
├── tests/                # Test suite
├── pyproject.toml        # Modern Python packaging
├── requirements.txt      # Legacy dependency management
└── README.md            # This file
```

## Key Components

### Database Engine (`database.py`)
- Pure Python implementation using only standard library
- Manual SQL parsing with regex patterns
- Support for JOIN, WHERE, LIMIT clauses
- Execution plan generation with cost estimation
- In-memory storage with proper data typing

### API Layer (`main.py`)
- FastAPI application with automatic OpenAPI documentation
- RESTful endpoints for all database operations
- CORS middleware for frontend integration
- Comprehensive error handling

### Data Models (`models.py`)
- Pydantic models for request/response validation
- Type-safe data structures
- Automatic serialization/deserialization

## Development

### Prerequisites
- Python 3.11+
- pip package manager

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or with modern packaging
pip install -e .[dev]
```

### Running the Server
```bash
# Development mode
python -m app.main

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
When running, visit `http://localhost:8000/docs` for interactive API documentation.

### Testing
```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

### Code Quality
```bash
# Format code
black app/
isort app/

# Type checking
mypy app/

# Lint
flake8 app/
```

## API Endpoints

### Database Management
- `GET /databases` - List databases
- `POST /databases` - Create database
- `GET /databases/{name}` - Get database state
- `POST /databases/{name}/reset` - Reset to demo data

### Table Operations
- `POST /databases/{name}/tables` - Create table
- `PUT /databases/{name}/tables/{table}` - Update table
- `DELETE /databases/{name}/tables/{table}` - Drop table

### Data Operations
- `POST /databases/{name}/query` - Execute SQL
- `PUT /databases/{name}/cells/{table}` - Update cell

## Design Principles

### Standard Library Only
The database engine uses only Python standard library:
- `collections` for data structures
- `re` for SQL parsing
- `time` for performance measurement
- `typing` for type hints

### Manual SQL Parsing
- No external SQL parsing libraries
- Regex-based query analysis
- Support for essential SQL operations
- Proper error handling for malformed queries

### Type Safety
- Full Pydantic validation
- Type hints throughout codebase
- MyPy for static type checking
- Runtime type validation

## Performance Characteristics

- **In-memory storage**: Fast access but volatile
- **Simple indexing**: B-tree/hash support for WHERE optimization
- **Cost-based planning**: Query execution planning
- **Minimal overhead**: Lightweight implementation

## Extension Points

- **Persistent storage**: Add file-based or external database persistence
- **Advanced SQL**: Subqueries, aggregations, stored procedures
- **Authentication**: User management and access control
- **Optimization**: Query optimization and caching layers
- **Distribution**: Multi-node database clustering

## Contributing

Follow the main project contributing guidelines. For backend-specific changes:

1. Ensure type hints are complete
2. Add tests for new functionality
3. Update API documentation
4. Follow PEP 8 style guidelines
5. Use black/isort for formatting
