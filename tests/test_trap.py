"""Tests for Trap class following UTF contract GAME-COMBAT-006.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.1 Monster Implementation
"""

from unittest.mock import MagicMock

import pytest

from src.models.character import Character
from src.models.trap import Trap, TrapType


class TestTrap:
    """Test cases for Trap class (GAME-COMBAT-006)."""

    def test_trap_creation(self):
        """Test basic trap creation."""
        trap = Trap(x=5, y=5, trap_type=TrapType.SPIKE, damage=5, floor_level=1)

        assert trap.x == 5
        assert trap.y == 5
        assert trap.trap_type == TrapType.SPIKE
        assert trap.damage == 5
        assert trap.floor_level == 1
        assert trap.triggered is False
        assert trap.position == (5, 5)

    def test_trap_types(self):
        """Test all trap type enums."""
        assert TrapType.SPIKE.value == "spike"
        assert TrapType.POISON.value == "poison"
        assert TrapType.ALARM.value == "alarm"

    def test_spike_trap_trigger(self):
        """Test spike trap deals direct damage."""
        trap = Trap(x=0, y=0, trap_type=TrapType.SPIKE, damage=10, floor_level=1)
        character = MagicMock(spec=Character)
        character.hp = 20
        character.take_damage = MagicMock()

        result = trap.trigger(character)

        assert trap.triggered is True
        assert result["damage"] == 10
        assert result["effect"] == "spike_damage"
        character.take_damage.assert_called_once_with(10)

    def test_poison_trap_trigger(self):
        """Test poison trap deals damage and applies effect."""
        trap = Trap(x=0, y=0, trap_type=TrapType.POISON, damage=5, floor_level=2)
        character = MagicMock(spec=Character)
        character.hp = 15
        character.take_damage = MagicMock()
        character.apply_status = MagicMock()

        result = trap.trigger(character)

        assert trap.triggered is True
        assert result["damage"] == 5
        assert result["effect"] == "poisoned"
        character.take_damage.assert_called_once_with(5)
        character.apply_status.assert_called_once_with("poisoned", duration=3)

    def test_alarm_trap_trigger(self):
        """Test alarm trap alerts nearby monsters."""
        trap = Trap(x=5, y=5, trap_type=TrapType.ALARM, damage=0, floor_level=1)
        character = MagicMock(spec=Character)

        result = trap.trigger(character)

        assert trap.triggered is True
        assert result["damage"] == 0
        assert result["effect"] == "alarm_triggered"
        assert result["alert_radius"] == 10
        assert result["alert_position"] == (5, 5)

    def test_trap_cannot_trigger_twice(self):
        """Test trap only triggers once."""
        trap = Trap(x=0, y=0, trap_type=TrapType.SPIKE, damage=5, floor_level=1)
        character = MagicMock(spec=Character)
        character.take_damage = MagicMock()

        # First trigger
        result1 = trap.trigger(character)
        assert result1 is not None
        assert trap.triggered is True
        character.take_damage.assert_called_once()

        # Second trigger should do nothing
        result2 = trap.trigger(character)
        assert result2 is None
        assert character.take_damage.call_count == 1  # Not called again

    def test_trap_damage_scaling(self):
        """Test trap damage scales with floor level."""
        # Floor 1 trap
        trap1 = Trap.create_scaled(x=0, y=0, trap_type=TrapType.SPIKE, floor_level=1)
        assert trap1.damage == 5  # Base damage

        # Floor 5 trap
        trap5 = Trap.create_scaled(x=0, y=0, trap_type=TrapType.SPIKE, floor_level=5)
        assert trap5.damage == 7  # 5 + (5-1)//2 = 7

        # Floor 10 trap
        trap10 = Trap.create_scaled(x=0, y=0, trap_type=TrapType.SPIKE, floor_level=10)
        assert trap10.damage == 9  # 5 + (10-1)//2 = 9

        # Poison trap scaling (less damage)
        poison5 = Trap.create_scaled(x=0, y=0, trap_type=TrapType.POISON, floor_level=5)
        assert poison5.damage == 5  # 3 + (5-1)//2 = 5

    def test_trap_render(self):
        """Test trap render display."""
        spike = Trap(x=0, y=0, trap_type=TrapType.SPIKE, damage=5, floor_level=1)
        assert spike.render() == "^"

        poison = Trap(x=0, y=0, trap_type=TrapType.POISON, damage=3, floor_level=1)
        assert poison.render() == "~"

        alarm = Trap(x=0, y=0, trap_type=TrapType.ALARM, damage=0, floor_level=1)
        assert alarm.render() == "!"

        # Triggered traps show differently
        spike.triggered = True
        assert spike.render() == "."

    def test_trap_description(self):
        """Test trap description generation."""
        spike = Trap(x=0, y=0, trap_type=TrapType.SPIKE, damage=5, floor_level=1)
        assert spike.description() == "A spike trap (5 damage)"

        poison = Trap(x=0, y=0, trap_type=TrapType.POISON, damage=3, floor_level=1)
        assert poison.description() == "A poison gas trap (3 damage + poison)"

        alarm = Trap(x=0, y=0, trap_type=TrapType.ALARM, damage=0, floor_level=1)
        assert alarm.description() == "An alarm trap (alerts monsters)"

        spike.triggered = True
        assert spike.description() == "A triggered spike trap"

    def test_utf_contract_game_combat_006(self):
        """Verify UTF contract GAME-COMBAT-006 compliance."""
        # Given: Character on trap tile
        trap = Trap(x=3, y=3, trap_type=TrapType.SPIKE, damage=8, floor_level=2)
        character = MagicMock(spec=Character)
        character.position = (3, 3)
        character.take_damage = MagicMock()

        # When: Trap is triggered
        result = trap.trigger(character)

        # Then: Damage dealt, effects applied, trap disarms
        assert result["damage"] == 8
        character.take_damage.assert_called_with(8)
        assert trap.triggered is True  # Trap disarmed

        # Verify appropriate damage for trap type
        if trap.trap_type in [TrapType.SPIKE, TrapType.POISON]:
            assert result["damage"] > 0

        # Alarm traps don't deal damage
        alarm = Trap(x=0, y=0, trap_type=TrapType.ALARM, damage=0, floor_level=1)
        alarm_result = alarm.trigger(character)
        assert alarm_result["damage"] == 0
