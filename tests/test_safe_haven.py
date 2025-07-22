"""Tests for Safe Haven interior and mechanics."""

import pytest

from src.enums import TileType
from src.models.character import Character
from src.models.floor import Floor
from src.models.safe_haven import EnhancedSafeHaven, SafeHavenInterior


class TestSafeHavenInterior:
    """Tests for Safe Haven interior layout."""

    @pytest.fixture
    def interior(self):
        """Create a SafeHavenInterior instance."""
        return SafeHavenInterior()

    def test_zone_locations(self, interior):
        """Test that all zones are at correct positions."""
        assert interior.SPAWN_PLAZA == (2, 2)
        assert interior.MERCHANT_QUARTER == (3, 2)
        assert interior.HALL_OF_SOULS == (1, 2)
        assert interior.STORAGE_VAULTS == (2, 3)
        assert interior.LOST_SOUL_MEMORIAL == (2, 1)

    def test_zone_names(self, interior):
        """Test zone name mapping."""
        assert interior.zones[interior.SPAWN_PLAZA] == "Spawn Plaza"
        assert interior.zones[interior.MERCHANT_QUARTER] == "Merchant Quarter"
        assert interior.zones[interior.HALL_OF_SOULS] == "Hall of Souls"
        assert interior.zones[interior.STORAGE_VAULTS] == "Storage Vaults"
        assert interior.zones[interior.LOST_SOUL_MEMORIAL] == "Lost Soul Memorial"

    def test_create_detailed_interior(self, interior):
        """Test interior floor creation."""
        floor = interior.create_detailed_interior()

        # Check it's a valid floor
        assert isinstance(floor, Floor)
        assert floor.width == Floor.FLOOR_WIDTH
        assert floor.height == Floor.FLOOR_HEIGHT

        # Check 5x5 center area is all floor tiles
        center_start = (Floor.FLOOR_WIDTH - 5) // 2
        center_end = center_start + 5

        for y in range(center_start, center_end):
            for x in range(center_start, center_end):
                tile = floor.get_tile(x, y)
                assert tile is not None
                assert tile.tile_type == TileType.FLOOR

    def test_get_zone_at(self, interior):
        """Test zone lookup by position."""
        center_start = (Floor.FLOOR_WIDTH - 5) // 2

        # Test spawn plaza (center)
        spawn_pos = (center_start + 2, center_start + 2)
        assert interior.get_zone_at(spawn_pos) == "Spawn Plaza"

        # Test merchant quarter (east)
        merchant_pos = (center_start + 3, center_start + 2)
        assert interior.get_zone_at(merchant_pos) == "Merchant Quarter"

        # Test position outside special zones
        outside_pos = (center_start + 4, center_start + 4)
        assert interior.get_zone_at(outside_pos) is None

    def test_is_in_safe_haven(self, interior):
        """Test Safe Haven boundary checking."""
        center_start = (Floor.FLOOR_WIDTH - 5) // 2
        center_end = center_start + 5

        # Inside Safe Haven
        assert interior.is_in_safe_haven((center_start, center_start))
        assert interior.is_in_safe_haven((center_start + 2, center_start + 2))
        assert interior.is_in_safe_haven((center_end - 1, center_end - 1))

        # Outside Safe Haven
        assert not interior.is_in_safe_haven((center_start - 1, center_start))
        assert not interior.is_in_safe_haven((center_end, center_end))
        assert not interior.is_in_safe_haven((0, 0))

    def test_no_combat_zone(self, interior):
        """Test combat is forbidden in Safe Haven."""
        character = Character("Test Hero", 10, 10)
        can_attack, reason = interior.can_attack(character, (10, 10))

        assert can_attack is False
        assert "Combat is forbidden" in reason

    def test_respawn_positions(self, interior):
        """Test respawn positions for different character types."""
        center_start = (Floor.FLOOR_WIDTH - 5) // 2

        # New character spawns at plaza
        new_spawn = interior.get_respawn_position(is_lost_soul=False)
        expected_plaza = (center_start + 2, center_start + 2)
        assert new_spawn == expected_plaza

        # Lost Soul spawns at memorial
        soul_spawn = interior.get_respawn_position(is_lost_soul=True)
        expected_memorial = (center_start + 2, center_start + 1)
        assert soul_spawn == expected_memorial


class TestEnhancedSafeHaven:
    """Tests for enhanced Safe Haven location."""

    @pytest.fixture
    def safe_haven(self):
        """Create an EnhancedSafeHaven instance."""
        return EnhancedSafeHaven()

    def test_initialization(self, safe_haven):
        """Test Safe Haven is properly initialized."""
        assert safe_haven.name == "Safe Haven"
        assert safe_haven.position == (37, 37)  # Center of world map
        assert safe_haven.discovered is True  # Always discovered
        assert safe_haven.no_combat is True
        assert safe_haven.interior is not None

    def test_can_always_enter(self, safe_haven):
        """Test Safe Haven can always be entered."""
        character = Character("Test Hero", 10, 10)
        can_enter, reason = safe_haven.can_enter(character)

        assert can_enter is True
        assert reason == ""

    def test_create_interior(self, safe_haven):
        """Test interior creation returns proper floor."""
        floor = safe_haven.create_interior()
        assert isinstance(floor, Floor)

        # Verify it has the Safe Haven layout
        center_start = (Floor.FLOOR_WIDTH - 5) // 2
        center_end = center_start + 5

        for y in range(center_start, center_end):
            for x in range(center_start, center_end):
                tile = floor.get_tile(x, y)
                assert tile.tile_type == TileType.FLOOR

    def test_spawn_points(self, safe_haven):
        """Test spawn points for different character types."""
        # New character spawn
        new_spawn = safe_haven.get_spawn_point(is_lost_soul=False)
        assert isinstance(new_spawn, tuple)
        assert len(new_spawn) == 2

        # Lost Soul spawn
        soul_spawn = safe_haven.get_spawn_point(is_lost_soul=True)
        assert isinstance(soul_spawn, tuple)
        assert len(soul_spawn) == 2

        # Should be different positions
        assert new_spawn != soul_spawn
