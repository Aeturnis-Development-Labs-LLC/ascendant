"""Manages placement and tracking of world map locations."""

from typing import List, Optional, Tuple

from src.models.location import DungeonEntrance, Location, SafeHaven, TowerEntrance
from src.models.world_map import WorldMap


class LocationManager:
    """Manages all locations on the world map."""

    def __init__(self, world_map: WorldMap):
        """Initialize location manager.

        Args:
            world_map: The world map to place locations on
        """
        self.world_map = world_map
        self.locations: List[Location] = []
        self.safe_haven: Optional[SafeHaven] = None
        self.tower: Optional[TowerEntrance] = None

    def place_all_locations(self) -> None:
        """Place all game locations at their designated positions."""
        # Place Safe Haven
        self.safe_haven = SafeHaven()
        self._place_location(self.safe_haven)

        # Place Tower (1 tile north of Haven)
        self.tower = TowerEntrance()
        self._place_location(self.tower)

        # Place dungeons at specified distances
        self._place_dungeons()

    def _place_location(self, location: Location) -> None:
        """Place a location on the world map.

        Args:
            location: Location to place
        """
        x, y = location.position
        tile = self.world_map.get_tile(x, y)
        if tile:
            tile.location = location  # type: ignore[assignment]
            self.locations.append(location)

    def _place_dungeons(self) -> None:
        """Place all bracket dungeons at correct distances."""
        # Define dungeon configurations
        dungeon_configs = [
            # (name, position offset from center, min_lvl, max_lvl, floors)
            ("Novice Hollow", (7, 7), 1, 9, 3),  # 7 tiles SE
            ("Apprentice Caverns", (-12, 12), 10, 19, 4),  # 12 tiles SW
            ("Journeyman Depths", (-13, -13), 20, 29, 5),  # 18 tiles NW
            ("Expert Catacombs", (0, -25), 30, 39, 6),  # 25 tiles N
            ("Master Crypts", (0, -35), 40, 49, 7),  # 35 tiles N
        ]

        center_x, center_y = self.world_map.safe_haven_position

        for name, offset, min_lvl, max_lvl, floors in dungeon_configs:
            position = (center_x + offset[0], center_y + offset[1])

            # Ensure position is valid
            if self.world_map.is_valid_position(*position):
                dungeon = DungeonEntrance(position, name, min_lvl, max_lvl, floors)
                self._place_location(dungeon)

    def get_location_at(self, x: int, y: int) -> Optional[Location]:
        """Get location at specific coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Location at position or None
        """
        tile = self.world_map.get_tile(x, y)
        if tile:
            return tile.location
        return None

    def get_all_locations(self) -> List[Location]:
        """Get list of all locations.

        Returns:
            List of all placed locations
        """
        return self.locations.copy()

    def get_dungeons(self) -> List[DungeonEntrance]:
        """Get list of all dungeon entrances.

        Returns:
            List of dungeon entrances
        """
        return [loc for loc in self.locations if isinstance(loc, DungeonEntrance)]

    def validate_dungeon_access(self, character_level: int, bracket_max: int) -> bool:
        """Check if character can access a dungeon bracket.

        Args:
            character_level: Character's current level
            bracket_max: Maximum level for dungeon bracket

        Returns:
            True if character can enter
        """
        return character_level <= bracket_max

    def get_accessible_dungeons(self, character_level: int) -> List[DungeonEntrance]:
        """Get list of dungeons character can enter.

        Args:
            character_level: Character's level

        Returns:
            List of accessible dungeons
        """
        accessible = []
        for dungeon in self.get_dungeons():
            # Can enter if character level is within the dungeon's range
            if dungeon.min_level <= character_level <= dungeon.max_level:
                accessible.append(dungeon)
        return accessible

    def find_nearest_location(
        self, from_pos: Tuple[int, int], location_type: Optional[type] = None
    ) -> Optional[Tuple[Location, float]]:
        """Find nearest location to a position.

        Args:
            from_pos: Starting position
            location_type: Optional type filter (e.g., DungeonEntrance)

        Returns:
            Tuple of (nearest_location, distance) or None
        """
        nearest = None
        min_distance = float("inf")

        for location in self.locations:
            if location_type and not isinstance(location, location_type):
                continue

            dx = location.position[0] - from_pos[0]
            dy = location.position[1] - from_pos[1]
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < min_distance:
                min_distance = distance
                nearest = location

        if nearest:
            return (nearest, min_distance)
        return None
