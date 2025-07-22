"""Tests for escape mechanics."""

import pytest

from src.game.escape_mechanics import EscapeMechanics, Room, RoomType
from src.models.character import Character
from src.models.location import DungeonEntrance, SafeHaven, TowerEntrance


class TestRoom:
    """Tests for Room class."""

    def test_room_creation(self):
        """Test creating different room types."""
        normal_room = Room(RoomType.NORMAL)
        assert normal_room.room_type == RoomType.NORMAL
        assert not normal_room.is_boss_room()

        boss_room = Room(RoomType.BOSS)
        assert boss_room.room_type == RoomType.BOSS
        assert boss_room.is_boss_room()
        assert not boss_room.boss_defeated

    def test_boss_defeat(self):
        """Test boss defeat tracking."""
        boss_room = Room(RoomType.BOSS)
        assert not boss_room.boss_defeated

        boss_room.boss_defeated = True
        assert boss_room.boss_defeated


class TestEscapeMechanics:
    """Tests for escape mechanics system."""

    @pytest.fixture
    def escape_mechanics(self):
        """Create an EscapeMechanics instance."""
        return EscapeMechanics()

    @pytest.fixture
    def character(self):
        """Create a test character."""
        return Character("Test Hero", 10, 10)

    def test_can_use_escape_rope_in_dungeon(self, escape_mechanics):
        """Test escape rope works in dungeons."""
        dungeon = DungeonEntrance(
            position=(20, 20),
            name="Test Dungeon",
            min_level=1,
            max_level=9,
            floor_count=3,
        )
        escape_mechanics.enter_location(dungeon)

        can_use, reason = escape_mechanics.can_use_escape_rope()
        assert can_use is True
        assert reason == ""

    def test_cannot_escape_from_safe_haven(self, escape_mechanics):
        """Test escape rope doesn't work in Safe Haven."""
        safe_haven = SafeHaven()
        escape_mechanics.enter_location(safe_haven)

        can_use, reason = escape_mechanics.can_use_escape_rope()
        assert can_use is False
        assert "already in Safe Haven" in reason

    def test_cannot_escape_from_tower(self, escape_mechanics):
        """Test escape rope doesn't work in Tower."""
        tower = TowerEntrance()
        escape_mechanics.enter_location(tower)

        can_use, reason = escape_mechanics.can_use_escape_rope()
        assert can_use is False
        assert "Tower's magic prevents escape" in reason

    def test_boss_room_lock(self, escape_mechanics):
        """Test boss room prevents escape until defeated."""
        boss_room = Room(RoomType.BOSS)
        escape_mechanics.enter_room(boss_room)

        # Cannot escape while boss is alive
        can_use, reason = escape_mechanics.can_use_escape_rope()
        assert can_use is False
        assert "boss room is sealed" in reason
        assert escape_mechanics.boss_room_lock_active

        # Can escape after defeating boss
        escape_mechanics.defeat_boss()
        can_use, reason = escape_mechanics.can_use_escape_rope()
        assert can_use is True
        assert not escape_mechanics.boss_room_lock_active

    def test_normal_room_escape(self, escape_mechanics):
        """Test can escape from normal rooms."""
        normal_room = Room(RoomType.NORMAL)
        escape_mechanics.enter_room(normal_room)

        can_use, reason = escape_mechanics.can_use_escape_rope()
        assert can_use is True

    def test_return_to_safe_haven(self, escape_mechanics, character):
        """Test returning to Safe Haven."""
        dungeon = DungeonEntrance(
            position=(20, 20),
            name="Test Dungeon",
            min_level=1,
            max_level=9,
            floor_count=3,
        )
        escape_mechanics.enter_location(dungeon)

        success, message = escape_mechanics.return_to_safe_haven(character)
        assert success is True
        assert "return to Safe Haven" in message

    def test_cannot_return_from_boss_room(self, escape_mechanics, character):
        """Test cannot return while fighting boss."""
        boss_room = Room(RoomType.BOSS)
        escape_mechanics.enter_room(boss_room)

        success, message = escape_mechanics.return_to_safe_haven(character)
        assert success is False
        assert "boss room is sealed" in message

    def test_town_portal_follows_escape_rules(self, escape_mechanics):
        """Test town portal has same restrictions as escape rope."""
        # In dungeon - can use
        dungeon = DungeonEntrance(
            position=(20, 20),
            name="Test Dungeon",
            min_level=1,
            max_level=9,
            floor_count=3,
        )
        escape_mechanics.enter_location(dungeon)
        can_use, _ = escape_mechanics.can_use_town_portal()
        assert can_use is True

        # In boss room - cannot use
        boss_room = Room(RoomType.BOSS)
        escape_mechanics.enter_room(boss_room)
        can_use, _ = escape_mechanics.can_use_town_portal()
        assert can_use is False

    def test_teleport_restrictions(self, escape_mechanics):
        """Test teleportation restrictions."""
        # Create some locations
        safe_haven = SafeHaven()
        safe_haven.discovered = True

        dungeon = DungeonEntrance(
            position=(20, 20),
            name="Test Dungeon",
            min_level=1,
            max_level=9,
            floor_count=3,
        )
        dungeon.discovered = True

        tower = TowerEntrance()
        tower.discovered = True

        # Can teleport to Safe Haven
        can_tp, reason = escape_mechanics.can_teleport_to_location(safe_haven)
        assert can_tp is True

        # Cannot teleport to dungeons
        can_tp, reason = escape_mechanics.can_teleport_to_location(dungeon)
        assert can_tp is False
        assert "Cannot teleport directly into dungeons" in reason

        # Cannot teleport to Tower
        can_tp, reason = escape_mechanics.can_teleport_to_location(tower)
        assert can_tp is False
        assert "Tower's magic blocks teleportation" in reason

    def test_cannot_teleport_to_undiscovered(self, escape_mechanics):
        """Test cannot teleport to undiscovered locations."""
        dungeon = DungeonEntrance(
            position=(20, 20),
            name="Hidden Dungeon",
            min_level=1,
            max_level=9,
            floor_count=3,
        )
        dungeon.discovered = False

        can_tp, reason = escape_mechanics.can_teleport_to_location(dungeon)
        assert can_tp is False
        assert "undiscovered locations" in reason

    def test_cannot_teleport_during_boss_fight(self, escape_mechanics):
        """Test teleportation blocked during boss fights."""
        boss_room = Room(RoomType.BOSS)
        escape_mechanics.enter_room(boss_room)

        safe_haven = SafeHaven()
        can_tp, reason = escape_mechanics.can_teleport_to_location(safe_haven)
        assert can_tp is False
        assert "during boss fight" in reason

    def test_escape_cost(self, escape_mechanics):
        """Test escape cost calculation."""
        # Currently always free with escape rope
        cost = escape_mechanics.get_escape_cost()
        assert cost == 0

        # Even in dungeons
        dungeon = DungeonEntrance(
            position=(20, 20),
            name="Test Dungeon",
            min_level=1,
            max_level=9,
            floor_count=3,
        )
        escape_mechanics.enter_location(dungeon)
        cost = escape_mechanics.get_escape_cost()
        assert cost == 0
