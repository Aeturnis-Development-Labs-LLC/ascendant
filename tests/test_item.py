"""Tests for Item base class - UTF Contract GAME-CORE-005."""

import pytest

from src.enums import ItemType
from src.models.item import Item


class TestItem:
    """Tests for Item class."""

    def test_item_creation(self):
        """Test that an item can be created with name and type."""
        item = Item("Sword", ItemType.WEAPON)
        assert item.name == "Sword"
        assert item.item_type == ItemType.WEAPON
        assert item.item_id is not None

    def test_item_id_generation(self):
        """Test that item IDs are automatically generated."""
        item1 = Item("Potion", ItemType.CONSUMABLE)
        item2 = Item("Potion", ItemType.CONSUMABLE)

        # IDs should be unique even for items with same name
        assert item1.item_id != item2.item_id

        # IDs should be valid UUIDs (36 characters with hyphens)
        assert len(item1.item_id) == 36
        assert item1.item_id.count("-") == 4

    def test_item_id_provided(self):
        """Test that custom item IDs can be provided."""
        custom_id = "custom-item-id-456"
        item = Item("Shield", ItemType.ARMOR, item_id=custom_id)
        assert item.item_id == custom_id

    def test_name_validation_empty(self):
        """Test that empty names are rejected."""
        with pytest.raises(ValueError) as exc_info:
            Item("", ItemType.MISC)
        assert "name cannot be empty" in str(exc_info.value)

    def test_name_validation_whitespace(self):
        """Test that whitespace-only names are rejected."""
        with pytest.raises(ValueError) as exc_info:
            Item("   ", ItemType.MISC)
        assert "name cannot be empty" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            Item("\t\n", ItemType.MISC)
        assert "name cannot be empty" in str(exc_info.value)

    def test_name_trimming(self):
        """Test that names are trimmed of whitespace."""
        item = Item("  Magic Sword  ", ItemType.WEAPON)
        assert item.name == "Magic Sword"

    def test_all_item_types(self):
        """Test that items can be created with all item types."""
        weapon = Item("Sword", ItemType.WEAPON)
        assert weapon.item_type == ItemType.WEAPON

        armor = Item("Plate Mail", ItemType.ARMOR)
        assert armor.item_type == ItemType.ARMOR

        consumable = Item("Health Potion", ItemType.CONSUMABLE)
        assert consumable.item_type == ItemType.CONSUMABLE

        misc = Item("Key", ItemType.MISC)
        assert misc.item_type == ItemType.MISC

    def test_string_representation(self):
        """Test string representation of items."""
        item = Item("Healing Potion", ItemType.CONSUMABLE)
        assert str(item) == "Healing Potion (CONSUMABLE)"

    def test_repr_representation(self):
        """Test detailed representation of items."""
        item = Item("Magic Ring", ItemType.ARMOR)
        repr_str = repr(item)

        assert "Item" in repr_str
        assert "name='Magic Ring'" in repr_str
        assert "type=ARMOR" in repr_str
        assert item.item_id[:8] in repr_str  # First 8 chars of UUID

    def test_item_properties_are_readonly(self):
        """Test that item properties cannot be modified after creation."""
        item = Item("Sword", ItemType.WEAPON)

        # Properties should not have setters
        with pytest.raises(AttributeError):
            item.name = "New Name"  # type: ignore[misc]

        with pytest.raises(AttributeError):
            item.item_type = ItemType.ARMOR  # type: ignore[misc]

        with pytest.raises(AttributeError):
            item.item_id = "new-id"  # type: ignore[misc]
