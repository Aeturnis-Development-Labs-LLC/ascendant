"""Core enumerations for Ascendant: The Eternal Spire."""

from enum import Enum, auto


class TileType(Enum):
    """Types of tiles that can exist in the game world."""

    FLOOR = auto()
    WALL = auto()
    STAIRS_UP = auto()
    TRAP = auto()
    CHEST = auto()

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.name


class Direction(Enum):
    """Cardinal directions for movement and orientation."""

    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)

    def __init__(self, dx: int, dy: int):
        """Initialize with direction vector."""
        self.dx = dx
        self.dy = dy

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.name


class ItemType(Enum):
    """Types of items that can exist in the game."""

    WEAPON = auto()
    ARMOR = auto()
    CONSUMABLE = auto()
    MISC = auto()

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.name


class EntityType(Enum):
    """Types of entities that can exist in the game."""

    PLAYER = auto()
    MONSTER = auto()
    NPC = auto()

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.name
