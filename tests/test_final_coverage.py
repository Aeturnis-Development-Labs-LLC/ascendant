"""Final tests to reach 90% coverage."""

import pytest

from src.enums import (
    ActionType,
    Direction,
    EntityType,
    ItemType,
    LocationType,
    MonsterType,
    TerrainType,
    TileType,
)
from src.game.death_handler import DeathHandler
from src.game.trap_handler import TrapHandler
from src.models.ability import Ability
from src.models.character import Character
from src.models.floor import Floor
from src.models.monster import AIBehavior, Monster


class TestEnumsCoverage:
    """Test enum string representations."""

    def test_all_enum_str_methods(self):
        """Test string methods for all enums."""
        # These enums have custom __str__ methods
        assert str(TileType.FLOOR) == "FLOOR"
        assert str(Direction.NORTH) == "NORTH"
        assert str(ItemType.WEAPON) == "WEAPON"
        assert str(EntityType.PLAYER) == "PLAYER"
        assert str(ActionType.MOVE) == "MOVE"
        assert str(TerrainType.PLAINS) == "PLAINS"
        assert str(LocationType.SAFE_HAVEN) == "SAFE_HAVEN"
        assert str(MonsterType.GOBLIN) == "GOBLIN"


class TestDeathHandlerCoverage:
    """Test death handler initialization."""

    def test_death_handler_init(self):
        """Test DeathHandler can be initialized."""
        from src.game.combat_log import CombatLog

        log = CombatLog()
        handler = DeathHandler(log)
        assert handler.combat_log == log


class TestTrapHandlerCoverage:
    """Test trap handler initialization."""

    def test_trap_handler_init(self):
        """Test TrapHandler can be initialized."""
        from src.game.combat_log import CombatLog

        log = CombatLog()
        handler = TrapHandler(log)
        assert handler.combat_log == log


class TestAbilityCoverage:
    """Test ability initialization."""

    def test_ability_creation(self):
        """Test creating abilities."""
        from src.models.ability import Ability

        ability = Ability(
            name="Test Strike",
            description="A test ability",
            cooldown_duration=3,
            stamina_cost=10,
            damage_multiplier=1.5,
        )

        assert ability.name == "Test Strike"
        assert ability.cooldown_duration == 3
        assert ability.stamina_cost == 10
        assert ability.damage_multiplier == 1.5
        assert ability.effect is None


class TestFloorCoverage:
    """Additional floor tests."""

    def test_floor_random_seed(self):
        """Test floor with random seed."""
        # This should generate a random seed internally
        floor = Floor()
        assert floor._seed is not None
        assert floor.width == 50
        assert floor.height == 50

    def test_floor_fog_of_war_methods(self):
        """Test fog of war methods."""
        floor = Floor(seed=42)
        floor.generate()

        # Mark some tiles as seen
        floor.mark_as_seen(10, 10)
        assert floor.is_seen(10, 10) is True

        # Check unseen tile
        assert floor.is_seen(40, 40) is False


class TestMonsterCoverage:
    """Additional monster tests."""

    def test_monster_validation_errors(self):
        """Test monster parameter validation."""
        # Test negative HP
        with pytest.raises(ValueError, match="HP cannot be negative"):
            Monster(5, 5, "Bad", "B", -5, 10, 5, 5, MonsterType.RAT, AIBehavior.PASSIVE)

        # Test zero max HP
        with pytest.raises(ValueError, match="Max HP must be positive"):
            Monster(5, 5, "Bad", "B", 10, 0, 5, 5, MonsterType.RAT, AIBehavior.PASSIVE)

        # Test negative attack
        with pytest.raises(ValueError, match="Attack cannot be negative"):
            Monster(5, 5, "Bad", "B", 10, 10, -5, 5, MonsterType.RAT, AIBehavior.PASSIVE)

        # Test negative defense
        with pytest.raises(ValueError, match="Defense cannot be negative"):
            Monster(5, 5, "Bad", "B", 10, 10, 5, -5, MonsterType.RAT, AIBehavior.PASSIVE)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
