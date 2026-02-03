# Contributing to Inception

First off, thank you for considering contributing to Inception! It's people like you that make Inception such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct: be respectful, inclusive, and constructive.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (product ideas that caused issues, error messages)
- **Describe the behavior you observed and what you expected**
- **Include screenshots** if applicable
- **Include your environment details** (OS, Python version, Node version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any alternatives you've considered**

### Pull Requests

1. **Fork the repo** and create your branch from `main`
2. **Follow the coding style** of the project
3. **Add tests** if you've added code that should be tested
4. **Ensure the test suite passes**
5. **Update documentation** if needed
6. **Write a clear PR description**

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run tests
pytest

# Run linting
ruff check .
mypy .
```

### Frontend

```bash
cd frontend
npm install

# Run development server
npm run dev

# Run tests
npm test

# Run linting
npm run lint
```

## Style Guides

### Python Style Guide

- Follow PEP 8
- Use type hints for all functions
- Use docstrings for public functions and classes
- Maximum line length: 100 characters
- Use `ruff` for formatting and linting

### TypeScript Style Guide

- Use TypeScript strict mode
- Prefer functional components with hooks
- Use meaningful variable and function names
- Use ESLint configuration provided

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests when relevant

**Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Example:
```
feat: Add evidence tier badges to customer research display

- Added E1-E4 tier badges with color coding
- Implemented tooltip explanations for each tier
- Updated TypeScript interfaces for evidence data

Closes #123
```

## Project Structure

```
inception/
├── backend/
│   ├── agents/          # AI agent implementations
│   ├── models/          # Pydantic schemas
│   ├── utils/           # Helper utilities
│   └── main.py          # FastAPI application
├── frontend/
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── api/         # API client
│   │   └── types/       # TypeScript types
│   └── package.json
└── docs/                # Documentation
```

## Adding a New Agent

1. Create a new file in `backend/agents/`
2. Extend the `BaseAgent` class
3. Add the agent's prompt in `prompts.py`
4. Register the agent in `orchestrator.py`
5. Add corresponding Pydantic schemas in `models/schemas.py`
6. Update frontend types in `frontend/src/types/api.ts`

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

Thank you for contributing! 🎉
