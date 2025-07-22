"""Tests for Entity base class - UTF Contract GAME-CORE-004."""

import pytest

from src.enums import EntityType
from src.models.entity import Entity


# Create concrete Entity subclasses for testing
class MockPlayer(Entity):
    """Concrete player entity for testing."""
    
    def update(self) -> None:
        """Update implementation."""
        self.updated = True

    def render(self) -> str:
        """Render implementation."""
        return "@"


class MockMonster(Entity):
    """Concrete monster entity for testing."""
    
    def update(self) -> None:
        """Update implementation."""
        self.health = getattr(self, "health", 100) - 1

    def render(self) -> str:
        """Render implementation."""
        return "M"


class TestEntity:
    """Tests for Entity abstract base class."""

    def test_entity_cannot_be_instantiated(self):
        """Test that Entity is abstract and cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            Entity((0, 0), EntityType.PLAYER)  # type: ignore[abstract]

        assert "Can't instantiate abstract class" in str(exc_info.value)

    def test_concrete_entity_creation(self):
        """Test that concrete entities can be created."""
        player = MockPlayer((5, 10), EntityType.PLAYER)
        assert player.position == (5, 10)
        assert player.x == 5
        assert player.y == 10
        assert player.entity_type == EntityType.PLAYER
        assert player.entity_id is not None

    def test_position_immutability(self):
        """Test that entity position cannot be modified."""
        player = MockPlayer((3, 4), EntityType.PLAYER)

        # Position tuple is immutable
        with pytest.raises(AttributeError):
            player.position = (5, 6)  # type: ignore[misc]

        # Individual coordinates cannot be set
        with pytest.raises(AttributeError):
            player.x = 5  # type: ignore[misc]

        with pytest.raises(AttributeError):
            player.y = 6  # type: ignore[misc]

    def test_entity_id_generation(self):
        """Test that entity IDs are automatically generated."""
        player1 = MockPlayer((0, 0), EntityType.PLAYER)
        player2 = MockPlayer((0, 0), EntityType.PLAYER)

        # IDs should be unique
        assert player1.entity_id != player2.entity_id

        # IDs should be valid UUIDs (36 characters with hyphens)
        assert len(player1.entity_id) == 36
        assert player1.entity_id.count("-") == 4

    def test_entity_id_provided(self):
        """Test that custom entity IDs can be provided."""
        custom_id = "custom-entity-id-123"
        player = MockPlayer((0, 0), EntityType.PLAYER, entity_id=custom_id)
        assert player.entity_id == custom_id

    def test_abstract_methods_must_be_implemented(self):
        """Test that subclasses must implement abstract methods."""

        # Create a class that doesn't implement abstract methods
        class IncompleteEntity(Entity):
            pass

        with pytest.raises(TypeError) as exc_info:
            IncompleteEntity((0, 0), EntityType.NPC)  # type: ignore[abstract]

        error_msg = str(exc_info.value)
        assert "Can't instantiate abstract class" in error_msg
        assert "update" in error_msg or "render" in error_msg

    def test_update_method_implementation(self):
        """Test that update method works in concrete classes."""
        player = MockPlayer((0, 0), EntityType.PLAYER)
        player.update()
        assert hasattr(player, "updated") and player.updated

        monster = MockMonster((0, 0), EntityType.MONSTER)
        monster.update()
        assert monster.health == 99

    def test_render_method_implementation(self):
        """Test that render method works in concrete classes."""
        player = MockPlayer((0, 0), EntityType.PLAYER)
        assert player.render() == "@"

        monster = MockMonster((0, 0), EntityType.MONSTER)
        assert monster.render() == "M"

    def test_entity_type_property(self):
        """Test that entity type is properly stored."""
        player = MockPlayer((0, 0), EntityType.PLAYER)
        assert player.entity_type == EntityType.PLAYER

        monster = MockMonster((0, 0), EntityType.MONSTER)
        assert monster.entity_type == EntityType.MONSTER

    def test_string_representation(self):
        """Test string representations of entities."""
        player = MockPlayer((3, 4), EntityType.PLAYER)
        assert str(player) == "MockPlayer(3, 4)"

        # Test repr
        repr_str = repr(player)
        assert "MockPlayer" in repr_str
        assert "position=(3, 4)" in repr_str
        assert "type=PLAYER" in repr_str
        assert player.entity_id[:8] in repr_str  # First 8 chars of UUID
