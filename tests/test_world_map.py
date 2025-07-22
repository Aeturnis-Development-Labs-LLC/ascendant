"""Tests for world map generation and functionality."""

import pytest

from src.enums import TerrainType
from src.models.world_map import WorldMap, WorldTile


class TestWorldTile:
    """Tests for WorldTile class."""

    def test_world_tile_creation(self):
        """Test creating a world tile."""
        tile = WorldTile(10, 20, TerrainType.PLAINS)
        assert tile.x == 10
        assert tile.y == 20
        assert tile.terrain_type == TerrainType.PLAINS
        assert tile.location is None
        assert tile.discovered is False

    def test_tile_position_property(self):
        """Test position property returns tuple."""
        tile = WorldTile(5, 7, TerrainType.FOREST)
        assert tile.position == (5, 7)

    def test_tile_passability(self):
        """Test terrain passability."""
        # Most terrains are passable
        for terrain in [
            TerrainType.PLAINS,
            TerrainType.FOREST,
            TerrainType.MOUNTAINS,
            TerrainType.ROADS,
            TerrainType.SHADOWLANDS,
        ]:
            tile = WorldTile(0, 0, terrain)
            assert tile.is_passable() is True

        # Water is impassable
        water_tile = WorldTile(0, 0, TerrainType.WATER)
        assert water_tile.is_passable() is False


class TestWorldMap:
    """Tests for WorldMap class."""

    def test_world_map_dimensions(self):
        """Test world map has correct dimensions."""
        world = WorldMap(seed=42)
        assert world.WIDTH == 75
        assert world.HEIGHT == 75
        assert world.CENTER_X == 37
        assert world.CENTER_Y == 37
        assert len(world.tiles) == 75
        assert len(world.tiles[0]) == 75

    def test_world_map_initialization(self):
        """Test world map initializes with plains."""
        world = WorldMap(seed=42)
        # Check all tiles exist and start as plains
        for y in range(world.HEIGHT):
            for x in range(world.WIDTH):
                tile = world.tiles[y][x]
                assert tile is not None
                assert tile.terrain_type == TerrainType.PLAINS
                assert tile.position == (x, y)

    def test_deterministic_generation(self):
        """Test same seed produces same world."""
        world1 = WorldMap(seed=12345)
        world1.generate_world()

        world2 = WorldMap(seed=12345)
        world2.generate_world()

        # Check some random positions have same terrain
        test_positions = [(10, 10), (30, 30), (50, 50), (20, 60)]
        for x, y in test_positions:
            assert world1.tiles[y][x].terrain_type == world2.tiles[y][x].terrain_type

    def test_safe_haven_placement(self):
        """Test Safe Haven is placed at center."""
        world = WorldMap(seed=42)
        world.generate_world()

        # Check center area is cleared to plains
        center_x, center_y = world.safe_haven_position
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                x = center_x + dx
                y = center_y + dy
                assert world.tiles[y][x].terrain_type == TerrainType.PLAINS

    def test_shadowlands_on_edges(self):
        """Test shadowlands are placed on map edges."""
        world = WorldMap(seed=42)
        world.generate_world()

        # Check corners and edges have shadowlands
        edge_positions = [
            (0, 0),
            (74, 0),
            (0, 74),
            (74, 74),  # Corners
            (0, 37),
            (74, 37),
            (37, 0),
            (37, 74),  # Edge midpoints
        ]

        shadowland_count = 0
        for x, y in edge_positions:
            if world.tiles[y][x].terrain_type == TerrainType.SHADOWLANDS:
                shadowland_count += 1

        # At least some edges should be shadowlands
        assert shadowland_count > 4

    def test_terrain_variety(self):
        """Test that world has variety of terrain types."""
        world = WorldMap(seed=42)
        world.generate_world()

        terrain_counts = {terrain: 0 for terrain in TerrainType}

        for y in range(world.HEIGHT):
            for x in range(world.WIDTH):
                terrain_counts[world.tiles[y][x].terrain_type] += 1

        # Should have all terrain types
        assert terrain_counts[TerrainType.PLAINS] > 0
        assert terrain_counts[TerrainType.FOREST] > 0
        assert terrain_counts[TerrainType.MOUNTAINS] > 0
        assert terrain_counts[TerrainType.WATER] > 0
        assert terrain_counts[TerrainType.ROADS] > 0
        assert terrain_counts[TerrainType.SHADOWLANDS] > 0

    def test_roads_from_center(self):
        """Test roads extend from Safe Haven."""
        world = WorldMap(seed=42)
        world.generate_world()

        center_x, center_y = world.safe_haven_position

        # Check cardinal directions have roads
        road_found = {
            "north": False,
            "south": False,
            "east": False,
            "west": False,
        }

        # Check north
        for y in range(center_y - 10, center_y):
            if world.tiles[y][center_x].terrain_type == TerrainType.ROADS:
                road_found["north"] = True
                break

        # Check south
        for y in range(center_y + 1, center_y + 10):
            if world.tiles[y][center_x].terrain_type == TerrainType.ROADS:
                road_found["south"] = True
                break

        # Check east
        for x in range(center_x + 1, center_x + 10):
            if world.tiles[center_y][x].terrain_type == TerrainType.ROADS:
                road_found["east"] = True
                break

        # Check west
        for x in range(center_x - 10, center_x):
            if world.tiles[center_y][x].terrain_type == TerrainType.ROADS:
                road_found["west"] = True
                break

        # Should have roads in at least 3 directions
        roads_count = sum(1 for found in road_found.values() if found)
        assert roads_count >= 3

    def test_get_tile(self):
        """Test getting tiles by coordinates."""
        world = WorldMap(seed=42)

        # Valid positions
        tile = world.get_tile(10, 20)
        assert tile is not None
        assert tile.position == (10, 20)

        # Invalid positions
        assert world.get_tile(-1, 10) is None
        assert world.get_tile(10, -1) is None
        assert world.get_tile(75, 10) is None
        assert world.get_tile(10, 75) is None

    def test_is_valid_position(self):
        """Test position validation."""
        world = WorldMap(seed=42)

        # Valid positions
        assert world.is_valid_position(0, 0) is True
        assert world.is_valid_position(74, 74) is True
        assert world.is_valid_position(37, 37) is True

        # Invalid positions
        assert world.is_valid_position(-1, 0) is False
        assert world.is_valid_position(0, -1) is False
        assert world.is_valid_position(75, 0) is False
        assert world.is_valid_position(0, 75) is False

    def test_reveal_area(self):
        """Test fog of war reveal functionality."""
        world = WorldMap(seed=42)

        # Initially nothing discovered
        assert world.tiles[37][37].discovered is False

        # Reveal area around center
        world.reveal_area(37, 37, 3)

        # Check tiles within radius are discovered
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                x = 37 + dx
                y = 37 + dy
                distance = (dx * dx + dy * dy) ** 0.5
                if distance <= 3:
                    assert world.tiles[y][x].discovered is True

        # Check tiles outside radius remain undiscovered
        assert world.tiles[30][30].discovered is False
        assert world.tiles[44][44].discovered is False
