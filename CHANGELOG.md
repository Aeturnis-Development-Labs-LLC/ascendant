# Changelog

All notable changes to Ascendant: The Eternal Spire will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.15.0] - 2025-07-23

### Added
- Monster Implementation (Phase 4.1)
  - Entity base class for all game entities
    * Abstract methods for render() and update()
    * Position property and entity type tracking
  - Monster class with full combat stats
    * HP, attack, defense attributes
    * AIBehavior enum (PASSIVE, AGGRESSIVE, DEFENSIVE, RANGED)
    * take_damage() and is_alive() methods
    * Monster type identification system
  - Trap system with three types
    * SPIKE: Direct damage
    * POISON: Damage + poison status effect
    * ALARM: Alerts nearby monsters
    * Damage scaling based on floor level
    * One-time trigger mechanism
  - MonsterSpawner for dynamic monster generation
    * 6 monster types (rat, goblin, skeleton, orc, troll, demon)
    * Level-based monster availability
    * Stat scaling with floor level
    * Room-based spawning only
    * Exclusion zones (stairs, player position)
- Character class enhancements
  - take_damage() method for combat integration
  - apply_status() method for status effects
  - HP tracking (hp, hp_max attributes)

### Changed
- Character class now includes combat-related methods
- Test infrastructure updated to use Tile objects properly

### Technical Details
- 95.74% test coverage (31 tests)
- Full type safety with mypy strict mode
- Black formatted with 79-character line limit
- AI attribution headers on all generated files
- UTF contracts GAME-COMBAT-001 and GAME-COMBAT-006 implemented

## [0.14.0] - 2025-07-23

### Added
- Information Panels Implementation (Phase 3.3)
  - CharacterPanel widget with comprehensive character display
    * HP and stamina bars with color-coded health status
    * Character stats display (STR, DEX, INT, VIT)
    * Buffs and debuffs lists
    * Mini-map widget (10x10 grid centered on player)
    * Quick action slots (1-9) with signal emission
  - InfoPanel widget with tabbed interface
    * Inventory tab with 5x8 grid (40 slots)
    * Combat log tab with auto-scrolling and 500-line limit
    * Statistics tab with categorized game stats
    * Floor info display (always visible)
  - StatusBar widget with priority system
    * Three priority levels: FLAVOR < INFO < COMBAT
    * Auto-clear functionality (5-second default)
    * Message history tracking (50 messages)
    * Custom color support per message type
- Panel synchronization in MainWindow
  - update_character() method for character data
  - show_status_message() for status bar updates
  - add_combat_message() for combat log
  - update_floor_info() for floor information
  - Signal connections for action/inventory clicks
- Comprehensive test suite (47 new tests)
- Demo script (demo_panels.py) showing all features

### Changed
- MainWindow now integrates all three information panels
- Status bar now uses custom widget instead of default QStatusBar

### Technical Details
- 100% test coverage for all new widgets
- All linting issues resolved with black formatting
- KISS principles maintained throughout implementation
- UTF contracts GAME-UI-003 and GAME-UI-005 fully implemented

## [0.13.1] - 2025-07-23

### Added
- Zoom functionality for map widget
  - Mouse wheel zoom support (0.5x to 3.0x range)
  - Keyboard shortcuts (Ctrl++, Ctrl+-, Ctrl+0)
  - Dynamic tile size recalculation
- Minimap overlay feature
  - Toggle with 'M' key
  - Shows entire floor overview
  - Yellow viewport indicator
  - Player position marker
  - Semi-transparent rendering
- View menu in main window with zoom/minimap controls
- Integration with movement and stamina systems

### Fixed
- Map widget initialization order issue
- Import path problems when running from different locations
- Minimap grid lines removed for cleaner appearance

### Improved
- Performance optimization (<16ms paint time)
- Test coverage increased to 28 tests for map widget

## [0.13.0] - 2025-01-23

