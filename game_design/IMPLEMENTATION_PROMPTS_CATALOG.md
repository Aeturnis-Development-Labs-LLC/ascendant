# Implementation Prompts Catalog
## Systematic Development Guide for Ascendant: The Eternal Spire

This catalog provides specific implementation prompts for each step of development, mapped to UTF contracts following CAFE methodology.

---

## Phase 0: Foundation (Days 1-2)

### 0.1 Project Setup
**UTF Contracts**: GAME-CORE-001
**Implementation Prompt**:
```
Create a new Python project structure for a game called "Ascendant: The Eternal Spire":
1. Create directory structure: /src, /tests, /docs, /assets, /contracts
2. Initialize git repository with .gitignore for Python
3. Create virtual environment with Python 3.11+
4. Create requirements.txt with initial dependencies: pytest, pytest-cov, mypy, black, flake8
5. Create a simple __main__.py that prints "Ascendant: The Eternal Spire" and exits
6. Ensure 'python -m ascendant' runs without errors
```

### 0.2 Core Data Structures
**UTF Contracts**: GAME-CORE-002, GAME-CORE-003, GAME-CORE-004, GAME-CORE-005
**Implementation Prompt**:
```
Implement the core data structures following these specifications:

1. Create enums.py with:
   - TileType enum: FLOOR, WALL, STAIRS_UP, TRAP, CHEST
   - Direction enum: NORTH, SOUTH, EAST, WEST
   - ItemType enum: WEAPON, ARMOR, CONSUMABLE, MISC
   - EntityType enum: PLAYER, MONSTER, NPC

2. Create models/tile.py with Tile class:
   - Immutable position (x, y)
   - tile_type: TileType
   - occupant: Optional[Entity] (can hold one entity)
   - item: Optional[Item] (can hold one item)
   - is_walkable property based on type
   - Validation: prevent multiple occupants

3. Create models/entity.py with Entity base class:
   - position: Tuple[int, int] (immutable after creation)
   - entity_id: str (unique UUID)
   - entity_type: EntityType
   - Abstract methods: update(), render()

4. Create models/item.py with Item base class:
   - item_id: str (unique UUID)
   - name: str
   - item_type: ItemType
   - base_stats: Dict[str, int]
   - Validation: stats must be appropriate for item type

Write comprehensive unit tests for each class ensuring immutability and validation rules.
```

---

## Phase 1: Map Generation & Display (Days 3-5)

### 1.1 Basic Floor Generation
**UTF Contracts**: GAME-MAP-001, GAME-MAP-002
**Implementation Prompt**:
```
Implement a floor generation system:

1. Create models/floor.py with Floor class:
   - 20x20 grid of Tile objects
   - seed: int for reproducible generation
   - generate() method that creates rooms
   
2. Implement basic room generation:
   - Generate 5-10 rectangular rooms
   - Room size: 3x3 to 8x8 tiles
   - Rooms cannot overlap
   - Rooms must be 1 tile away from edges
   - Fill non-room tiles with walls
   
3. Create a simple test that:
   - Generates a floor with seed 12345
   - Verifies room count is between 5-10
   - Ensures no rooms overlap
   - Confirms same seed produces identical layout
```

### 1.2 Room Connection Algorithm
**UTF Contracts**: GAME-MAP-003, GAME-MAP-004
**Implementation Prompt**:
```
Extend the Floor class with room connection and stairs:

1. Add connect_rooms() method:
   - Use L-shaped corridors (horizontal then vertical)
   - Connect each room to at least one other
   - Ensure all rooms are reachable from any other room
   - Corridors are 1 tile wide
   
2. Add place_stairs() method:
   - Select a random room
   - Place stairs in the room center if possible
   - Otherwise, place on any floor tile in the room
   - Ensure stairs are not in doorways
   
3. Add validation method is_fully_connected():
   - Use pathfinding to verify all rooms are connected
   - Return True only if every room is reachable
   
4. Write tests verifying:
   - All generated floors are fully connected
   - Stairs are accessible from every room
   - Corridors don't create isolated sections
```

