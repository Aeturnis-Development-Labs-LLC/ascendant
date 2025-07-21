# Ascendant: The Eternal Spire

A roguelike tower climbing game where players must ascend an infinite tower, battling through increasingly difficult floors filled with monsters, traps, and bosses.

## Project Structure

```
ascendant/
├── src/         # Source code
├── tests/       # Unit and integration tests
├── docs/        # Documentation
├── assets/      # Game assets (sprites, sounds, etc.)
├── contracts/   # UTF contracts for CAFE methodology
└── venv/        # Virtual environment (not tracked in git)
```

## Setup

1. Clone the repository
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

```bash
python -m ascendant
```

## Development

This project follows the CAFE (Contract-First, AI-Assisted, Facilitated Engineering) methodology.

### Quick Start for Developers

```bash
make dev-setup      # Set up complete development environment
```

This installs dependencies and configures pre-commit hooks for code quality.

### Testing

```bash
make test           # Run all tests
make test-cov       # Run with coverage report
```

### Code Quality

```bash
make pre-commit     # Run all code quality checks
make format         # Format code with black and isort
make lint           # Lint code with flake8
make typecheck      # Type checking with mypy
make security       # Security scan with bandit
```

Pre-commit hooks automatically run on `git commit` to ensure code quality.

See [Development Guide](docs/DEVELOPMENT.md) for detailed information.

## License

Copyright 2025 Aeturnis Development Labs LLC