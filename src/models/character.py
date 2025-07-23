"""Simplified character model without unnecessary inheritance.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Modified for Phase 4.1 Monster Implementation
"""

import uuid
from typing import TYPE_CHECKING, Dict, Optional, Tuple

from src.enums import ActionType, Direction, EntityType, TileType
from src.models.floor import Floor

if TYPE_CHECKING:
    from src.game.combat_system import CombatResult
    from src.models.ability import Ability
    from src.models.monster import Monster


class Character:
    """Represents a player character with movement and stamina."""

    def __init__(self, name: str, x: int, y: int):
        """Initialize a character.

        Args:
            name: Character's name
            x: Starting X coordinate
            y: Starting Y coordinate
        """
        self.uuid = str(uuid.uuid4())  # Add UUID for entity identification
        self.name = name
        self.x = x
        self.y = y
        self.entity_type = EntityType.PLAYER
        self._stamina = 100
        self.stamina_max = 100
        self.hp = 100
        self.hp_max = 100
        self.status_effects: Dict[str, int] = {}
        # Combat stats
        self.attack = 10
        self.defense = 5
        self.crit_chance = 0.1  # 10% base crit chance
        # Progression
        self.level = 1
        self.experience = 0
        self.luck = 0
        # Abilities
        self.abilities: Dict[str, "Ability"] = {}
        self.ability_cooldowns: Dict[str, int] = {}

    @property
    def stamina(self) -> int:
        """Get current stamina."""
        return max(0, min(self._stamina, self.stamina_max))

    @stamina.setter
    def stamina(self, value: int) -> None:
        """Set stamina, clamped between 0 and stamina_max."""
        self._stamina = max(0, min(value, self.stamina_max))

    @property
    def position(self) -> Tuple[int, int]:
        """Get current position as tuple."""
        return (self.x, self.y)

    def move_to(self, new_pos: Tuple[int, int]) -> None:
        """Move character to a new position.

        Args:
            new_pos: Tuple of (x, y) coordinates
        """
        self.x, self.y = new_pos

    def validate_move(self, direction: Direction, floor: Floor) -> bool:
        """Check if a move in the given direction is valid.

        Args:
            direction: Direction to move
            floor: Current floor

        Returns:
            True if move is valid, False otherwise
        """
        # Calculate new position
        new_x = self.x + direction.dx
        new_y = self.y + direction.dy

        # Check bounds
        if not floor.is_valid_position(new_x, new_y):
            return False

        # Check tile is walkable
        tile = floor.get_tile(new_x, new_y)
        if tile is None:
            return False

        # Can walk on floor, stairs, but not walls
        walkable_tiles = {TileType.FLOOR, TileType.STAIRS_UP, TileType.STAIRS_DOWN}
        return tile.tile_type in walkable_tiles

    def perform_action(self, action_type: ActionType, cost: int) -> bool:
        """Perform an action if sufficient stamina is available.

        Args:
            action_type: Type of action to perform
            cost: Stamina cost of the action

        Returns:
            True if action was performed, False if insufficient stamina
        """
        if self.stamina >= cost:
            self.stamina -= cost
            return True
        return False

    def __str__(self) -> str:
        """Return string representation of the character."""
        return f"Character({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Return detailed representation of the character."""
        return f"Character(name='{self.name}', position={self.position})"

    def take_damage(self, damage: int) -> None:
        """Apply damage to the character.

        Args:
            damage: Amount of damage to apply
        """
        self.hp = max(0, self.hp - damage)

    def apply_status(self, status: str, duration: int) -> None:
        """Apply a status effect to the character.

        Args:
            status: Name of the status effect
            duration: Duration in turns
        """
        self.status_effects[status] = duration

    def is_alive(self) -> bool:
        """Check if character is still alive.

        Returns:
            True if HP > 0
        """
        return self.hp > 0

    def attack_target(self, target: "Monster", ability_name: Optional[str] = None) -> bool:
        """Attack a target, optionally using an ability.

        Args:
            target: The target to attack
            ability_name: Name of ability to use (None for basic attack)

        Returns:
            True if attack succeeded, False otherwise
        """
        # Check if target is adjacent
        if not self._is_adjacent(target):
            return False

        # Check if target is alive
        if not target.is_alive():
            return False

        # Handle ability usage
        if ability_name:
            # Check if ability exists
            if ability_name not in self.abilities:
                return False

            ability = self.abilities[ability_name]
            current_cooldown = self.ability_cooldowns.get(ability_name, 0)

            # Check if ability can be used
            if not ability.can_use(current_cooldown, self.stamina):
                return False

            # Use the ability
            return self.use_ability(ability_name, target) is not None
        else:
            # Basic attack
            from src.game.combat_system import CombatSystem

            combat_system = CombatSystem()
            # Set combat log if available
            if hasattr(self, "_combat_log") and self._combat_log:
                combat_system.combat_log = self._combat_log
            result = combat_system.attack(self, target)
            return result is not None

    def use_ability(self, ability_name: str, target: "Monster") -> Optional["CombatResult"]:
        """Use an ability on a target.

        Args:
            ability_name: Name of the ability to use
            target: Target of the ability

        Returns:
            CombatResult if successful, None otherwise
        """
        if ability_name not in self.abilities:
            return None

        ability = self.abilities[ability_name]

        # Deduct stamina
        self.stamina -= ability.stamina_cost

        # Set cooldown
        self.ability_cooldowns[ability_name] = ability.cooldown_duration

        # Apply damage with multiplier
        from src.game.combat_system import CombatSystem

        combat_system = CombatSystem()
        # Set combat log if available
        if hasattr(self, "_combat_log") and self._combat_log:
            combat_system.combat_log = self._combat_log

        # Temporarily boost attack for this ability
        original_attack = self.attack
        self.attack = int(self.attack * ability.damage_multiplier)

        result = combat_system.attack(self, target)

        # Restore original attack
        self.attack = original_attack

        # Apply any special effects
        if ability.effect and result:
            ability.effect(self, target, result)

        return result

    def tick_cooldowns(self) -> None:
        """Decrement all ability cooldowns by 1 turn."""
        for ability_name in self.ability_cooldowns:
            if self.ability_cooldowns[ability_name] > 0:
                self.ability_cooldowns[ability_name] -= 1

    def _is_adjacent(self, target: "Monster") -> bool:
        """Check if target is adjacent to character.

        Args:
            target: Target to check

        Returns:
            True if target is adjacent (including diagonals)
        """
        dx = abs(self.x - target.x)
        dy = abs(self.y - target.y)
        return dx <= 1 and dy <= 1 and (dx + dy) > 0