### 1.3 ASCII Visualization & Map Features
**UTF Contracts**: GAME-MAP-005, GAME-MAP-006, GAME-MAP-007
**Implementation Prompt**:
```
Complete the map generation with visualization and features:

1. Create renderers/ascii_renderer.py:
   - render(floor, player_pos, vision_radius) method
   - Use these ASCII characters:
     '#' = wall, '.' = floor, '^' = stairs up
     '@' = player, 'M' = monster, 'T' = trap
     'C' = chest, '?' = fog of war
   - Apply fog of war outside vision radius
   - Return multi-line string

2. Add trap placement to Floor:
   - place_traps(density: float) method
   - Density 0.0-1.0 (0.1 = 10% of floor tiles)
   - Only place on walkable tiles
   - Not on stairs or spawn points
   - Traps start hidden

3. Add chest generation to Floor:
   - place_chests(count: int) method
   - Place in rooms only
   - Not blocking doorways or stairs
   - Higher floors = better loot table

4. Create comprehensive test suite verifying all placement rules
```

---

## Phase 2: Movement System (Days 6-7)

### 2.1 Basic Movement
**UTF Contracts**: GAME-MOVE-001, GAME-MOVE-002, GAME-MOVE-005
**Implementation Prompt**:
```
Implement character movement system:

1. Create models/character.py extending Entity:
   - stamina: int (max 100)
   - move_to(new_pos) method
   - validate_move(direction, floor) method
   
2. Create game/movement.py with MovementSystem:
   - validate_position(pos, floor) -> bool
   - calculate_new_position(current, direction) -> Tuple
   - execute_move(character, direction, floor) -> bool
   
3. Create input/keyboard_handler.py:
   - Map keys to Direction enum:
     W/↑ = NORTH, S/↓ = SOUTH
     D/→ = EAST, A/← = WEST
   - Queue valid commands
   - Ignore invalid/unmapped keys
   
4. Write movement tests:
   - Cannot move through walls
   - Cannot move off map
   - Position updates correctly
   - Invalid moves are rejected
```

### 2.2 Stamina System
**UTF Contracts**: GAME-MOVE-003, GAME-MOVE-004
**Implementation Prompt**:
```
Implement the stamina system disguised as turns:

1. Extend Character class with stamina management:
   - stamina: int (0-100, starts at 100)
   - stamina_max: int = 100
   - perform_action(action_type, cost) method
   
2. Create game/stamina_system.py:
   - Action costs:
     * Move: 10 stamina
     * Attack: 15 stamina
     * Use item: 10 stamina
     * Cast spell: 20-50 stamina
     * Wait: -20 stamina (regenerates)
   - regenerate(character, turns) method:
     * +5 stamina per turn idle
     * Wait action gives +20 stamina
   - force_wait(character) when stamina < action cost
   
3. Integration tests:
   - Stamina never goes below 0
   - Stamina never exceeds maximum
   - Forced wait when insufficient stamina
   - Regeneration calculates correctly
```

---

## Phase 3: Basic Client (Days 8-10)

### 3.1 PyQt Window Setup
**UTF Contracts**: GAME-UI-001, GAME-UI-004
**Implementation Prompt**:
```
Create the PyQt6 game client structure:

1. Create client/main_window.py:
   - MainWindow class extending QMainWindow
   - Default size: 1280x720, minimum: 1024x600
   - Three-panel layout using QHBoxLayout:
     * Left panel: 20% width
     * Center panel: 60% width  
     * Right panel: 20% width
   - Resizable with locked panel ratios
   
2. Create menu bar with:
   - File menu: New Game, Save, Load, Quit
   - Options menu: Settings, Controls
   - Help menu: About, How to Play
   
3. Add keyboard event handling:
   - Override keyPressEvent
   - Forward game commands to handler
   - Prevent default key behaviors
   
4. Create app.py entry point:
   - Initialize QApplication
   - Create and show MainWindow
   - Handle clean shutdown
```

### 3.2 Map Display Widget
**UTF Contracts**: GAME-UI-002
**Implementation Prompt**:
```
Implement the game map display:

1. Create client/widgets/map_widget.py:
   - MapWidget extending QWidget
   - Tile-based rendering (calculate tile size from widget size)
   - Color mapping:
     * Background: #1a1a1a
     * Walls: #666666
     * Floor: #333333
     * Player: #00ff00
     * Monsters: #ff0000
   
2. Implement paint methods:
   - paintEvent to draw the visible map
   - draw_tile(painter, x, y, tile_type, color)
   - Center view on player position
   - Smooth updates without flicker
   
3. Connect to game state:
   - Accept Floor object and player position
   - Update display when state changes
   - Handle resize events properly
   
4. Add visual feedback:
   - Highlight valid move tiles on hover
   - Flash tiles for combat
   - Smooth scrolling when player moves
```

