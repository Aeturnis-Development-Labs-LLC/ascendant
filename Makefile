.PHONY: help install dev-setup test lint format typecheck security clean run version pre-commit

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev-setup  - Set up development environment with pre-commit"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code with black and isort"
	@echo "  make typecheck  - Run type checking with mypy"
	@echo "  make security   - Run security checks with bandit"
	@echo "  make pre-commit - Run all pre-commit hooks"
	@echo "  make clean      - Remove build artifacts"
	@echo "  make run        - Run the game"
	@echo "  make version    - Show current version"

install:
	pip install -r requirements.txt

dev-setup: install
	python scripts/setup_dev_environment.py

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	python -m flake8 src tests

format:
	python -m black src tests scripts
	python -m isort src tests scripts

typecheck:
	python -m mypy src

security:
	python -m bandit -r src -ll

pre-commit:
	pre-commit run --all-files

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf .coverage

run:
	python -m src

version:
	@cat VERSION