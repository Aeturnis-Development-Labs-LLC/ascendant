"""Character model representing the player character."""

from typing import Tuple

from src.enums import ActionType, Direction, EntityType, TileType
from src.models.entity import Entity
from src.models.floor import Floor


class Character(Entity):
    """Represents a player character with movement and stamina."""

    def __init__(self, name: str, x: int, y: int):
        """Initialize a character.

        Args:
            name: Character's name
            x: Starting X coordinate
            y: Starting Y coordinate
        """
        super().__init__((x, y), EntityType.PLAYER)
        self.name = name
        self._stamina = 100
        self.stamina_max = 100
        # Store mutable position for movement
        self._x = x
        self._y = y

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
        return (self._x, self._y)

    def move_to(self, new_pos: Tuple[int, int]) -> None:
        """Move character to a new position.

        Args:
            new_pos: Tuple of (x, y) coordinates
        """
        self._x, self._y = new_pos
        # Update parent's immutable position
        self._position = new_pos

    def validate_move(self, direction: Direction, floor: Floor) -> bool:
        """Check if a move in the given direction is valid.

        Args:
            direction: Direction to move
            floor: Current floor

        Returns:
            True if move is valid, False otherwise
        """
        # Calculate new position
        new_x = self._x + direction.dx
        new_y = self._y + direction.dy

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

    def update(self) -> None:
        """Update character state. Currently a no-op for basic movement."""
        pass

    def render(self) -> str:
        """Render character as string representation.

        Returns:
            '@' symbol representing the player
        """
        return "@"
