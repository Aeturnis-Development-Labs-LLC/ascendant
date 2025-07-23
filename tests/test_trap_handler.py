"""Tests for trap handler following UTF contract GAME-COMBAT-006.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.2 Combat System Implementation
"""

from unittest.mock import MagicMock

from src.game.trap_handler import TrapHandler, TrapResult
from src.models.character import Character
from src.models.trap import Trap, TrapType


class TestTrapHandler:
    """Test cases for trap handler (GAME-COMBAT-006)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.trap_handler = TrapHandler()

        # Create test character
        self.character = Character("Hero", 5, 5)
        self.character.hp = 20
        self.character.hp_max = 20

        # Create test traps
        self.spike_trap = Trap(3, 3, TrapType.SPIKE, damage=5, floor_level=1)
        self.poison_trap = Trap(4, 4, TrapType.POISON, damage=3, floor_level=1)
        self.alarm_trap = Trap(5, 5, TrapType.ALARM, damage=0, floor_level=1)

    def test_spike_trap_damage(self):
        """Test spike trap deals direct damage (GAME-COMBAT-006)."""
        # Mock combat log
        self.trap_handler.combat_log = MagicMock()

        result = self.trap_handler.handle_trap(self.character, self.spike_trap)

        assert result is not None
        assert result.trap_type == TrapType.SPIKE
        assert result.damage_dealt == 5
        assert result.status_applied is None
        assert result.trap_disarmed is True
        assert self.character.hp == 15  # 20 - 5

        # Verify combat log called
        self.trap_handler.combat_log.add_message.assert_called()

    def test_poison_trap_damage_and_status(self):
        """Test poison trap deals damage and applies status (GAME-COMBAT-006)."""
        # Mock combat log
        self.trap_handler.combat_log = MagicMock()

        # Mock status application
        self.character.apply_status = MagicMock()

        result = self.trap_handler.handle_trap(self.character, self.poison_trap)

        assert result is not None
        assert result.trap_type == TrapType.POISON
        assert result.damage_dealt == 3
        assert result.status_applied == "poisoned"
        assert result.trap_disarmed is True
        assert self.character.hp == 17  # 20 - 3

        # Verify status applied
        self.character.apply_status.assert_called_once_with("poisoned", duration=3)

    def test_alarm_trap_no_damage(self):
        """Test alarm trap triggers alert without damage (GAME-COMBAT-006)."""
        # Mock combat log
        self.trap_handler.combat_log = MagicMock()

        result = self.trap_handler.handle_trap(self.character, self.alarm_trap)

        assert result is not None
        assert result.trap_type == TrapType.ALARM
        assert result.damage_dealt == 0
        assert result.status_applied is None
        assert result.trap_disarmed is True
        assert result.alert_radius == 10
        assert self.character.hp == 20  # No damage

    def test_trap_disarms_after_trigger(self):
        """Test trap is disarmed after triggering (GAME-COMBAT-006)."""
        assert self.spike_trap.triggered is False

        self.trap_handler.handle_trap(self.character, self.spike_trap)

        assert self.spike_trap.triggered is True

        # Second trigger returns None
        result = self.trap_handler.handle_trap(self.character, self.spike_trap)
        assert result is None

    def test_scaled_trap_damage(self):
        """Test trap damage scales with floor level."""
        # Create scaled trap (floor 5)
        scaled_trap = Trap.create_scaled(6, 6, TrapType.SPIKE, floor_level=5)

        # Base damage 5 + (5-1)//2 = 5 + 2 = 7
        assert scaled_trap.damage == 7

        result = self.trap_handler.handle_trap(self.character, scaled_trap)

        assert result.damage_dealt == 7
        assert self.character.hp == 13  # 20 - 7

    def test_trap_result_object(self):
        """Test TrapResult data structure."""
        result = TrapResult(
            trap_type=TrapType.SPIKE,
            damage_dealt=5,
            status_applied=None,
            trap_disarmed=True,
            alert_radius=0,
        )

        assert result.trap_type == TrapType.SPIKE
        assert result.damage_dealt == 5
        assert result.status_applied is None
        assert result.trap_disarmed is True
        assert result.alert_radius == 0

    def test_character_death_from_trap(self):
        """Test character can die from trap damage."""
        self.character.hp = 3  # Low HP

        result = self.trap_handler.handle_trap(self.character, self.spike_trap)

        assert result is not None
        assert self.character.hp == 0
        assert not self.character.is_alive()

    def test_trap_damage_minimum(self):
        """Test trap damage cannot reduce HP below 0."""
        self.character.hp = 2  # Low HP

        self.trap_handler.handle_trap(self.character, self.spike_trap)

        assert self.character.hp == 0  # Not negative

    def test_utf_contract_game_combat_006(self):
        """Verify UTF contract GAME-COMBAT-006: Trap Damage."""
        # Test all trap types
        traps = [
            (self.spike_trap, 5, None),
            (self.poison_trap, 3, "poisoned"),
            (self.alarm_trap, 0, None),
        ]

        for trap, expected_damage, expected_status in traps:
            # Reset character
            self.character.hp = 20
            if hasattr(self.character, "apply_status"):
                self.character.apply_status = MagicMock()

            # Trigger trap
            result = self.trap_handler.handle_trap(self.character, trap)

            # Verify damage appropriate to trap type
            assert result.damage_dealt == expected_damage

            # Verify status effects
            if expected_status:
                assert result.status_applied == expected_status

            # Verify trap disarmed
            assert trap.triggered is True
