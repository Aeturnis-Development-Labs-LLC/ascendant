"""World map system for overworld navigation."""

import random
from typing import Dict, List, Optional, Set, Tuple

from src.enums import TerrainType
from src.models.location import DungeonEntrance, SafeHaven, TowerEntrance


class WorldTile:
    """Represents a single tile on the world map."""

    def __init__(self, x: int, y: int, terrain_type: TerrainType):
        """Initialize a world tile.

        Args:
            x: X coordinate
            y: Y coordinate
            terrain_type: Type of terrain
        """
        self.x = x
        self.y = y
        self.terrain_type = terrain_type
        self.location = None  # Will hold Location objects
        self.discovered = False

    @property
    def position(self) -> Tuple[int, int]:
        """Get tile position as tuple."""
        return (self.x, self.y)

    def is_passable(self) -> bool:
        """Check if tile can be walked on."""
        return self.terrain_type != TerrainType.WATER


class WorldMap:
    """Represents the overworld map (75x75 grid)."""

    WIDTH = 75
    HEIGHT = 75
    CENTER_X = 37
    CENTER_Y = 37

    # Vision radius by terrain type (per GAME-WORLD-014)
    VISION_RADIUS_BY_TERRAIN: Dict[TerrainType, int] = {
        TerrainType.ROADS: 5,
        TerrainType.PLAINS: 4,
        TerrainType.FOREST: 2,
        TerrainType.MOUNTAINS: 3,
        TerrainType.SHADOWLANDS: 2,
        TerrainType.WATER: 4,
    }

    def __init__(self, seed: Optional[int] = None):
        """Initialize the world map.

        Args:
            seed: Random seed for generation
        """
        self.seed = seed if seed is not None else random.randint(0, 999999)
        self.rng = random.Random(self.seed)
        self.tiles: List[List[WorldTile]] = []
        self.safe_haven_position = (self.CENTER_X, self.CENTER_Y)
        self.discovered_tiles: Set[Tuple[int, int]] = set()
        self.locations: List = []  # List of all locations on the map

        # Initialize empty grid
        for y in range(self.HEIGHT):
            row = []
            for x in range(self.WIDTH):
                row.append(WorldTile(x, y, TerrainType.PLAINS))
            self.tiles.append(row)

        # Add width and height properties for compatibility
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.safe_haven: Optional[SafeHaven] = None  # Will be set during generation

    def generate_world(self) -> None:
        """Generate the world terrain."""
        # Start with all plains
        self._generate_base_terrain()

        # Add terrain features
        self._generate_mountains()
        self._generate_forests()
        self._generate_water()
        self._generate_shadowlands()
        self._generate_roads()

        # Place Safe Haven
        self._place_safe_haven()

        # Place other locations
        self._place_locations()

    def _generate_base_terrain(self) -> None:
        """Fill world with base terrain (plains)."""
        # Already done in __init__, but method here for clarity
        pass

    def _generate_mountains(self) -> None:
        """Generate mountain ranges."""
        # Northern mountain range
        for _ in range(3):  # 3 mountain clusters
            center_x = self.rng.randint(10, 65)
            center_y = self.rng.randint(5, 20)
            self._create_terrain_cluster(center_x, center_y, TerrainType.MOUNTAINS, 8, 12)

    def _generate_forests(self) -> None:
        """Generate forest areas."""
        # Multiple forest clusters
        for _ in range(5):  # 5 forest areas
            center_x = self.rng.randint(10, 65)
            center_y = self.rng.randint(10, 65)
            self._create_terrain_cluster(center_x, center_y, TerrainType.FOREST, 6, 10)

    def _generate_water(self) -> None:
        """Generate lakes and rivers."""
        # A few lakes
        for _ in range(2):
            center_x = self.rng.randint(15, 60)
            center_y = self.rng.randint(15, 60)
            self._create_terrain_cluster(center_x, center_y, TerrainType.WATER, 4, 6)

    def _generate_shadowlands(self) -> None:
        """Generate dangerous shadowlands on the edges."""
        # Outer edges become shadowlands
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                distance_from_edge = min(x, y, self.WIDTH - x - 1, self.HEIGHT - y - 1)
                if distance_from_edge < 3:
                    self.tiles[y][x].terrain_type = TerrainType.SHADOWLANDS

    def _generate_roads(self) -> None:
        """Generate roads connecting key areas."""
        # Main road from Safe Haven going in cardinal directions
        center_x, center_y = self.safe_haven_position

        # Road to the east
        for x in range(center_x, min(center_x + 20, self.WIDTH)):
            if self.tiles[center_y][x].terrain_type != TerrainType.WATER:
                self.tiles[center_y][x].terrain_type = TerrainType.ROADS

        # Road to the west
        for x in range(max(center_x - 20, 0), center_x):
            if self.tiles[center_y][x].terrain_type != TerrainType.WATER:
                self.tiles[center_y][x].terrain_type = TerrainType.ROADS

        # Road to the north
        for y in range(max(center_y - 20, 0), center_y):
            if self.tiles[y][center_x].terrain_type != TerrainType.WATER:
                self.tiles[y][center_x].terrain_type = TerrainType.ROADS

        # Road to the south
        for y in range(center_y, min(center_y + 20, self.HEIGHT)):
            if self.tiles[y][center_x].terrain_type != TerrainType.WATER:
                self.tiles[y][center_x].terrain_type = TerrainType.ROADS

    def _create_terrain_cluster(
        self, center_x: int, center_y: int, terrain_type: TerrainType, min_size: int, max_size: int
    ) -> None:
        """Create a cluster of terrain around a center point.

        Args:
            center_x: Center X coordinate
            center_y: Center Y coordinate
            terrain_type: Type of terrain to place
            min_size: Minimum radius
            max_size: Maximum radius
        """
        size = self.rng.randint(min_size, max_size)
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                x = center_x + dx
                y = center_y + dy
                if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
                    # Use distance to create roughly circular clusters
                    distance = (dx * dx + dy * dy) ** 0.5
                    if distance <= size and self.rng.random() > distance / (size * 1.5):
                        self.tiles[y][x].terrain_type = terrain_type

    def _place_safe_haven(self) -> None:
        """Clear area around Safe Haven and create the location."""
        center_x, center_y = self.safe_haven_position

        # Clear 5x5 area for Safe Haven
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x = center_x + dx
                y = center_y + dy
                if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
                    self.tiles[y][x].terrain_type = TerrainType.PLAINS

        # Create SafeHaven instance
        self.safe_haven = SafeHaven()

        # Add locations list if not exists
        if not hasattr(self, "locations"):
            self.locations = []
        self.locations.append(self.safe_haven)

    def _place_locations(self) -> None:
        """Place additional locations on the map."""
        # Place Tower Entrance at a fixed position
        tower_entrance = TowerEntrance()
        self.locations.append(tower_entrance)

        # Place at least 2 dungeon entrances
        # Beginner dungeon near safe haven
        beginner_dungeon = DungeonEntrance(
            position=(45, 37),  # East of safe haven
            name="Caves of Learning",
            min_level=1,
            max_level=10,
            floor_count=5,
        )
        self.locations.append(beginner_dungeon)

        # Intermediate dungeon further away
        intermediate_dungeon = DungeonEntrance(
            position=(20, 20),  # Northwest
            name="Forgotten Crypts",
            min_level=10,
            max_level=20,
            floor_count=10,
        )
        self.locations.append(intermediate_dungeon)

    def get_tile(self, x: int, y: int) -> Optional[WorldTile]:
        """Get tile at position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            WorldTile or None if out of bounds
        """
        if 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT:
            return self.tiles[y][x]
        return None

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within map bounds.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if position is valid
        """
        return 0 <= x < self.WIDTH and 0 <= y < self.HEIGHT

    def reveal_area(self, center_x: int, center_y: int, radius: int) -> None:
        """Reveal tiles around a position.

        Args:
            center_x: Center X coordinate
            center_y: Center Y coordinate
            radius: Vision radius
        """
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy
                if self.is_valid_position(x, y):
                    distance = (dx * dx + dy * dy) ** 0.5
                    if distance <= radius:
                        self.tiles[y][x].discovered = True
                        self.discovered_tiles.add((x, y))

    def is_discovered(self, x: int, y: int) -> bool:
        """Check if a tile has been discovered.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if tile has been discovered
        """
        return (x, y) in self.discovered_tiles

    def get_vision_radius(self, terrain: TerrainType) -> int:
        """Get vision radius for terrain type.

        Args:
            terrain: Current terrain type

        Returns:
            Vision radius in tiles
        """
        return self.VISION_RADIUS_BY_TERRAIN.get(terrain, 3)

    def generate(self) -> None:
        """Alias for generate_world() to match expected interface."""
        self.generate_world()
