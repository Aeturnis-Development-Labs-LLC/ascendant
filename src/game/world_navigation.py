"""World map navigation and movement system."""

from typing import Dict, Set, Tuple

from src.enums import TerrainType
from src.models.character import Character
from src.models.location import Location
from src.models.world_map import WorldMap


class WorldNavigation:
    """Handles movement and navigation on the world map."""

    # Movement costs by terrain (tiles per turn)
    MOVEMENT_COSTS: Dict[TerrainType, float] = {
        TerrainType.ROADS: 3.0,
        TerrainType.PLAINS: 2.0,
        TerrainType.FOREST: 1.0,
        TerrainType.MOUNTAINS: 0.5,
        TerrainType.SHADOWLANDS: 1.0,
        TerrainType.WATER: 0.0,  # Impassable
    }

    # Vision radius by terrain
    VISION_RADIUS: Dict[TerrainType, int] = {
        TerrainType.ROADS: 5,
        TerrainType.PLAINS: 4,
        TerrainType.FOREST: 2,
        TerrainType.MOUNTAINS: 3,
        TerrainType.SHADOWLANDS: 2,
        TerrainType.WATER: 4,
    }

    def __init__(self, world_map: WorldMap):
        """Initialize navigation system.

        Args:
            world_map: The world map to navigate
        """
        self.world_map = world_map
        self.discovered_locations: Set[Tuple[int, int]] = set()

    def get_movement_cost(self, terrain: TerrainType) -> float:
        """Get movement cost for terrain type.

        Args:
            terrain: Type of terrain

        Returns:
            Tiles that can be moved per turn (0 if impassable)
        """
        return self.MOVEMENT_COSTS.get(terrain, 1.0)

    def can_move_to(self, x: int, y: int) -> bool:
        """Check if position can be moved to.

        Args:
            x: Target X coordinate
            y: Target Y coordinate

        Returns:
            True if position is valid and passable
        """
        tile = self.world_map.get_tile(x, y)
        if tile is None:
            return False
        return tile.is_passable()

    def calculate_distance(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> float:
        """Calculate straight-line distance between positions.

        Args:
            from_pos: Starting position (x, y)
            to_pos: Target position (x, y)

        Returns:
            Euclidean distance
        """
        dx = to_pos[0] - from_pos[0]
        dy = to_pos[1] - from_pos[1]
        return float((dx * dx + dy * dy) ** 0.5)

    def calculate_manhattan_distance(
        self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]
    ) -> int:
        """Calculate Manhattan distance between positions.

        Args:
            from_pos: Starting position (x, y)
            to_pos: Target position (x, y)

        Returns:
            Manhattan distance (sum of absolute differences)
        """
        return abs(to_pos[0] - from_pos[0]) + abs(to_pos[1] - from_pos[1])

    def get_vision_radius(self, terrain: TerrainType) -> int:
        """Get vision radius for terrain type.

        Args:
            terrain: Current terrain type

        Returns:
            Vision radius in tiles
        """
        return self.VISION_RADIUS.get(terrain, 3)

    def reveal_from_position(self, x: int, y: int) -> None:
        """Reveal map from a position based on terrain.

        Args:
            x: Current X position
            y: Current Y position
        """
        tile = self.world_map.get_tile(x, y)
        if tile is None:
            return

        radius = self.get_vision_radius(tile.terrain_type)
        self.world_map.reveal_area(x, y, radius)

    def can_enter_location(self, character: Character, location: Location) -> Tuple[bool, str]:
        """Check if character can enter a location.

        Args:
            character: Character trying to enter
            location: Target location

        Returns:
            Tuple of (can_enter, reason_if_not)
        """
        # First check if at the location
        char_pos = getattr(character, "world_position", character.position)
        if char_pos != location.position:
            return (False, "You must be at the location to enter.")

        # Then check location-specific requirements
        return location.can_enter(character)

    def discover_location(self, character: Character, location: Location) -> None:
        """Mark a location as discovered by character.

        Args:
            character: Character who discovered it
            location: Location to discover
        """
        location.discover()
        self.discovered_locations.add(location.position)

        # Track on character if they have that attribute
        if hasattr(character, "discovered_locations"):
            character.discovered_locations.add(location.position)

    def find_nearby_locations(
        self, position: Tuple[int, int], radius: int, locations: list[Location]
    ) -> list[Location]:
        """Find locations within radius of position.

        Args:
            position: Center position
            radius: Search radius
            locations: List of all locations to check

        Returns:
            List of locations within radius
        """
        nearby = []
        for location in locations:
            if self.calculate_distance(position, location.position) <= radius:
                nearby.append(location)
        return nearby

    def check_location_discovery(
        self, character_pos: Tuple[int, int], locations: list[Location], discovery_radius: int = 3
    ) -> list[Location]:
        """Check for newly discovered locations.

        Args:
            character_pos: Character's current position
            locations: All locations to check
            discovery_radius: How close to auto-discover

        Returns:
            List of newly discovered locations
        """
        newly_discovered = []
        for location in locations:
            if not location.discovered:
                distance = self.calculate_distance(character_pos, location.position)
                if distance <= discovery_radius:
                    location.discover()
                    newly_discovered.append(location)
        return newly_discovered
