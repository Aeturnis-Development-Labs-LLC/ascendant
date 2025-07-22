"""Tests for location manager."""

import pytest

from src.game.location_manager import LocationManager
from src.models.location import DungeonEntrance, SafeHaven, TowerEntrance
from src.models.world_map import WorldMap


class TestLocationManager:
    """Tests for LocationManager class."""

    @pytest.fixture
    def location_manager(self):
        """Create world map and location manager."""
        world = WorldMap(seed=42)
        world.generate_world()
        manager = LocationManager(world)
        return manager

    def test_initialization(self, location_manager):
        """Test location manager initialization."""
        assert location_manager.world_map is not None
        assert len(location_manager.locations) == 0
        assert location_manager.safe_haven is None
        assert location_manager.tower is None

    def test_place_all_locations(self, location_manager):
        """Test placing all game locations."""
        location_manager.place_all_locations()

        # Check Safe Haven placed
        assert location_manager.safe_haven is not None
        assert location_manager.safe_haven.position == (37, 37)

        # Check Tower placed
        assert location_manager.tower is not None
        assert location_manager.tower.position == (37, 36)

        # Check dungeons placed (5 dungeons + haven + tower = 7 total)
        assert len(location_manager.locations) == 7

        # Verify all locations are on the map
        for location in location_manager.locations:
            x, y = location.position
            tile = location_manager.world_map.get_tile(x, y)
            assert tile is not None
            assert tile.location == location

    def test_dungeon_placement_distances(self, location_manager):
        """Test dungeons are placed at correct distances."""
        location_manager.place_all_locations()
        
        center_x, center_y = location_manager.world_map.safe_haven_position
        dungeons = location_manager.get_dungeons()

        expected_distances = {
            "Novice Hollow": 9.899,  # ~10 (7,7 offset)
            "Apprentice Caverns": 16.97,  # ~17 (-12,12 offset)
            "Journeyman Depths": 18.38,  # ~18 (-13,-13 offset)
            "Expert Catacombs": 25.0,  # 25 (0,-25 offset)
            "Master Crypts": 35.0,  # 35 (0,-35 offset)
        }

        for dungeon in dungeons:
            if dungeon.name in expected_distances:
                dx = dungeon.position[0] - center_x
                dy = dungeon.position[1] - center_y
                actual_distance = (dx * dx + dy * dy) ** 0.5
                expected = expected_distances[dungeon.name]
                assert abs(actual_distance - expected) < 0.1, f"{dungeon.name} at wrong distance"

    def test_dungeon_level_brackets(self, location_manager):
        """Test dungeons have correct level brackets."""
        location_manager.place_all_locations()
        dungeons = location_manager.get_dungeons()

        expected_brackets = {
            "Novice Hollow": (1, 9, 3),
            "Apprentice Caverns": (10, 19, 4),
            "Journeyman Depths": (20, 29, 5),
            "Expert Catacombs": (30, 39, 6),
            "Master Crypts": (40, 49, 7),
        }

        for dungeon in dungeons:
            if dungeon.name in expected_brackets:
                min_lvl, max_lvl, floors = expected_brackets[dungeon.name]
                assert dungeon.min_level == min_lvl
                assert dungeon.max_level == max_lvl
                assert dungeon.floor_count == floors

    def test_get_location_at(self, location_manager):
        """Test getting location at coordinates."""
        location_manager.place_all_locations()

        # Get Safe Haven
        haven = location_manager.get_location_at(37, 37)
        assert haven is not None
        assert isinstance(haven, SafeHaven)

        # Get Tower
        tower = location_manager.get_location_at(37, 36)
        assert tower is not None
        assert isinstance(tower, TowerEntrance)

        # Empty tile
        empty = location_manager.get_location_at(50, 50)
        assert empty is None

        # Out of bounds
        oob = location_manager.get_location_at(-1, -1)
        assert oob is None

    def test_get_all_locations(self, location_manager):
        """Test getting all locations."""
        location_manager.place_all_locations()
        
        locations = location_manager.get_all_locations()
        assert len(locations) == 7
        
        # Should be a copy, not the original list
        locations.append(None)
        assert len(location_manager.locations) == 7

    def test_get_dungeons(self, location_manager):
        """Test getting only dungeon entrances."""
        location_manager.place_all_locations()
        
        dungeons = location_manager.get_dungeons()
        assert len(dungeons) == 5
        
        for dungeon in dungeons:
            assert isinstance(dungeon, DungeonEntrance)

    def test_validate_dungeon_access(self, location_manager):
        """Test dungeon access validation."""
        assert location_manager.validate_dungeon_access(5, 9) is True
        assert location_manager.validate_dungeon_access(9, 9) is True
        assert location_manager.validate_dungeon_access(10, 9) is False
        assert location_manager.validate_dungeon_access(20, 19) is False

    def test_get_accessible_dungeons(self, location_manager):
        """Test getting dungeons character can enter."""
        location_manager.place_all_locations()

        # Level 5 character
        accessible = location_manager.get_accessible_dungeons(5)
        assert len(accessible) == 1  # Only Novice Hollow
        assert accessible[0].name == "Novice Hollow"

        # Level 15 character
        accessible = location_manager.get_accessible_dungeons(15)
        assert len(accessible) == 1  # Only Apprentice (too high for Novice)
        assert accessible[0].name == "Apprentice Caverns"

        # Level 35 character
        accessible = location_manager.get_accessible_dungeons(35)
        assert len(accessible) == 1  # Only Expert Catacombs (30-39)
        assert accessible[0].name == "Expert Catacombs"

        # Level 45 character
        accessible = location_manager.get_accessible_dungeons(45)
        assert len(accessible) == 1  # Only Master Crypts (40-49)
        assert accessible[0].name == "Master Crypts"

        # Level 50 character (too high for any dungeon)
        accessible = location_manager.get_accessible_dungeons(50)
        assert len(accessible) == 0  # Can't enter any dungeons

    def test_find_nearest_location(self, location_manager):
        """Test finding nearest location."""
        location_manager.place_all_locations()

        # From center, nearest should be Safe Haven itself
        nearest, distance = location_manager.find_nearest_location((37, 37))
        assert nearest.name == "Safe Haven"
        assert distance == 0.0

        # From just north of center, nearest should be Tower
        nearest, distance = location_manager.find_nearest_location((37, 35))
        assert nearest.name == "The Eternal Spire"
        assert distance == 1.0

        # Filter by type - nearest dungeon from center
        nearest, distance = location_manager.find_nearest_location((37, 37), DungeonEntrance)
        assert isinstance(nearest, DungeonEntrance)
        assert nearest.name == "Novice Hollow"  # Should be closest dungeon

        # No locations returns None
        manager_empty = LocationManager(WorldMap())
        result = manager_empty.find_nearest_location((0, 0))
        assert result is None