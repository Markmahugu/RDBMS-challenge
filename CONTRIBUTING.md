# Contributing to WebRDBMS

Thank you for your interest in contributing to WebRDBMS! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Project Structure](#project-structure)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Documentation](#documentation)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## Getting Started

### Prerequisites

- **Python 3.11+** with pip
- **Node.js 18+** with npm
- **Git** for version control
- **Make** (optional, for using Makefile commands)

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/username/webrdbms.git
   cd webrdbms
   ```

2. **Set up the development environment**
   ```bash
   # Using Makefile (recommended)
   make setup

   # Or manually
   npm install
   cd frontend && npm install
   cd ../backend && pip install -r requirements.txt
   ```

3. **Set up pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. **Start development servers**
   ```bash
   make dev
   # Or manually in separate terminals:
   # Terminal 1: make dev-backend
   # Terminal 2: make dev-frontend
   ```

## Development Workflow

### 1. Choose an Issue
- Check the [Issues](../../issues) page for open tasks
- Comment on the issue to indicate you're working on it
- Create a new issue if you have a feature idea

### 2. Create a Branch
```bash
# Create and switch to a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number-description
```

### 3. Make Changes
- Write clear, focused commits
- Test your changes thoroughly
- Follow the coding standards below
- Update documentation as needed

### 4. Test Your Changes
```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend

# Check code quality
make lint
```

### 5. Submit a Pull Request
- Push your branch to GitHub
- Create a Pull Request with a clear description
- Reference any related issues
- Wait for review and address feedback

## Project Structure

```
webrdbms/
├── frontend/                 # React/TypeScript UI
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── services/        # API client services
│   │   └── types.ts         # TypeScript definitions
│   ├── package.json
│   └── ...
├── backend/                  # Python FastAPI server
│   ├── app/
│   │   ├── __init__.py      # Package initialization
│   │   ├── main.py         # FastAPI application
│   │   ├── database.py     # Database engine
│   │   └── models.py       # Pydantic models
│   ├── tests/              # Backend tests
│   ├── pyproject.toml      # Python packaging
│   └── requirements.txt    # Dependencies
├── docs/                    # Documentation
├── docker/                  # Docker configuration
├── scripts/                 # Utility scripts
├── Makefile                # Development commands
├── docker-compose.yml      # Container orchestration
├── package.json            # Root monorepo config
└── README.md               # Main documentation
```

## Coding Standards

### Python (Backend)

#### Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Maximum line length: 88 characters (Black default)

#### Type Hints
- Use type hints for all function parameters and return values
- Use modern typing syntax (Union → |, etc.)
- Leverage Pydantic for data validation

#### Example
```python
from typing import List, Optional
from pydantic import BaseModel

class UserSchema(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

def get_users(limit: int = 10) -> List[UserSchema]:
    """Get list of users with optional limit."""
    # Implementation here
    pass
```

### TypeScript/React (Frontend)

#### Code Style
- Use [Prettier](https://prettier.io/) for code formatting
- Follow [ESLint](https://eslint.org/) rules
- Use TypeScript strict mode
- Use functional components with hooks

#### Component Structure
```typescript
import React, { useState, useEffect } from 'react';

interface UserListProps {
  limit?: number;
  onUserSelect?: (userId: string) => void;
}

export const UserList: React.FC<UserListProps> = ({
  limit = 10,
  onUserSelect
}) => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, [limit]);

  const fetchUsers = async () => {
    try {
      const response = await api.getUsers({ limit });
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="user-list">
      {users.map(user => (
        <div key={user.id} onClick={() => onUserSelect?.(user.id)}>
          {user.name}
        </div>
      ))}
    </div>
  );
};
```

### Commit Messages

Follow [Conventional Commits](https://conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing
- `chore`: Maintenance

Examples:
```
feat(auth): add user login functionality
fix(api): handle null values in user query
docs(readme): update installation instructions
```

## Testing

### Backend Testing
```bash
# Run all backend tests
cd backend && python -m pytest

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run specific test file
python -m pytest tests/test_database.py
```

### Frontend Testing
```bash
# Run all frontend tests
cd frontend && npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Test Structure
- **Backend**: Use pytest with fixtures
- **Frontend**: Use Jest and React Testing Library
- Write tests for new features and bug fixes
- Aim for good test coverage (>80%)

## Submitting Changes

### Pull Request Process

1. **Ensure your branch is up to date**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run quality checks**
   ```bash
   make lint
   make test
   ```

3. **Create a Pull Request**
   - Use a descriptive title
   - Reference related issues
   - Provide context and testing instructions
   - Request review from maintainers

4. **Address Review Feedback**
   - Make requested changes
   - Push updates to your branch
   - Maintain clear commit history

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass and coverage is adequate
- [ ] Documentation is updated
- [ ] No breaking changes without migration path
- [ ] Commit messages follow conventions
- [ ] PR description is clear and complete

## Documentation

### Types of Documentation
- **README.md**: Project overview and setup
- **API Documentation**: Auto-generated from FastAPI
- **Code Comments**: Inline documentation for complex logic
- **Architecture Docs**: High-level system design

### Updating Documentation
- Keep README.md current with setup changes
- Document new API endpoints in code
- Update this CONTRIBUTING.md for process changes
- Use docstrings for Python functions
- Use JSDoc for complex TypeScript functions

## Getting Help

- **Issues**: Check existing issues or create new ones
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Refer to README.md and this guide
- **Community**: Join our community chat (if available)

## Recognition

Contributors will be recognized in:
- GitHub repository contributors list
- CHANGELOG.md for significant contributions
- Release notes for major features

Thank you for contributing to WebRDBMS! 🎉