### 3.3 Information Panels
**UTF Contracts**: GAME-UI-003, GAME-UI-005
**Implementation Prompt**:
```
Create the information panels:

1. Create client/widgets/character_panel.py (Left):
   - Character name and portrait placeholder
   - HP/Stamina bars with labels
   - Stats display (STR, DEX, INT, VIT)
   - Buffs/debuffs list
   - Mini-map (10x10 compressed view)
   - Quick action slots (1-9)
   
2. Create client/widgets/info_panel.py (Right):
   - QTabWidget with tabs:
     * Inventory (grid layout)
     * Combat Log (scrollable text)
     * Statistics (totals and percentages)
   - Floor info at bottom (always visible)
   
3. Create client/widgets/status_bar.py:
   - Display game messages
   - Priority system (combat > info > flavor)
   - Auto-clear after 5 seconds
   - Different colors for message types
   
4. Implement panel synchronization:
   - Update all panels on game state change
   - No lag between action and display
   - Maintain state during tab switches
```

---

## Phase 4: Combat Foundation (Days 11-13)

### 4.1 Monster Implementation
**UTF Contracts**: GAME-COMBAT-001, GAME-COMBAT-006
**Implementation Prompt**:
```
Create the monster system:

1. Create models/monster.py extending Entity:
   - hp: int (current health)
   - hp_max: int (maximum health)
   - attack: int (base damage)
   - defense: int (damage reduction)
   - monster_type: str
   - ai_behavior: AIBehavior enum
   
2. Create game/monster_spawner.py:
   - spawn_monsters(floor, count, level) method
   - Scale stats with floor level
   - Place in rooms (not corridors)
   - Not on stairs or player spawn
   
3. Create models/trap.py:
   - trap_type: TrapType enum (SPIKE, POISON, ALARM)
   - damage: int (based on type and floor)
   - triggered: bool (starts False)
   - trigger(character) method
   
4. Write combat foundation tests:
   - Monsters spawn with correct stats
   - Trap damage scales properly
   - Entities placed correctly on floor
```

### 4.2 Combat System
**UTF Contracts**: GAME-COMBAT-002, GAME-COMBAT-003, GAME-COMBAT-004
**Implementation Prompt**:
```
Implement core combat mechanics:

1. Create game/combat_system.py:
   - calculate_damage(attacker, defender) -> int:
     * Base = attacker.attack - defender.defense
     * Minimum damage = 1
     * Return integer damage value
   
   - calculate_critical(attacker) -> bool:
     * Base crit chance 5%
     * +1% per 10 DEX
     * Critical hits deal 2x damage
   
   - resolve_attack(attacker, defender) -> CombatResult:
     * Calculate hit/miss
     * Calculate damage (with crit)
     * Apply damage
     * Return result object
   
2. Create combat result handling:
   - CombatResult dataclass with:
     * attacker, defender
     * damage_dealt
     * was_critical
     * target_died
   - Generate combat log messages
   
3. Implement death handling:
   - Remove dead entities from floor
   - Drop loot if applicable
   - Award experience to killer
   - Clean up references
   
4. Combat test suite:
   - Damage calculation correctness
   - Critical hit probability
   - Death triggers properly
   - No negative HP values
```

### 4.3 Player Combat Integration
**UTF Contracts**: GAME-COMBAT-005
**Implementation Prompt**:
```
Complete player combat system:

1. Extend Character with combat:
   - attack_target(target) method
   - abilities: Dict[str, Ability] 
   - ability_cooldowns: Dict[str, int]
   
2. Create models/ability.py:
   - name: str
   - cooldown: int (turns)
   - stamina_cost: int
   - effect: Callable
   - can_use() -> bool
   
3. Add combat animations to client:
   - Flash attacker tile (white, 100ms)
   - Flash defender tile (red, 100ms)
   - Float damage numbers up
   - Update HP bars smoothly
   
4. Integration tests:
   - Player can attack adjacent enemies
   - Abilities respect cooldowns
   - Combat log updates properly
   - UI reflects combat results
```

---

## Phase 5: Server Architecture (Days 14-16)