### Added
- Map Display Widget Implementation (Phase 3.2)
  - MapWidget class with tile-based rendering
  - Dynamic tile size calculation based on widget size
  - Player position centering with viewport management
  - Color mapping for different tile types:
    * Background: #1a1a1a
    * Walls: #666666
    * Floor: #333333
    * Player: #00ff00
    * Monsters: #ff0000
  - Visual feedback features:
    * Hover highlighting
    * Combat tile flashing
    * Valid move indicators
  - Mouse tracking for interactive features
  - UTF contract GAME-UI-002 implementation
  - Comprehensive test suite (18 tests) for map rendering

### Changed
- MainWindow now integrates MapWidget in center panel
- Added client/widgets directory for custom PyQt widgets

### Technical Details
- Tile-based rendering with automatic size calculation
- Smooth viewport scrolling when player moves
- Performance optimized for 60 FPS rendering
- Memory-stable update system
- Graceful fallback when PyQt6 not available

## [0.12.0] - 2025-01-22

### Added
- PyQt6 Client Implementation (Phase 3.1)
  - MainWindow class with three-panel layout (20%-60%-20% ratios)
  - Menu bar with File, Options, and Help menus
  - Keyboard event handling with customizable handler
  - Application entry point with GUI/console mode detection
  - UTF contracts GAME-UI-001 and GAME-UI-004
  - Comprehensive test suite (18 tests) with PyQt6 skip handling

### Changed
- Main entry point now defaults to GUI mode
- Console mode requires --console flag
- Added PyQt6 to requirements.txt

### Technical Details
- Default window size: 1280x720 pixels
- Minimum window size: 1024x600 pixels
- Panel ratios maintained during window resize
- All menu items have keyboard shortcuts
- Tests skip gracefully when PyQt6 not installed

## [0.11.0] - 2025-01-22

### Changed
- **Major Refactoring**: KISS (Keep It Simple, Stupid) principle applied throughout codebase
  - Consolidated color system from 921 lines (4 files) to 378 lines (2 files)
  - Removed Entity abstract base class inheritance, simplified Character class (189 → 97 lines)
  - Converted all static classes to simple functions:
    - MovementSystem → movement functions (72 → 65 lines)
    - StaminaSystem → stamina functions (147 → 65 lines)
    - WorldMapRenderer → render function (85 → 84 lines)
  - Archived premature features (soul system) for future implementation
  - Total codebase reduction: 1,044 lines (30%)

### Technical Improvements
- Eliminated unnecessary abstraction layers
- Simplified imports and function calls
- Improved code readability and maintainability
- All 255 tests passing with >98% coverage
- Zero performance regression

### Developer Experience
- Direct function calls instead of static methods
- Clearer code structure with less cognitive overhead
- Easier testing and mocking
- Better alignment with Python idioms

## [0.10.0] - 2025-01-22

### Added
- Color System Implementation (Phase 2.6)
  - ColorScheme class for managing RGB/ANSI color mappings
  - Color effects (fog of war, status effects, damage flash animations)
  - Accessibility features (colorblind modes, high contrast, symbol-only mode)
  - Extended ASCII renderer with color support
  - JSON-loadable custom color schemes
  - 70 new tests following TDD methodology
  
### Changed
- ASCII renderer now supports both colored and non-colored output
- Backward compatibility maintained with static render method

### Contract Coverage
- GAME-COLOR-001: Color scheme management ✅
- GAME-COLOR-002: Visual effects system ✅
- GAME-COLOR-003: Accessibility features ✅

## [0.9.0] - 2025-07-22

### Added
- Safe Haven & Special Locations (Phase 2.5)
  - Safe Haven interior with 5x5 grid and named zones
  - Lost Soul system with achievement badges and bonus caps
  - Dungeon properties with level brackets and floor counts
  - Escape rope mechanics with location-based restrictions
  - Boss room locks preventing escape
  - Deterministic dungeon generation using seeds
- 51 new tests for special location features

### Contract Coverage
- GAME-WORLD-002: Safe Haven implementation ✅
- GAME-WORLD-018: Lost Soul system ✅
- GAME-WORLD-019: Dungeon properties ✅

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

[Unreleased]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.15.0...HEAD
[0.15.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.14.0...v0.15.0
[0.14.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.13.1...v0.14.0
[0.13.1]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.13.0...v0.13.1
[0.13.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Aeturnis-Development-Labs-LLC/ascendant/releases/tag/v0.1.0
