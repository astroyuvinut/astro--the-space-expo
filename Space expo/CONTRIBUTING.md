# Contributing to Space Exploration AI - Satellite Pass Predictor

Thank you for your interest in contributing to the Satellite Pass Predictor! This document provides guidelines and information for contributors.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Development Guidelines](#development-guidelines)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:
- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Development Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/space-expo-satellite-predictor.git
   cd space-expo-satellite-predictor
   ```

2. **Set up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -e ".[dev]"
   ```

3. **Run Tests**
   ```bash
   python -m pytest
   ```

4. **Start Development**
   ```bash
   # Run the optimized Streamlit app
   streamlit run app/streamlit_app_optimized.py

   # Or use the CLI
   python -m src.orbits.pass_predictor_optimized --help
   ```

## How to Contribute

### Types of Contributions
- **Bug fixes** - Fix existing issues
- **Features** - Add new functionality
- **Documentation** - Improve docs, tutorials, or examples
- **Tests** - Add or improve test coverage
- **Performance** - Optimize existing code
- **UI/UX** - Improve user interfaces

### Finding Issues to Work On
- Check the [Issues](https://github.com/yourusername/space-expo-satellite-predictor/issues) page
- Look for issues labeled `good first issue` or `help wanted`
- Check the project roadmap in the README

## Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write descriptive variable and function names
- Keep functions focused on single responsibilities
- Add docstrings to all public functions

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
```
feat: add support for custom TLE sources
fix: handle network timeouts in TLE fetching
docs: update installation instructions
```

### Branch Naming
- Use descriptive names: `feature/add-satellite-database`, `fix/tle-parsing-bug`
- Base feature branches on `main`
- Keep branches focused on single features/fixes

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_pass_predictor.py

# Run performance tests
python performance_comparison.py
```

### Writing Tests
- Place tests in `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Include edge cases and error conditions
- Mock external dependencies (API calls, file I/O)

### Test Coverage
- Aim for >90% code coverage
- Focus on critical paths and error conditions
- Include integration tests for key workflows

## Submitting Changes

### Pull Request Process
1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a pull request on GitHub

### PR Requirements
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Commit messages follow conventional format
- [ ] PR description explains changes and rationale
- [ ] No merge conflicts

## Reporting Issues

### Bug Reports
When reporting bugs, please include:
- **Description**: Clear description of the issue
- **Steps to Reproduce**: Step-by-step instructions
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: Python version, OS, dependencies
- **Logs/Error Messages**: Any relevant output

### Feature Requests
For feature requests, include:
- **Description**: What feature you'd like
- **Use Case**: Why this feature would be useful
- **Implementation Ideas**: Any thoughts on how to implement
- **Alternatives**: Other solutions you've considered

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- GitHub contributors list
- Project documentation

Thank you for contributing to the Satellite Pass Predictor! 🚀