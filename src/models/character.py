"""Simplified character model without unnecessary inheritance.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Modified for Phase 4.1 Monster Implementation
"""

from typing import Dict, Tuple

from src.enums import ActionType, Direction, EntityType, TileType
from src.models.floor import Floor


class Character:
    """Represents a player character with movement and stamina."""

    def __init__(self, name: str, x: int, y: int):
        """Initialize a character.

        Args:
            name: Character's name
            x: Starting X coordinate
            y: Starting Y coordinate
        """
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
