# Ascendant: The Eternal Spire - Game Client

[![CI](https://github.com/Aeturnis-Development-Labs-LLC/ascendant/actions/workflows/ci.yml/badge.svg)](https://github.com/Aeturnis-Development-Labs-LLC/ascendant/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.16.0-green)](VERSION)

The game client for Ascendant: The Eternal Spire - a roguelike tower climbing game where players must ascend an infinite tower, battling through increasingly difficult floors filled with monsters, traps, and bosses.

This package (`ascendant-client`) contains the game engine, rendering systems, and client-side logic. The server component will be developed separately in Phase 5.

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

## Current Features (v0.16.0)

### Core Systems
- **Procedural Dungeon Generation**: Rooms, corridors, and multi-floor towers
- **ASCII Rendering**: Classic roguelike display with fog of war
- **Movement System**: 8-directional movement with stamina costs
- **PyQt6 Client**: Modern GUI with map display, character panel, and mini-map

### World Features
- **World Map**: Overworld with multiple dungeons and special locations
- **Safe Haven**: Central hub with Lost Souls memorial system
- **Fast Travel**: Between discovered locations
- **Environmental Hazards**: Storms, avalanches, and other dangers

### Combat Systems (NEW in v0.16.0)
- **Combat Engine**: ATK-DEF damage formula with critical hits
- **Monster System**: 6 monster types with AI behaviors
- **Death Handling**: Entity removal, experience awards, and loot drops
- **Trap System**: Spike, poison, and alarm traps with scaling damage
- **Loot System**: Monster-specific drop tables with luck modifiers
- **Combat Log**: Real-time battle message tracking

### UTF Contracts Implemented
- 43/72 contracts completed (59.7%)
- Full compliance with CAFE methodology
- 87.63% test coverage across combat modules

## License

Copyright 2025 Aeturnis Development Labs LLC
