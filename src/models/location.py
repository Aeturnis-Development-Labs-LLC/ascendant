"""Location system for world map points of interest."""

from abc import ABC, abstractmethod
from typing import Set, Tuple

from src.enums import LocationType, TileType
from src.models.character import Character
from src.models.floor import Floor


class Location(ABC):
    """Base class for all world map locations."""

    def __init__(
        self,
        position: Tuple[int, int],
        name: str,
        location_type: LocationType,
        description: str = "",
    ):
        """Initialize a location.

        Args:
            position: (x, y) position on world map
            name: Display name
            location_type: Type of location
            description: Flavor text
        """
        self.position = position
        self.name = name
        self.location_type = location_type
        self.description = description
        self.discovered = False

    @abstractmethod
    def can_enter(self, character: Character) -> Tuple[bool, str]:
        """Check if character can enter this location.

        Args:
            character: Character trying to enter

        Returns:
            Tuple of (can_enter, reason_if_not)
        """
        pass

    def discover(self) -> None:
        """Mark this location as discovered."""
        self.discovered = True

    def get_display_symbol(self) -> str:
        """Get ASCII symbol for map display."""
        if not self.discovered:
            return "?"

        if self.location_type == LocationType.SAFE_HAVEN:
            return "[H]"
        elif self.location_type == LocationType.TOWER_ENTRANCE:
            return "[T]"
        elif self.location_type == LocationType.DUNGEON_ENTRANCE:
            return "[D]"
        elif self.location_type == LocationType.VILLAGE:
            return "[v]"
        else:
            return "[?]"


class SafeHaven(Location):
    """The central hub town where players start and respawn."""

    def __init__(self):
        """Initialize Safe Haven at the center of the map."""
        super().__init__(
            position=(37, 37),
            name="Safe Haven",
            location_type=LocationType.SAFE_HAVEN,
            description="A peaceful town protected by ancient magic. No combat is allowed here.",
        )
        self.discovered = True  # Always discovered
        self.interior_size = 5  # 5x5 interior grid
        self.no_combat = True
        self.spawn_point = (2, 2)  # Center of interior

    def can_enter(self, character: Character) -> Tuple[bool, str]:
        """Safe Haven can always be entered."""
        return (True, "")

    def create_interior(self) -> Floor:
        """Create the interior layout of Safe Haven.

        Returns:
            Floor object representing the town interior
        """
        # Floor uses fixed 20x20 size, we'll use a subset
        interior = Floor(seed=42)  # Fixed seed for consistency

        # Generate the floor to populate tiles
        interior.generate()

        # We'll treat the center 5x5 area as the Safe Haven interior
        # Clear center area to be all floor tiles
        center_start = (Floor.FLOOR_WIDTH - self.interior_size) // 2
        center_end = center_start + self.interior_size

        for y in range(center_start, center_end):
            for x in range(center_start, center_end):
                interior.tiles[(x, y)].tile_type = TileType.FLOOR

        return interior


class DungeonEntrance(Location):
    """Entrance to a level-bracketed dungeon."""

    def __init__(
        self,
        position: Tuple[int, int],
        name: str,
        min_level: int,
        max_level: int,
        floor_count: int,
    ):
        """Initialize a dungeon entrance.

        Args:
            position: World map position
            name: Dungeon name
            min_level: Minimum level for bracket
            max_level: Maximum level for bracket
            floor_count: Number of floors in dungeon
        """
        description = f"A dungeon for adventurers level {min_level}-{max_level}."
        super().__init__(position, name, LocationType.DUNGEON_ENTRANCE, description)
        self.min_level = min_level
        self.max_level = max_level
        self.floor_count = floor_count
        self.completed_by: Set[str] = set()  # Track character IDs who completed it

    def can_enter(self, character: Character) -> Tuple[bool, str]:
        """Check level requirements for entry.

        Args:
            character: Character trying to enter

        Returns:
            Tuple of (can_enter, reason_if_not)
        """
        char_level = getattr(character, "level", 1)  # Default to 1 if no level yet

        if char_level > self.max_level:
            return (
                False,
                f"You are too high level ({char_level}) for this dungeon (max {self.max_level})."
            )

        if char_level < self.min_level:
            return (False, f"You must be at least level {self.min_level} to enter.")

        return (True, "")

    def get_display_symbol(self) -> str:
        """Get bracket-specific symbol."""
        if not self.discovered:
            return "?"

        # Show bracket number based on level range
        # 1-9 = bracket 1, 10-19 = bracket 2, etc.
        bracket = (self.max_level // 10) + 1
        if self.max_level == 9:  # Special case for 1-9
            bracket = 1

        if bracket <= 9:
            return f"[{bracket}]"
        return "[D]"


class TowerEntrance(Location):
    """Entrance to the Eternal Spire."""

    def __init__(self):
        """Initialize the Tower entrance."""
        super().__init__(
            position=(37, 36),  # 1 tile north of Safe Haven
            name="The Eternal Spire",
            location_type=LocationType.TOWER_ENTRANCE,
            description=(
                "A massive obsidian tower that pierces the clouds. "
                "The ultimate challenge awaits within."
            ),
        )
        self.min_level_requirement = 10
        self.dungeon_requirement = 1  # Must complete at least 1 dungeon

    def can_enter(self, character: Character) -> Tuple[bool, str]:
        """Check if character meets requirements to enter tower.

        Args:
            character: Character trying to enter

        Returns:
            Tuple of (can_enter, reason_if_not)
        """
        char_level = getattr(character, "level", 1)
        dungeons_completed = getattr(character, "dungeons_completed", 0)

        if char_level < self.min_level_requirement:
            return (
                False,
                f"You must be at least level {self.min_level_requirement} to enter the Tower.",
            )

        if dungeons_completed < self.dungeon_requirement:
            return (
                False,
                f"You must complete at least {self.dungeon_requirement} dungeon "
                "before entering the Tower.",
            )

        return (True, "")

    def get_display_symbol(self) -> str:
        """Tower always shows its symbol once discovered."""
        return "[T]" if self.discovered else "?"
