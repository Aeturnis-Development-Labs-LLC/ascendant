.PHONY: help install test lint format typecheck clean run version

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code with black"
	@echo "  make typecheck  - Run type checking with mypy"
	@echo "  make clean      - Remove build artifacts"
	@echo "  make run        - Run the game"
	@echo "  make version    - Show current version"

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	python -m flake8 src tests

format:
	python -m black src tests

typecheck:
	python -m mypy src

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