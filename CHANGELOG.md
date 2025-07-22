# Changelog

All notable changes to Ascendant: The Eternal Spire will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.0] - 2025-07-22

### Added
- World Map Features (Phase 2.4)
  - Fog of war system with terrain-based vision radius
  - Fast travel system (walking free, carriage 50g/10 tiles)
  - Random encounters with terrain-specific distributions
  - Environmental hazards (weather system + terrain hazards)
  - Location entry/exit mechanics
  - World map ASCII renderer with weather display
- 45 new tests for world map features

### Changed
- Package renamed from `ascendant` to `ascendant-client` to clarify this is the game client
- Console entry point renamed to `ascendant-client`

### Contract Coverage
- GAME-WORLD-004: Fog of war system ✅
- GAME-WORLD-005: Fast travel system ✅
- GAME-WORLD-006: Random encounters ✅
- GAME-WORLD-007: Environmental hazards ✅

## [0.7.0] - 2025-07-22

### Added
- StaminaSystem class for managing action costs and regeneration in `src/game/stamina_system.py`
- ActionType enum for different action categories
- Stamina management in Character class with proper bounds checking
- Performance benchmarking script for stamina operations
- Comprehensive stamina test suite (17 new tests, all passing)

### Performance
- Can Perform Action: 2,386,526 ops/sec (0.000ms per check) ✅
- Execute Action: 1,068,612 ops/sec (0.001ms per action) ✅
- State Queries: 3,427,867 ops/sec (0.000ms per query) ✅
- Regeneration: 1,837,657 ops/sec (0.001ms per regen) ✅
- Force Wait: 1,486,393 ops/sec (0.001ms per check) ✅

### Contract Coverage
- GAME-MOVE-003: Stamina-based action system ✅
- GAME-MOVE-004: Stamina regeneration ✅

## [0.6.0] - 2025-07-22

### Added
- Character model extending Entity with stamina system in `src/models/character.py`
- Movement system with collision detection in `src/game/movement.py`
- Keyboard input handler with WASD support in `src/input/keyboard_handler.py`
- Comprehensive movement test suite (20 new tests, all passing)
- Performance benchmarking for movement operations

### Performance
- Movement Validation: 0.001ms per check (target <10ms) ✅
- Movement Execution: 0.001ms per move (target <10ms) ✅
- Keyboard Handling: 0.000ms per key (target <10ms) ✅
- Full Movement Cycle: 0.001ms per cycle (target <10ms) ✅
- Can handle 722,907 movements/second (12,000x exceeds 60 FPS requirement) ✅

### Contract Coverage
- GAME-MOVE-001: Basic 4-way movement ✅
- GAME-MOVE-002: Collision detection ✅
- GAME-MOVE-005: Diagonal movement ready ✅

## [0.5.0] - 2025-07-21

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

[Unreleased]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.6.0...HEAD
[0.6.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/releases/tag/v0.1.0
