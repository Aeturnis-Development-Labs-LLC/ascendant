"""Centralized game state management with UI update methods.

This module provides a single source of truth for game state and
standardized methods for updating UI components, preventing naming
inconsistencies and coupling issues.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from client.main_window import MainWindow
    from src.game.combat_log import CombatLog
    from src.models.character import Character
    from src.models.floor import Floor
    from src.models.monster import Monster


@dataclass
class GameState:
    """Centralized game state container."""

    character: Optional["Character"] = None
    current_floor: Optional["Floor"] = None
    monsters: List["Monster"] = field(default_factory=list)
    combat_log: Optional["CombatLog"] = None

    # UI update flags
    ui_needs_update: Dict[str, bool] = field(
        default_factory=lambda: {
            "character": False,
            "map": False,
            "inventory": False,
            "combat_log": False,
            "floor_info": False,
        }
    )

    def mark_dirty(self, component: str) -> None:
        """Mark a UI component as needing update."""
        if component in self.ui_needs_update:
            self.ui_needs_update[component] = True

    def mark_all_dirty(self) -> None:
        """Mark all UI components as needing update."""
        for key in self.ui_needs_update:
            self.ui_needs_update[key] = True


class GameStateManager:
    """Manages game state and provides UI update interface."""

    def __init__(self):
        """Initialize the game state manager."""
        self.state = GameState()
        self.main_window: Optional["MainWindow"] = None

    def attach_window(self, window: "MainWindow") -> None:
        """Attach the main window for UI updates."""
        self.main_window = window

    def new_game(self, character_name: str = "Hero") -> None:
        """Initialize a new game."""
        from src.game.combat_log import CombatLog
        from src.game.default_abilities import initialize_character_abilities
        from src.models.character import Character
        from src.models.floor import Floor

        # Create new game state
        self.state.character = Character(character_name, 10, 10)
        self.state.character.hp = 100
        self.state.character.stamina = 100
        initialize_character_abilities(self.state.character)

        self.state.current_floor = Floor(width=50, height=50, level=1)
        self.state.current_floor.generate()

        self.state.combat_log = CombatLog()
        # Set combat log on character using setattr for dynamic attribute
        setattr(self.state.character, "_combat_log", self.state.combat_log)

        self.state.monsters = []

        # Mark everything for update
        self.state.mark_all_dirty()
        self.update_ui()

    def update_ui(self) -> None:
        """Update all dirty UI components."""
        if not self.main_window:
            return

        if self.state.ui_needs_update["character"]:
            self._update_character_panel()
            self.state.ui_needs_update["character"] = False

        if self.state.ui_needs_update["map"]:
            self._update_map_widget()
            self.state.ui_needs_update["map"] = False

        if self.state.ui_needs_update["combat_log"]:
            self._update_combat_log()
            self.state.ui_needs_update["combat_log"] = False

        if self.state.ui_needs_update["floor_info"]:
            self._update_floor_info()
            self.state.ui_needs_update["floor_info"] = False

    def _update_character_panel(self) -> None:
        """Update the character panel with current state."""
        if not self.main_window or not self.state.character:
            return
        panel = getattr(self.main_window, "character_panel", None)
        if not panel:
            return

        char = self.state.character

        # Update basic info
        panel.name_label.setText(f"Name: {char.name}")

        # Update HP
        panel.hp_bar.setMaximum(char.hp_max)
        panel.hp_bar.setValue(char.hp)
        panel.hp_label.setText(f"HP: {char.hp}/{char.hp_max}")

        # Update Stamina
        panel.stamina_bar.setMaximum(char.stamina_max)
        panel.stamina_bar.setValue(char.stamina)
        panel.stamina_label.setText(f"Stamina: {char.stamina}/{char.stamina_max}")

        # Update stats (mapping game stats to UI stats)
        panel.stats_labels["STR"].setText(f"STR: {char.attack}")
        panel.stats_labels["DEX"].setText(f"DEX: {char.defense}")
        panel.stats_labels["INT"].setText(f"INT: {char.level}")
        panel.stats_labels["VIT"].setText(f"VIT: {char.hp_max}")

        # Update minimap
        if self.state.current_floor:
            panel.minimap.floor = self.state.current_floor
            panel.minimap.player_pos = (char.x, char.y)
            panel.minimap.update()

    def _update_map_widget(self) -> None:
        """Update the map widget with current state."""
        if not self.main_window or not self.state.character or not self.state.current_floor:
            return
        widget = getattr(self.main_window, "map_widget", None)
        if not widget:
            return

        widget.floor = self.state.current_floor
        widget.player_pos = (self.state.character.x, self.state.character.y)
        widget.monsters = self.state.monsters
        widget.update()

    def _update_combat_log(self) -> None:
        """Update the combat log display."""
        if not self.main_window or not self.state.combat_log:
            return
        panel = getattr(self.main_window, "info_panel", None)
        if not panel:
            return

        # Get recent messages and add them
        messages = self.state.combat_log.get_recent_messages(10)
        for msg in messages:
            panel.add_combat_message(msg.text)

    def _update_floor_info(self) -> None:
        """Update the floor info display."""
        if not self.main_window or not self.state.current_floor:
            return
        panel = getattr(self.main_window, "info_panel", None)
        if not panel:
            return

        floor = self.state.current_floor
        panel.floor_info_label.setText(f"Floor {floor.level} - The Infinite Tower")

    def move_character(self, dx: int, dy: int) -> bool:
        """Move the character and update UI.

        Args:
            dx: X direction (-1, 0, 1)
            dy: Y direction (-1, 0, 1)

        Returns:
            True if move was successful
        """
        if not self.state.character or not self.state.current_floor:
            return False

        char = self.state.character
        floor = self.state.current_floor

        new_x = char.x + dx
        new_y = char.y + dy

        # Validate move
        if 0 <= new_x < floor.width and 0 <= new_y < floor.height:
            char.x = new_x
            char.y = new_y

            # Update UI
            self.state.mark_dirty("character")
            self.state.mark_dirty("map")
            self.state.mark_dirty("floor_info")
            self.update_ui()

            return True

        return False

    def use_ability(self, ability_index: int) -> bool:
        """Use an ability on the nearest enemy.

        Args:
            ability_index: 0-based index of ability

        Returns:
            True if ability was used successfully
        """
        if not self.state.character:
            return False

        char = self.state.character
        ability_names = list(char.abilities.keys())

        if ability_index >= len(ability_names):
            return False

        ability_name = ability_names[ability_index]

        # Find adjacent monster
        for monster in self.state.monsters:
            if not monster.is_alive():
                continue

            dx = abs(char.x - monster.x)
            dy = abs(char.y - monster.y)

            if dx <= 1 and dy <= 1:
                # Try to use ability
                if char.attack_target(monster, ability_name):
                    self.state.mark_dirty("character")
                    self.state.mark_dirty("combat_log")
                    self.update_ui()
                    return True
                break

        return False


# Global instance
game_state_manager = GameStateManager()
