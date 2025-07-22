"""Tests for world map navigation system."""

import pytest

from src.enums import TerrainType
from src.game.world_navigation import WorldNavigation
from src.models.character import Character
from src.models.location import DungeonEntrance, SafeHaven
from src.models.world_map import WorldMap


class TestWorldNavigation:
    """Tests for WorldNavigation class."""

    @pytest.fixture
    def world_nav(self):
        """Create world map and navigation system."""
        world = WorldMap(seed=42)
        world.generate_world()
        return WorldNavigation(world)

    def test_movement_costs(self):
        """Test terrain movement costs."""
        nav = WorldNavigation(WorldMap())

        assert nav.get_movement_cost(TerrainType.ROADS) == 3.0
        assert nav.get_movement_cost(TerrainType.PLAINS) == 2.0
        assert nav.get_movement_cost(TerrainType.FOREST) == 1.0
        assert nav.get_movement_cost(TerrainType.MOUNTAINS) == 0.5
        assert nav.get_movement_cost(TerrainType.SHADOWLANDS) == 1.0
        assert nav.get_movement_cost(TerrainType.WATER) == 0.0

    def test_can_move_to(self, world_nav):
        """Test movement validation."""
        # Valid positions with passable terrain
        assert world_nav.can_move_to(37, 37) is True  # Center should be plains

        # Out of bounds
        assert world_nav.can_move_to(-1, 10) is False
        assert world_nav.can_move_to(10, -1) is False
        assert world_nav.can_move_to(75, 10) is False
        assert world_nav.can_move_to(10, 75) is False

        # Water tiles (if any exist) should be impassable
        for y in range(75):
            for x in range(75):
                tile = world_nav.world_map.get_tile(x, y)
                if tile and tile.terrain_type == TerrainType.WATER:
                    assert world_nav.can_move_to(x, y) is False
                    return  # Found at least one water tile to test

    def test_distance_calculations(self):
        """Test distance calculation methods."""
        nav = WorldNavigation(WorldMap())

        # Euclidean distance
        assert nav.calculate_distance((0, 0), (3, 4)) == 5.0  # 3-4-5 triangle
        assert nav.calculate_distance((10, 10), (10, 10)) == 0.0  # Same position

        # Manhattan distance
        assert nav.calculate_manhattan_distance((0, 0), (3, 4)) == 7
        assert nav.calculate_manhattan_distance((10, 10), (10, 10)) == 0
        assert nav.calculate_manhattan_distance((5, 5), (8, 9)) == 7  # |8-5| + |9-5|

    def test_vision_radius(self):
        """Test vision radius by terrain."""
        nav = WorldNavigation(WorldMap())

        assert nav.get_vision_radius(TerrainType.ROADS) == 5
        assert nav.get_vision_radius(TerrainType.PLAINS) == 4
        assert nav.get_vision_radius(TerrainType.FOREST) == 2
        assert nav.get_vision_radius(TerrainType.MOUNTAINS) == 3
        assert nav.get_vision_radius(TerrainType.SHADOWLANDS) == 2
        assert nav.get_vision_radius(TerrainType.WATER) == 4

    def test_reveal_from_position(self, world_nav):
        """Test revealing map from position."""
        # Ensure area is not discovered
        center_x, center_y = 37, 37
        for y in range(35, 40):
            for x in range(35, 40):
                world_nav.world_map.tiles[y][x].discovered = False

        # Reveal from center
        world_nav.reveal_from_position(center_x, center_y)

        # Check appropriate tiles are revealed based on terrain
        tile = world_nav.world_map.get_tile(center_x, center_y)
        radius = world_nav.get_vision_radius(tile.terrain_type)

        # At least the center and immediate neighbors should be revealed
        assert world_nav.world_map.tiles[center_y][center_x].discovered is True
        assert world_nav.world_map.tiles[center_y - 1][center_x].discovered is True
        assert world_nav.world_map.tiles[center_y + 1][center_x].discovered is True

    def test_can_enter_location_position_check(self):
        """Test location entry position validation."""
        nav = WorldNavigation(WorldMap())
        haven = SafeHaven()
        char = Character("Hero", 10, 10)

        # Character not at location
        char.world_position = (10, 10)
        can_enter, reason = nav.can_enter_location(char, haven)
        assert can_enter is False
        assert "must be at the location" in reason

        # Character at location
        char.world_position = haven.position
        can_enter, reason = nav.can_enter_location(char, haven)
        assert can_enter is True

    def test_discover_location(self):
        """Test location discovery."""
        nav = WorldNavigation(WorldMap())
        dungeon = DungeonEntrance((10, 10), "Test Dungeon", 1, 9, 3)
        char = Character("Hero", 10, 10)

        assert dungeon.discovered is False
        assert dungeon.position not in nav.discovered_locations

        nav.discover_location(char, dungeon)

        assert dungeon.discovered is True
        assert dungeon.position in nav.discovered_locations

    def test_find_nearby_locations(self):
        """Test finding locations within radius."""
        nav = WorldNavigation(WorldMap())

        locations = [
            SafeHaven(),  # at (37, 37)
            DungeonEntrance((40, 40), "Near", 1, 9, 3),
            DungeonEntrance((50, 50), "Far", 10, 19, 4),
        ]

        # From center, within radius 5
        nearby = nav.find_nearby_locations((37, 37), 5, locations)
        assert len(nearby) == 2  # Haven and Near dungeon
        assert locations[0] in nearby
        assert locations[1] in nearby
        assert locations[2] not in nearby

    def test_check_location_discovery(self):
        """Test automatic location discovery."""
        nav = WorldNavigation(WorldMap())

        locations = [
            DungeonEntrance((40, 37), "Close", 1, 9, 3),
            DungeonEntrance((45, 37), "Far", 10, 19, 4),
        ]

        # Mark as undiscovered
        for loc in locations:
            loc.discovered = False

        # Check from position with radius 3
        newly_discovered = nav.check_location_discovery((37, 37), locations, discovery_radius=3)

        assert len(newly_discovered) == 1
        assert newly_discovered[0] == locations[0]
        assert locations[0].discovered is True
        assert locations[1].discovered is False

    def test_character_world_position_fallback(self):
        """Test using character position when world_position not available."""
        nav = WorldNavigation(WorldMap())
        haven = SafeHaven()
        char = Character("Hero", 37, 37)  # No world_position attribute

        # Should use regular position as fallback
        can_enter, reason = nav.can_enter_location(char, haven)
        assert can_enter is True  # At correct position

        # Wrong position
        char2 = Character("Hero2", 10, 10)
        can_enter, reason = nav.can_enter_location(char2, haven)
        assert can_enter is False