### 5.1 Flask API Setup
**UTF Contracts**: GAME-API-001, GAME-API-004
**Implementation Prompt**:
```
Create the game server API:

1. Create server/app.py with Flask:
   - Configure CORS for client access
   - JSON request/response handling
   - Error handling middleware
   - Request logging
   
2. Implement session management:
   - POST /api/session/create
   - GET /api/session/{id}/status
   - DELETE /api/session/{id}
   - Session timeout after 30 min
   
3. Create auth middleware:
   - Generate session tokens (UUID4)
   - Validate tokens on requests
   - Rate limiting (60 requests/min)
   - Prevent duplicate sessions
   
4. API test suite:
   - Session creation/deletion
   - Token validation
   - CORS headers present
   - Rate limiting works
```

### 5.2 Game State Management
**UTF Contracts**: GAME-API-002, GAME-API-003
**Implementation Prompt**:
```
Implement server-side game logic:

1. Create server/game_state.py:
   - GameState class holding:
     * Current floor
     * Player character
     * Active entities
     * Game tick counter
   - Serialize/deserialize methods
   
2. Create action endpoints:
   - POST /api/game/{session}/action
   - Validate action legality
   - Apply action to game state
   - Return state delta
   
3. Implement state synchronization:
   - Version each state change
   - Send only deltas to client
   - Handle out-of-order updates
   - Conflict resolution strategy
   
4. Add anti-cheat validation:
   - Verify movement is legal
   - Check stamina constraints
   - Validate combat calculations
   - Log suspicious behavior
```

### 5.3 WebSocket Integration
**UTF Contracts**: GAME-API-005
**Implementation Prompt**:
```
Add real-time communication:

1. Integrate Flask-SocketIO:
   - WebSocket connection handling
   - Room-based communication
   - Heartbeat/ping system
   - Graceful disconnection
   
2. Create real-time events:
   - 'connect': Join game room
   - 'action': Process game action
   - 'state_update': Push to client
   - 'disconnect': Clean up session
   
3. Client WebSocket integration:
   - Connect on game start
   - Send actions via socket
   - Update UI on state push
   - Handle reconnection
   
4. Performance tests:
   - 100ms max latency
   - Handle 100 concurrent players
   - Automatic reconnection works
   - No memory leaks over time
```

---

## Phase 6: Character System (Days 17-18)

### 6.1 Character Creation
**UTF Contracts**: GAME-CHAR-001, GAME-CHAR-004
**Implementation Prompt**:
```
Implement character creation system:

1. Create models/races.py:
   - Human: +1 all stats, adaptability at lvl 20
   - Elf: +2 DEX, +2 vision radius
   - Dwarf: +2 VIT, 20% trap damage reduction
   
2. Create models/classes.py:
   - Warrior: +3 STR, +2 VIT
   - Rogue: +3 DEX, +2 STR  
   - Mage: +3 INT, +2 DEX
   
3. Create UI character_creation.py:
   - Race selection screen
   - Class selection screen
   - Name input (3-20 chars)
   - Stat preview display
   - Confirm/back buttons
   
4. Add bracket dungeon checks:
   - get_available_dungeons(level)
   - Dungeons have level ranges
   - Can't enter if over-leveled
   - Track completion status
```

### 6.2 Progression System
**UTF Contracts**: GAME-CHAR-002, GAME-CHAR-003, GAME-CHAR-005
**Implementation Prompt**:
```
Create character progression:

1. Implement experience system:
   - Award XP for monster kills
   - XP scales with monster level
   - Level thresholds: 100 * level^2
   - Trigger level_up() at threshold
   
2. Create stat point allocation:
   - Points per level (see design doc)
   - allocate_stat(stat, points) method
   - Update derived stats (HP, stamina)
   - Validation for available points
   
3. Add ascension mechanics:
   - Trigger every 10 floors
   - Temporary +20% all stats
   - Duration: 5 floors
   - Visual indicator when active
   
4. Progression tests:
   - XP calculation correct
   - Level up at right threshold
   - Stat points allocated properly
   - Ascension activates on schedule
```

---

## Phase 7: AI & Equipment (Days 19-21)

### 7.1 Monster AI
**UTF Contracts**: GAME-AI-001, GAME-AI-002, GAME-AI-003, GAME-AI-004
**Implementation Prompt**:
```
Implement monster AI behaviors:

1. Create ai/patrol_behavior.py:
   - Define patrol routes (back-and-forth)
   - Move along path each turn
   - Pause if blocked
   - Resume when unblocked
   
2. Create ai/guard_behavior.py:
   - Set guard point and radius
   - Attack players in radius
   - Return to point if pulled
   - Never exceed max distance
   
3. Create ai/pathfinding.py:
   - Implement A* algorithm
   - Account for obstacles
   - Return step-by-step path
   - Handle unreachable targets
   
4. Create ai/decision_tree.py:
   - Evaluate: player distance, HP%, blocked paths
   - Priority: attack > chase > patrol
   - Different weights per monster type
   - Return chosen action
```

