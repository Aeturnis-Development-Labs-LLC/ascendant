"""Tests for Tile data structure - UTF Contract GAME-CORE-003."""

import pytest

from src.enums import EntityType, ItemType, TileType
from src.models.item import Item
from src.models.tile import Tile


# Create a simple mock entity for testing
class MockEntity:
    """Simple mock entity for testing."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.position = (x, y)
        self.entity_type = EntityType.MONSTER


class TestTile:
    """Tests for Tile class."""

    def test_tile_creation(self):
        """Test that a tile can be created with position and type."""
        tile = Tile(5, 10, TileType.FLOOR)
        assert tile.position == (5, 10)
        assert tile.x == 5
        assert tile.y == 10
        assert tile.tile_type == TileType.FLOOR
        assert tile.occupant is None
        assert tile.item is None

    def test_position_immutability(self):
        """Test that tile position cannot be modified."""
        tile = Tile(3, 4, TileType.WALL)

        # Position tuple is immutable
        with pytest.raises(AttributeError):
            tile.position = (5, 6)  # type: ignore[misc]

        # Individual coordinates cannot be set
        with pytest.raises(AttributeError):
            tile.x = 5  # type: ignore[misc]

        with pytest.raises(AttributeError):
            tile.y = 6  # type: ignore[misc]

    def test_tile_type_can_be_changed(self):
        """Test that tile type can be modified."""
        tile = Tile(0, 0, TileType.FLOOR)
        assert tile.tile_type == TileType.FLOOR

        tile.tile_type = TileType.WALL
        assert tile.tile_type == TileType.WALL

    def test_is_walkable_property(self):
        """Test that walkability is determined by tile type."""
        # Walkable tiles
        floor_tile = Tile(0, 0, TileType.FLOOR)
        assert floor_tile.is_walkable is True

        stairs_tile = Tile(0, 0, TileType.STAIRS_UP)
        assert stairs_tile.is_walkable is True

        # Non-walkable tiles
        wall_tile = Tile(0, 0, TileType.WALL)
        assert wall_tile.is_walkable is False

        trap_tile = Tile(0, 0, TileType.TRAP)
        assert trap_tile.is_walkable is False

        chest_tile = Tile(0, 0, TileType.CHEST)
        assert chest_tile.is_walkable is False

    def test_occupant_placement(self):
        """Test that entities can be placed on tiles."""
        tile = Tile(0, 0, TileType.FLOOR)
        entity = MockEntity(0, 0)

        tile.occupant = entity
        assert tile.occupant == entity

    def test_occupant_validation(self):
        """Test that multiple occupants are prevented."""
        tile = Tile(0, 0, TileType.FLOOR)
        entity1 = MockEntity((0, 0), EntityType.PLAYER)
        entity2 = MockEntity((0, 0), EntityType.MONSTER)

        tile.occupant = entity1

        with pytest.raises(ValueError) as exc_info:
            tile.occupant = entity2

        assert "already occupied" in str(exc_info.value)

    def test_occupant_clearing(self):
        """Test that occupants can be cleared."""
        tile = Tile(0, 0, TileType.FLOOR)
        entity = MockEntity(0, 0)

        tile.occupant = entity
        assert tile.occupant == entity

        tile.occupant = None
        assert tile.occupant is None

        # Can place new entity after clearing
        entity2 = MockEntity((0, 0), EntityType.MONSTER)
        tile.occupant = entity2
        assert tile.occupant == entity2

    def test_item_placement(self):
        """Test that items can be placed on tiles."""
        tile = Tile(0, 0, TileType.FLOOR)
        item = Item("Sword", ItemType.WEAPON)

        tile.item = item
        assert tile.item == item

        # Can replace items without validation
        item2 = Item("Potion", ItemType.CONSUMABLE)
        tile.item = item2
        assert tile.item == item2

    def test_string_representation(self):
        """Test string representations of tiles."""
        tile = Tile(3, 4, TileType.WALL)
        assert str(tile) == "Tile(3, 4, WALL)"

        # Test repr with occupant and item
        entity = MockEntity((3, 4), EntityType.PLAYER)
        item = Item("Key", ItemType.MISC)
        tile.occupant = entity
        tile.item = item

        repr_str = repr(tile)
        assert "x=3" in repr_str
        assert "y=4" in repr_str
        assert "type=WALL" in repr_str
        assert "occupied=True" in repr_str
        assert "has_item=True" in repr_str
