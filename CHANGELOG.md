# Changelog

All notable changes to Ascendant: The Eternal Spire will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2025-07-22

### Added
- ASCII renderer with fog of war in `src/renderers/ascii_renderer.py`
- Trap placement system in `Floor.place_traps()` with density control
- Chest generation in `Floor.place_chests()` with loot tier system
- STAIRS_DOWN tile type for complete dungeon navigation
- Width and height properties on Floor class for easier access
- Comprehensive test suite for visualization (20 new tests)
- Performance benchmarking for all visualization features

### Performance
- ASCII Rendering (fog): 0.106ms average (target <10ms) ✅
- Full Map Rendering: 0.247ms average (target <20ms) ✅
- Trap Placement: 0.622ms average (target <5ms) ✅
- Chest Generation: 0.635ms average (target <5ms) ✅
- Complete Floor: 0.752ms average (target <100ms) ✅

### Contract Coverage
- GAME-MAP-005: ASCII Renderer ✅
- GAME-MAP-006: Trap Placement ✅
- GAME-MAP-007: Chest Generation ✅

## [0.4.0] - 2025-07-21

### Added
- Room connection algorithm using L-shaped corridors in `Floor.connect_rooms()`
- Stairs placement functionality in `Floor.place_stairs()`
- Connectivity validation with pathfinding in `Floor.is_fully_connected()`
- Comprehensive test suite for room connections (12 new tests)
- Performance benchmark scripts for floor operations
- Edge case testing for 100x100 floors demonstrating excellent scalability
- Visualization script for connected floors with stairs

### Performance
- Floor Generation: 0.44ms average (target <100ms) ✅
- Room Connection: 0.05ms average (target <50ms) ✅
- Pathfinding Check: 0.17ms average (target <50ms) ✅
- Full Floor Creation: 0.65ms average (target <500ms) ✅

### Contract Coverage
- GAME-MAP-003: Room Connection ✅
- GAME-MAP-004: Stairs Placement ✅

## [0.3.0] - 2025-07-21

### Added
- Floor generation system with 20x20 grid in `src/models/floor.py`
- Room class with overlap detection and minimum distance support
- Seed-based reproducible floor generation
- Generation of 5-10 rectangular rooms (3x3 to 8x8 tiles)
- Edge buffer of 1 tile from floor boundaries
- Four visualization scripts for debugging floor layouts
- Comprehensive test suite for floor generation (18 new tests)

### Fixed
- Room adjacency issue where rooms appeared connected
- Import sorting in scripts to satisfy CI/CD checks

### Contract Coverage
- GAME-MAP-001: Floor Generation System ✅
- GAME-MAP-002: Room Generation Algorithm ✅

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

[Unreleased]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/releases/tag/v0.1.0