### 7.2 Item System
**UTF Contracts**: GAME-ITEM-001, GAME-ITEM-003, GAME-ITEM-004, GAME-ITEM-006
**Implementation Prompt**:
```
Create item and inventory system:

1. Create items/item_generator.py:
   - generate_item(level, type) method
   - Rarity tiers affect stats
   - Stats scale with item level
   - Type determines stat distribution
   
2. Create models/equipment.py:
   - Equipment slots: weapon, armor, accessory
   - equip_item(character, item, slot)
   - Swap if slot occupied
   - Update character stats
   
3. Create models/inventory.py:
   - Max capacity: 20 items
   - Stack consumables (max 99)
   - Sort by type/value/name
   - add_item/remove_item methods
   
4. Create models/currency.py:
   - Gold tracking per character
   - add_gold/spend_gold methods
   - Cannot go negative
   - Drop gold on death
```

### 7.3 Durability System
**UTF Contracts**: GAME-ITEM-002, GAME-ITEM-005
**Implementation Prompt**:
```
Implement equipment durability:

1. Extend equipment with durability:
   - durability_current: int
   - durability_max: int (50-200)
   - use_item() reduces by 1
   - is_broken property
   
2. Create repair system:
   - RepairKit consumable item
   - repair_item(item, kit) method
   - Restores to max durability
   - Kit consumed on use
   
3. Broken equipment effects:
   - 50% effectiveness
   - Visual indicator (red tint)
   - Warning in combat log
   - Can still be repaired
   
4. Durability tests:
   - Decreases on use
   - Broken items give 50% stats
   - Repair restores fully
   - Cannot exceed max durability
```

---

## Phase 8: Boss & Persistence (Days 22-24)

### 8.1 Boss Implementation
**UTF Contracts**: GAME-BOSS-001, GAME-BOSS-002, GAME-BOSS-003
**Implementation Prompt**:
```
Create boss monster system:

1. Create models/boss.py:
   - Extends Monster class
   - 10x normal monster HP
   - Special attack patterns
   - Unique abilities per boss
   
2. Implement boss spawning:
   - Check if floor % 10 == 0
   - Replace normal spawns
   - Center of largest room
   - Boss-specific music cue
   
3. Create boss abilities:
   - Gatekeeper: Shield bash (knockback)
   - Twins: Synchronized attacks
   - Shapeshifter: Change resistances
   - Include telegraphed warnings
   
4. Boss rotation system:
   - After floor 50, randomize
   - Pool of 3 bosses per tier
   - No repeats in 30 floors
   - Nightmare versions at 100+
```

### 8.2 Save System
**UTF Contracts**: GAME-SAVE-001, GAME-SAVE-002, GAME-DEATH-001, GAME-DEATH-002
**Implementation Prompt**:
```
Implement save and death systems:

1. Create save/save_manager.py:
   - create_suspend_save(game_state)
   - Serialize to encrypted JSON
   - Include checksum validation
   - Delete after successful load
   
2. Add auto-suspend:
   - Hook application close event
   - Create emergency save
   - Flag as auto-suspend
   - Restore on next launch
   
3. Implement permadeath:
   - delete_character(id) on death
   - No recovery possible
   - Clear from all systems
   - Generate death certificate
   
4. Create soul echo:
   - Select 1 random item
   - Place at death location
   - Link to account
   - Found by next character
```

### 8.3 Leaderboard Integration
**UTF Contracts**: GAME-STATS-001
**Implementation Prompt**:
```
Add statistics and leaderboard:

1. Create stats/statistics_tracker.py:
   - Track all game events
   - Per-run and lifetime stats
   - Categories: combat, exploration, items
   - Export to JSON format
   
2. Create leaderboard system:
   - POST /api/leaderboard/submit
   - GET /api/leaderboard/top/{count}
   - Sort by floor reached
   - Include death details
   
3. Death summary screen:
   - Floor reached
   - Monsters killed
   - Time played
   - Cause of death
   - Submit to leaderboard
```

---

## Phase 9: Polish & Features (Days 25-27)

