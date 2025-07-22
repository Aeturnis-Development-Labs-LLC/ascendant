"""Tests for fog of war system."""

from src.enums import TerrainType
from src.models.world_map import WorldMap


class TestFogOfWar:
    """Tests for fog of war functionality."""

    def test_initial_map_undiscovered(self):
        """Test that map starts completely undiscovered."""
        world = WorldMap(seed=42)
        world.generate_world()

        # Check that no tiles are discovered initially
        assert len(world.discovered_tiles) == 0

        # Check individual tiles
        for y in range(5):  # Just check a sample
            for x in range(5):
                assert not world.tiles[y][x].discovered
                assert not world.is_discovered(x, y)

    def test_reveal_area_basic(self):
        """Test basic area reveal functionality."""
        world = WorldMap(seed=42)
        world.generate_world()

        # Reveal area around center
        center_x, center_y = 10, 10
        radius = 3
        world.reveal_area(center_x, center_y, radius)

        # Check tiles within radius are discovered
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = center_x + dx
                y = center_y + dy
                distance = (dx * dx + dy * dy) ** 0.5
                if distance <= radius:
                    assert world.tiles[y][x].discovered
                    assert world.is_discovered(x, y)
                    assert (x, y) in world.discovered_tiles

    def test_reveal_area_bounds_checking(self):
        """Test reveal area respects map boundaries."""
        world = WorldMap(seed=42)
        world.generate_world()

        # Try to reveal near map edge
        world.reveal_area(0, 0, 5)

        # Should not crash and only reveal valid tiles
        assert world.is_discovered(0, 0)
        assert not world.is_discovered(-1, -1)  # Out of bounds

    def test_discovered_tiles_persistence(self):
        """Test that discovered tiles remain discovered."""
        world = WorldMap(seed=42)
        world.generate_world()

        # Reveal an area
        world.reveal_area(20, 20, 2)
        initial_discovered = len(world.discovered_tiles)

        # Reveal a different area
        world.reveal_area(40, 40, 2)

        # Original area should still be discovered
        assert world.is_discovered(20, 20)
        assert len(world.discovered_tiles) > initial_discovered

    def test_vision_radius_by_terrain(self):
        """Test vision radius varies by terrain type."""
        world = WorldMap()

        # Test each terrain type
        assert world.get_vision_radius(TerrainType.ROADS) == 5
        assert world.get_vision_radius(TerrainType.PLAINS) == 4
        assert world.get_vision_radius(TerrainType.FOREST) == 2
        assert world.get_vision_radius(TerrainType.MOUNTAINS) == 3
        assert world.get_vision_radius(TerrainType.SHADOWLANDS) == 2
        assert world.get_vision_radius(TerrainType.WATER) == 4

        # Test default for unknown terrain
        assert world.get_vision_radius(None) == 3  # type: ignore

    def test_reveal_with_terrain_based_radius(self):
        """Test revealing with terrain-specific vision radius."""
        world = WorldMap(seed=42)
        world.generate_world()

        # Find a tile with specific terrain
        test_x, test_y = 37, 37  # Safe Haven is plains
        tile = world.get_tile(test_x, test_y)
        assert tile is not None

        # Get vision radius for that terrain
        vision_radius = world.get_vision_radius(tile.terrain_type)

        # Reveal area with that radius
        world.reveal_area(test_x, test_y, vision_radius)

        # Check appropriate area is revealed
        revealed_count = 0
        for dy in range(-vision_radius - 1, vision_radius + 2):
            for dx in range(-vision_radius - 1, vision_radius + 2):
                x = test_x + dx
                y = test_y + dy
                if world.is_valid_position(x, y):
                    distance = (dx * dx + dy * dy) ** 0.5
                    if distance <= vision_radius:
                        if world.is_discovered(x, y):
                            revealed_count += 1

        assert revealed_count > 0

    def test_circular_reveal_pattern(self):
        """Test that reveal creates circular pattern, not square."""
        world = WorldMap(seed=42)
        world.generate_world()

        center_x, center_y = 30, 30
        radius = 4
        world.reveal_area(center_x, center_y, radius)

        # Corners outside radius should not be revealed
        corner_distance = (radius * radius + radius * radius) ** 0.5
        assert corner_distance > radius

        # Check specific corners are not revealed
        assert not world.is_discovered(center_x + radius, center_y + radius)
        assert not world.is_discovered(center_x - radius, center_y - radius)

        # But edges at radius should be revealed
        assert world.is_discovered(center_x + radius, center_y)
        assert world.is_discovered(center_x, center_y + radius)
