"""Tests for core enumerations - UTF Contract GAME-CORE-002."""

import pytest

from src.enums import Direction, EntityType, ItemType, TileType


class TestTileType:
    """Tests for TileType enum."""

    def test_all_tile_types_exist(self):
        """Test that all required tile types are defined."""
        expected_types = {"FLOOR", "WALL", "STAIRS_UP", "STAIRS_DOWN", "TRAP", "CHEST", "DOOR"}
        actual_types = {tile.name for tile in TileType}
        assert actual_types == expected_types

    def test_tile_type_string_representation(self):
        """Test that string representation returns the name."""
        assert str(TileType.FLOOR) == "FLOOR"
        assert str(TileType.WALL) == "WALL"

    def test_tile_type_immutability(self):
        """Test that enum values cannot be modified."""
        with pytest.raises(AttributeError):
            TileType.FLOOR.value = 999  # type: ignore[misc]


class TestDirection:
    """Tests for Direction enum."""

    def test_all_directions_exist(self):
        """Test that all required directions are defined."""
        expected_directions = {
            "NORTH",
            "SOUTH",
            "EAST",
            "WEST",
            "NORTHEAST",
            "NORTHWEST",
            "SOUTHEAST",
            "SOUTHWEST",
        }
        actual_directions = {direction.name for direction in Direction}
        assert actual_directions == expected_directions

    def test_direction_vectors(self):
        """Test that direction vectors are correct."""
        assert Direction.NORTH.dx == 0 and Direction.NORTH.dy == -1
        assert Direction.SOUTH.dx == 0 and Direction.SOUTH.dy == 1
        assert Direction.EAST.dx == 1 and Direction.EAST.dy == 0
        assert Direction.WEST.dx == -1 and Direction.WEST.dy == 0

    def test_direction_string_representation(self):
        """Test that string representation returns the name."""
        assert str(Direction.NORTH) == "NORTH"
        assert str(Direction.EAST) == "EAST"


class TestItemType:
    """Tests for ItemType enum."""

    def test_all_item_types_exist(self):
        """Test that all required item types are defined."""
        expected_types = {"WEAPON", "ARMOR", "CONSUMABLE", "MISC", "KEY"}
        actual_types = {item.name for item in ItemType}
        assert actual_types == expected_types

    def test_item_type_string_representation(self):
        """Test that string representation returns the name."""
        assert str(ItemType.WEAPON) == "WEAPON"
        assert str(ItemType.CONSUMABLE) == "CONSUMABLE"


class TestEntityType:
    """Tests for EntityType enum."""

    def test_all_entity_types_exist(self):
        """Test that all required entity types are defined."""
        expected_types = {"PLAYER", "MONSTER", "NPC"}
        actual_types = {entity.name for entity in EntityType}
        assert actual_types == expected_types

    def test_entity_type_string_representation(self):
        """Test that string representation returns the name."""
        assert str(EntityType.PLAYER) == "PLAYER"
        assert str(EntityType.MONSTER) == "MONSTER"