### 9.1 Achievement System
**UTF Contracts**: GAME-ACHIEVE-001, GAME-ACHIEVE-002
**Implementation Prompt**:
```
Implement achievements and badges:

1. Create achievements/achievement_manager.py:
   - Define achievement conditions
   - Check triggers on events
   - Award once per account
   - Store unlock timestamps
   
2. Create badge effects:
   - Calculate total bonuses
   - Apply at character creation
   - Cap total bonus at +50%
   - Show in character screen
   
3. Achievement examples:
   - "First Blood": Kill first monster
   - "Floor 10": Reach floor 10
   - "Untouchable": Clear floor without damage
   - "Speed Runner": Floor in < 60 seconds
```

### 9.2 Death Markers
**UTF Contracts**: GAME-DEATH-003, GAME-FLOOR-001
**Implementation Prompt**:
```
Add death markers and floor optimization:

1. Create death marker system:
   - Store death locations
   - Include timestamp and cause
   - "X corpses are rotting here"
   - Examine for details
   
2. Implement floor memory:
   - Keep last 5 floors active
   - Older floors "crystallize"
   - Save minimal state
   - Regenerate on return
   
3. Visual polish:
   - Death markers show skull icon
   - Examine shows popup
   - Different messages for causes
   - Fade older corpses
```

### 9.3 Statistics Panel
**UTF Contracts**: Part of GAME-STATS-001
**Implementation Prompt**:
```
Complete the statistics display:

1. Add to right panel tabs:
   - Total kills by type
   - Damage dealt/taken
   - Items found/used
   - Floors cleared
   - Critical hit rate
   - Deaths by type
   
2. Create graphs/charts:
   - Damage per floor
   - Kill rate over time
   - Performance trends
   - Use matplotlib or PyQtGraph
   
3. Export functionality:
   - Save stats to CSV
   - Generate run report
   - Share to clipboard
   - Post to social media
```

---

## Phase 10: Testing & Launch (Days 28-30)

### 10.1 Bot Framework
**UTF Contracts**: GAME-BOT-001
**Implementation Prompt**:
```
Create automated testing bots:

1. Create bots/basic_bot.py:
   - Random valid moves
   - Attack when adjacent
   - Pick up items
   - Use stairs when found
   
2. Create bots/smart_bot.py:
   - A* pathfinding to stairs
   - Combat priorities
   - Item evaluation
   - Retreat when low HP
   
3. Bot test harness:
   - Run 100 bot games
   - Track statistics
   - Find crashes/hangs
   - Performance metrics
```

### 10.2 Performance Testing
**UTF Contracts**: GAME-PERF-001, GAME-PERF-002
**Implementation Prompt**:
```
Optimize and test performance:

1. Performance benchmarks:
   - Floor generation < 100ms
   - Frame render < 16ms
   - Memory stable over time
   - No leaks after 1000 floors
   
2. Optimization targets:
   - Profile hot paths
   - Cache floor renders
   - Optimize pathfinding
   - Reduce memory copies
   
3. Load testing:
   - 100 concurrent games
   - 1000 floors deep
   - 24-hour stability test
   - Memory growth tracking
```

### 10.3 Distribution
**UTF Contracts**: GAME-RELEASE-001
**Implementation Prompt**:
```
Package for distribution:

1. Create installer:
   - PyInstaller for executable
   - Include all assets
   - Bundle Python runtime
   - Create shortcuts
   
2. Documentation:
   - Player guide
   - Controls reference
   - Strategy tips
   - Troubleshooting
   
3. Release checklist:
   - Version numbering
   - Changelog updated
   - All tests passing
   - Performance validated
   - Installer tested on clean system
```

---

## Testing Strategy for Each Phase

After implementing each phase, run these verification steps:

1. **Unit Tests**: Each UTF contract should have corresponding tests
2. **Integration Tests**: Components work together properly
3. **Performance Tests**: Meet specified benchmarks
4. **User Acceptance**: Playable at each phase milestone
5. **Contract Validation**: All UTF contracts satisfied

## CAFE Methodology Compliance

Each prompt follows CAFE principles:
- **Contract-First**: UTF contracts defined before implementation
- **AI-Assisted**: Prompts designed for AI implementation
- **Facilitated**: Human oversight at each phase
- **Engineering**: Production-quality code standards

---

This catalog provides a complete roadmap from empty directory to finished game, with each step carefully mapped to its UTF contracts and designed for systematic implementation.