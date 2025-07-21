# Changelog

All notable changes to Ascendant: The Eternal Spire will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-07-21

### Added
- Core enumerations (TileType, Direction, ItemType, EntityType) in `src/enums.py`
- Direction enum with movement vectors (dx, dy)
- Tile data structure with immutable position and occupancy validation
- Entity abstract base class with immutable position and UUID generation
- Item base class with name validation and UUID generation
- Comprehensive test suite for all data structures (39 new tests)
- Type hints throughout all new code

### Contract Coverage
- GAME-CORE-002: Core Enumerations ✅
- GAME-CORE-003: Tile Data Structure ✅
- GAME-CORE-004: Entity Base Class ✅
- GAME-CORE-005: Item Base Class ✅

## [0.1.0] - 2025-07-21

### Added
- Initial project structure with `/src`, `/tests`, `/docs`, `/assets`, `/contracts` directories
- Python 3.11+ virtual environment support
- Basic entry point that displays game title
- Development dependencies (pytest, pytest-cov, mypy, black, flake8)
- UTF contract GAME-CORE-001 implementation
- Comprehensive test suite for project initialization
- README with setup instructions
- Python package configuration (setup.py)
- Git repository with proper .gitignore

### Contract Coverage
- GAME-CORE-001: Project Initialization ✅

[Unreleased]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/releases/tag/v0.1.0
