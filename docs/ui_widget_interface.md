# UI Widget Interface Documentation

This document defines the standard interface for all UI widgets in ASCENT to ensure consistency and prevent naming issues.

## CharacterPanel

**Purpose**: Display character information, stats, and status

**Required Attributes**:
- `name_label`: QLabel - Character name display
- `hp_bar`: QProgressBar - Health points bar
- `hp_label`: QLabel - HP text (e.g., "HP: 80/100")
- `stamina_bar`: QProgressBar - Stamina bar
- `stamina_label`: QLabel - Stamina text
- `stats_labels`: Dict[str, QLabel] - Stats display with keys: "STR", "DEX", "INT", "VIT"
- `buffs_list`: QListWidget - Active buffs
- `debuffs_list`: QListWidget - Active debuffs
- `minimap`: MiniMapWidget - Small map view
- `action_slots`: Dict[str, QPushButton] - Quick action buttons "1"-"9"

**Signals**:
- `action_slot_clicked(int)`: Emitted when action slot clicked

## MapWidget

**Purpose**: Display the game world map

**Required Attributes**:
- `floor`: Optional[Floor] - Current floor data
- `player_pos`: Optional[Tuple[int, int]] - Player position
- `monsters`: List[Monster] - Visible monsters (optional)
- `tile_size`: int - Size of each tile
- `zoom_level`: float - Current zoom

**Required Methods**:
- `update()`: Refresh the display
- `zoom_in()`: Increase zoom
- `zoom_out()`: Decrease zoom

## InfoPanel

**Purpose**: Display game information, inventory, and logs

**Required Attributes**:
- `tab_widget`: QTabWidget - Container for tabs
- `inventory_grid`: InventoryGrid - Inventory display
- `combat_log`: QTextEdit - Combat messages
- `statistics_display`: StatisticsDisplay - Game stats
- `floor_info_label`: QLabel - Current floor information

**Required Methods**:
- `add_combat_message(str)`: Add message to combat log
- `add_inventory_item(item, slot)`: Add item to inventory
- `update_statistic(name, value, is_percentage)`: Update a stat

**Signals**:
- `inventory_slot_clicked(int)`: Emitted when inventory slot clicked

## StatusBar

**Purpose**: Display temporary game messages

**Required Attributes**:
- None (extends QLabel)

**Required Methods**:
- `show_message(text: str, priority: MessagePriority, duration: int = 3000)`

**Enums**:
- `MessagePriority`: FLAVOR=1, INFO=2, COMBAT=3

## Design Patterns

### 1. Consistent Naming
- Use descriptive names that match the data they display
- Suffix with widget type: `_label`, `_bar`, `_list`, `_button`
- Group related widgets: `hp_bar` with `hp_label`

### 2. Data Flow
```
GameState -> GameStateManager -> Widget Update Methods -> UI Widgets
```

### 3. Update Pattern
```python
# Don't do this - direct coupling
window.character_panel.some_random_label.setText(character.hp)

# Do this - use manager
game_state_manager.state.character = character
game_state_manager.state.mark_dirty("character")
game_state_manager.update_ui()
```

### 4. Widget Discovery
```python
# Use introspection to discover widget attributes
def print_widget_interface(widget):
    """Print all public attributes of a widget."""
    for attr in dir(widget):
        if not attr.startswith('_'):
            obj = getattr(widget, attr)
            print(f"{attr}: {type(obj).__name__}")
```

## Testing Widget Interfaces

```python
def test_character_panel_interface():
    """Test that CharacterPanel has required interface."""
    panel = CharacterPanel()
    
    # Required attributes
    assert hasattr(panel, 'name_label')
    assert hasattr(panel, 'hp_bar')
    assert hasattr(panel, 'hp_label')
    assert hasattr(panel, 'stamina_bar')
    assert hasattr(panel, 'stamina_label')
    assert hasattr(panel, 'stats_labels')
    assert hasattr(panel, 'minimap')
    
    # Stats labels
    assert 'STR' in panel.stats_labels
    assert 'DEX' in panel.stats_labels
    assert 'INT' in panel.stats_labels
    assert 'VIT' in panel.stats_labels
```

## Migration Guide

When updating widgets:

1. Check this document for the expected interface
2. Update the widget to match the interface
3. Update the GameStateManager's update methods
4. Add tests to verify the interface

This ensures consistency across the codebase and prevents "AttributeError: 'Widget' has no attribute 'x'" errors.