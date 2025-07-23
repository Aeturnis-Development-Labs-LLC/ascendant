"""Core enumerations for Ascendant: The Eternal Spire."""

from enum import Enum, auto


class TileType(Enum):
    """Types of tiles that can exist in the game world."""

    FLOOR = auto()
    WALL = auto()
    STAIRS_UP = auto()
    STAIRS_DOWN = auto()
    TRAP = auto()
    CHEST = auto()
    DOOR = auto()  # Added for room connections

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.name


class Direction(Enum):
    """Cardinal and diagonal directions for movement and orientation."""

    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)
    NORTHEAST = (1, -1)
    NORTHWEST = (-1, -1)
    SOUTHEAST = (1, 1)
    SOUTHWEST = (-1, 1)

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
    KEY = auto()  # For locked doors and chests

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


class ActionType(Enum):
    """Types of actions that consume stamina."""

    MOVE = auto()
    ATTACK = auto()
    USE_ITEM = auto()
    CAST_SPELL = auto()
    WAIT = auto()

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.name


class TerrainType(Enum):
    """Types of terrain that can exist on the world map."""

    PLAINS = auto()
    FOREST = auto()
    MOUNTAINS = auto()
    WATER = auto()
    ROADS = auto()
    SHADOWLANDS = auto()

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.name


class LocationType(Enum):
    """Types of locations on the world map."""

    SAFE_HAVEN = auto()
    DUNGEON_ENTRANCE = auto()
    TOWER_ENTRANCE = auto()
    VILLAGE = auto()  # For future use

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.name
