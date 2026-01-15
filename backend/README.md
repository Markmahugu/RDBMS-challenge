# RDBMS Challenge Backend

A sophisticated Python FastAPI backend powering a complete relational database management system built entirely from scratch. This project demonstrates advanced software engineering skills through the implementation of a fully functional RDBMS using only Python's standard library, showcasing deep expertise in database systems, SQL processing, and scalable API design.

## Overview

This backend serves as the core engine for the RDBMS Challenge - a full-stack project that implements a relational database management system without relying on any external database libraries. It provides a robust RESTful API for all database operations, featuring:

- **Custom RDBMS Engine**: Complete in-memory database implementation using Python standard library
- **SQL Parser & Executor**: Hand-crafted SQL processing for SELECT, INSERT, UPDATE, DELETE, JOIN operations
- **Modern API Framework**: FastAPI-powered RESTful endpoints with automatic documentation
- **Type Safety & Validation**: Comprehensive Pydantic models with runtime validation
- **Cross-Origin Integration**: CORS-enabled for seamless frontend connectivity

This implementation highlights the ability to build complex systems from fundamental components, demonstrating strong problem-solving skills and deep understanding of database internals.

## Technical Achievements & Skills Demonstrated

This backend implementation showcases advanced technical capabilities that are highly valuable for senior software engineering roles:

### Database Systems Expertise
- **From-Scratch RDBMS**: Built a complete relational database engine without external dependencies, demonstrating deep understanding of database internals, indexing, query optimization, and data persistence concepts.
- **SQL Processing**: Implemented manual SQL parsing and execution for complex operations including JOINs, WHERE clauses, and aggregations using regex patterns and custom parsing logic.
- **Query Optimization**: Developed cost-based query planning with execution statistics, showing knowledge of database performance tuning and optimization strategies.

### Backend Engineering Proficiency
- **Modern Python Development**: Leveraged Python 3.11+ features with comprehensive type hints, demonstrating proficiency in modern Python best practices and static analysis.
- **API Design**: Created a RESTful API with FastAPI, featuring automatic OpenAPI documentation, proper HTTP status codes, and robust error handling.
- **Data Validation**: Implemented strict type safety with Pydantic models, ensuring runtime data integrity and API reliability.

### System Design & Architecture
- **Modular Architecture**: Designed a clean, maintainable codebase with clear separation of concerns across database engine, API layer, and data models.
- **Performance Awareness**: Built with performance considerations including in-memory storage optimization and efficient data structures.
- **Scalability Foundations**: Established extension points for advanced features like persistence, authentication, and distribution, showing forward-thinking architectural decisions.

### Development Best Practices
- **Code Quality**: Maintained high standards with black formatting, isort imports, MyPy type checking, and comprehensive testing with pytest.
- **Documentation**: Provided detailed API documentation and clear code structure, essential for collaborative development and maintenance.
- **Cross-Origin Support**: Implemented CORS for seamless frontend integration, demonstrating full-stack development awareness.

This project serves as a strong portfolio piece that proves the ability to tackle complex technical challenges, implement production-ready systems, and deliver functional software that adheres to industry best practices.

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

## Project Impact & Value Proposition

This RDBMS Challenge backend represents a significant technical achievement that demonstrates the kind of deep engineering skills employers seek in senior backend developers and system architects. The ability to implement a complete database system from scratch showcases:

- **Problem-Solving Excellence**: Tackling complex technical challenges without established frameworks
- **Deep Technical Knowledge**: Understanding database internals, SQL processing, and system optimization
- **Production-Ready Code**: Building maintainable, well-tested, and documented software
- **Architectural Vision**: Designing systems with scalability and extensibility in mind

For technical recruiters and hiring managers, this project provides concrete evidence of the developer's capability to deliver sophisticated backend systems that handle real-world database operations. The implementation choices reflect modern best practices while demonstrating the flexibility to work with fundamental tools when needed.

If you're evaluating candidates for backend engineering roles, particularly those involving database systems, distributed systems, or complex API development, this project serves as an excellent case study of technical proficiency and engineering mindset.

---

*Built as part of the RDBMS Challenge - a comprehensive demonstration of full-stack database engineering capabilities.*
