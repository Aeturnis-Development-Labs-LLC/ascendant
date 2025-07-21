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

### Testing

```bash
pytest
pytest --cov=src  # With coverage
```

### Code Quality

```bash
black src tests      # Format code
flake8 src tests    # Lint code
mypy src            # Type checking
```

## License

Copyright 2025 Aeturnis Development Labs LLC