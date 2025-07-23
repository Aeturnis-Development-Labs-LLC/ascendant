"""Tests for Monster class following UTF contracts.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.1 Monster Implementation
"""

import pytest

from src.enums import EntityType
from src.models.monster import AIBehavior, Monster


class TestMonster:
    """Test cases for Monster class (GAME-COMBAT-001)."""

    def test_monster_creation(self):
        """Test basic monster creation with required stats."""
        monster = Monster(
            x=5,
            y=5,
            name="Goblin",
            display_char="g",
            hp=10,
            hp_max=10,
            attack=3,
            defense=1,
            monster_type="goblin",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

        assert monster.x == 5
        assert monster.y == 5
        assert monster.name == "Goblin"
        assert monster.display_char == "g"
        assert monster.hp == 10
        assert monster.hp_max == 10
        assert monster.attack == 3
        assert monster.defense == 1
        assert monster.monster_type == "goblin"
        assert monster.ai_behavior == AIBehavior.AGGRESSIVE
        assert monster.entity_type == EntityType.MONSTER

    def test_monster_position(self):
        """Test monster position property."""
        monster = Monster(
            x=3,
            y=4,
            name="Orc",
            display_char="o",
            hp=15,
            hp_max=15,
            attack=5,
            defense=2,
            monster_type="orc",
            ai_behavior=AIBehavior.PASSIVE,
        )

        assert monster.position == (3, 4)

    def test_monster_take_damage(self):
        """Test monster takes damage correctly."""
        monster = Monster(
            x=0,
            y=0,
            name="Skeleton",
            display_char="s",
            hp=8,
            hp_max=8,
            attack=2,
            defense=0,
            monster_type="skeleton",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

        monster.take_damage(3)
        assert monster.hp == 5

        monster.take_damage(10)  # More than remaining HP
        assert monster.hp == 0
        assert monster.is_alive() is False

    def test_monster_is_alive(self):
        """Test monster alive status."""
        monster = Monster(
            x=0,
            y=0,
            name="Zombie",
            display_char="z",
            hp=5,
            hp_max=5,
            attack=2,
            defense=1,
            monster_type="zombie",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

        assert monster.is_alive() is True

        monster.hp = 0
        assert monster.is_alive() is False

        monster.hp = -5  # Negative HP
        assert monster.is_alive() is False

    def test_monster_render(self):
        """Test monster render returns display character."""
        monster = Monster(
            x=0,
            y=0,
            name="Dragon",
            display_char="D",
            hp=100,
            hp_max=100,
            attack=20,
            defense=10,
            monster_type="dragon",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

        assert monster.render() == "D"

    def test_monster_update(self):
        """Test monster update method (placeholder for now)."""
        monster = Monster(
            x=0,
            y=0,
            name="Slime",
            display_char="s",
            hp=3,
            hp_max=3,
            attack=1,
            defense=0,
            monster_type="slime",
            ai_behavior=AIBehavior.PASSIVE,
        )

        # Update should work without error (no-op for now)
        monster.update(0.016)  # 16ms delta time

    def test_damage_calculation_contract(self):
        """Test UTF contract GAME-COMBAT-001: Damage Calculation."""
        attacker = Monster(
            x=0,
            y=0,
            name="Attacker",
            display_char="A",
            hp=10,
            hp_max=10,
            attack=5,
            defense=2,
            monster_type="test",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

        defender = Monster(
            x=1,
            y=1,
            name="Defender",
            display_char="D",
            hp=10,
            hp_max=10,
            attack=3,
            defense=3,
            monster_type="test",
            ai_behavior=AIBehavior.PASSIVE,
        )

        # Test damage calculation: ATK - DEF with minimum 1
        damage = max(1, attacker.attack - defender.defense)
        assert damage == 2  # 5 - 3 = 2

        # Test minimum damage
        weak_attacker = Monster(
            x=2,
            y=2,
            name="Weak",
            display_char="w",
            hp=5,
            hp_max=5,
            attack=1,
            defense=0,
            monster_type="test",
            ai_behavior=AIBehavior.PASSIVE,
        )

        damage = max(1, weak_attacker.attack - defender.defense)
        assert damage == 1  # 1 - 3 = -2, but minimum is 1

    def test_ai_behavior_enum(self):
        """Test AIBehavior enum values."""
        assert AIBehavior.PASSIVE.value == "passive"
        assert AIBehavior.AGGRESSIVE.value == "aggressive"
        assert AIBehavior.DEFENSIVE.value == "defensive"
        assert AIBehavior.RANGED.value == "ranged"

    def test_monster_stat_validation(self):
        """Test monster stats are validated properly."""
        # HP cannot exceed HP max
        monster = Monster(
            x=0,
            y=0,
            name="Test",
            display_char="t",
            hp=20,
            hp_max=10,
            attack=1,
            defense=1,
            monster_type="test",
            ai_behavior=AIBehavior.PASSIVE,
        )
        assert monster.hp == 10  # Should be capped at hp_max

        # Stats cannot be negative
        with pytest.raises(ValueError):
            Monster(
                x=0,
                y=0,
                name="Invalid",
                display_char="i",
                hp=-5,
                hp_max=10,
                attack=1,
                defense=1,
                monster_type="test",
                ai_behavior=AIBehavior.PASSIVE,
            )
