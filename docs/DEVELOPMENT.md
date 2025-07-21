# Development Guide

## Setting Up Your Development Environment

### Prerequisites
- Python 3.11 or higher
- Git
- Make (optional but recommended)

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aeturnis-Development-Labs-LLC/ascendant.git
   cd ascendant
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Set up development environment**
   ```bash
   make dev-setup
   # Or manually:
   pip install -r requirements.txt
   python scripts/setup_dev_environment.py
   ```

This will:
- Install all dependencies
- Set up pre-commit hooks
- Run initial code quality checks

## Code Quality Standards

### Automated Checks
Pre-commit hooks run automatically on `git commit` and check:
- Code formatting (Black)
- Import sorting (isort)
- Linting (Flake8 with plugins)
- Type checking (mypy)
- Security issues (Bandit)
- File formatting (trailing whitespace, end of file, etc.)

### Manual Commands

Run all checks:
```bash
make pre-commit
# Or:
pre-commit run --all-files
```

Individual checks:
```bash
make format     # Format code with black and isort
make lint       # Run flake8 linting
make typecheck  # Run mypy type checking
make security   # Run bandit security scan
make test       # Run all tests
```

### Code Style
- **Line length**: 100 characters maximum
- **Formatting**: Black with default settings
- **Import order**: isort with Black-compatible profile
- **Docstrings**: Google style, required for all public functions/classes
- **Type hints**: Encouraged but not mandatory (yet)

## Testing

### Running Tests
```bash
make test        # Run all tests
make test-cov    # Run with coverage report
```

### Writing Tests
- All new features must have tests
- Tests go in the `tests/` directory
- Test files must start with `test_`
- Test functions must start with `test_`
- Aim for 80%+ code coverage

### UTF Contract Testing
Each UTF contract must have corresponding tests that validate:
- Expected behavior is implemented
- Edge cases are handled
- Contract requirements are met

## Git Workflow

### Branch Strategy
- `main` - Stable, production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `release/*` - Release preparation branches

### Commit Messages
Follow conventional commits format:
```
type(scope): description

[optional body]

[optional footer]
```

Types: feat, fix, docs, style, refactor, test, chore

### Pre-commit Hooks
If pre-commit blocks your commit:
1. Review the errors
2. Fix the issues
3. Stage the fixes
4. Commit again

To bypass hooks in emergency (not recommended):
```bash
git commit --no-verify -m "Emergency commit"
```

## IDE Configuration

### VS Code
Recommended extensions:
- Python
- Pylance
- Black Formatter
- isort
- Error Lens

Settings (`.vscode/settings.json`):
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=100"],
    "editor.formatOnSave": true,
    "editor.rulers": [100]
}
```

### PyCharm
- Enable Black formatter
- Set line length to 100
- Enable Flake8 inspections
- Configure isort

## Troubleshooting

### Pre-commit Issues
If pre-commit fails to install:
```bash
pip install --upgrade pre-commit
pre-commit clean
pre-commit install
```

### Import Errors
Ensure you're in the virtual environment:
```bash
which python  # Should show venv path
```

### Type Checking Errors
If mypy complains about missing stubs:
```bash
mypy --install-types
```

## Performance Guidelines
- Profile before optimizing
- Keep startup time under 1 second
- Floor generation should be under 100ms
- Memory usage should be reasonable for the feature set

## Security Guidelines
- Never commit credentials or secrets
- Validate all user input
- Use parameterized queries for any database operations
- Keep dependencies updated
- Run security scans regularly

## Documentation
- Update docstrings when changing function behavior
- Keep README.md current
- Update CHANGELOG.md for notable changes
- Document UTF contracts for new features
- Add inline comments for complex logic

## Release Process
1. Update VERSION file
2. Update CHANGELOG.md
3. Run full test suite
4. Create release branch
5. Tag release
6. Update documentation

## Getting Help
- Check existing documentation
- Review UTF contracts
- Ask in development chat
- Create an issue for bugs
- Submit pull requests for improvements