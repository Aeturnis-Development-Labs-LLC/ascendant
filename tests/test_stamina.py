"""Tests for stamina system - UTF Contracts GAME-MOVE-003, GAME-MOVE-004."""

from src.enums import ActionType
from src.game.stamina_system import StaminaSystem
from src.models.character import Character


class TestCharacterStamina:
    """Tests for Character stamina management."""

    def test_stamina_initial_values(self):
        """Test that character starts with full stamina."""
        char = Character("Hero", 5, 5)
        assert char.stamina == 100
        assert char.stamina_max == 100

    def test_perform_action_reduces_stamina(self):
        """Test that actions reduce stamina correctly."""
        char = Character("Hero", 5, 5)

        # Move action
        result = char.perform_action(ActionType.MOVE, 10)
        assert result is True
        assert char.stamina == 90

        # Attack action
        result = char.perform_action(ActionType.ATTACK, 15)
        assert result is True
        assert char.stamina == 75

    def test_insufficient_stamina_blocks_action(self):
        """Test that actions fail when insufficient stamina."""
        char = Character("Hero", 5, 5)
        char.stamina = 5

        # Try to move (costs 10)
        result = char.perform_action(ActionType.MOVE, 10)
        assert result is False
        assert char.stamina == 5  # Unchanged

    def test_stamina_never_negative(self):
        """Test that stamina cannot go below 0."""
        char = Character("Hero", 5, 5)
        char.stamina = 5

        # Force stamina reduction
        char._stamina = -10
        assert char.stamina == 0

    def test_stamina_never_exceeds_max(self):
        """Test that stamina cannot exceed maximum."""
        char = Character("Hero", 5, 5)

        # Try to set above max
        char.stamina = 150
        assert char.stamina == 100


class TestStaminaSystem:
    """Tests for StaminaSystem class."""

    def test_action_costs(self):
        """Test that action costs are defined correctly."""
        assert StaminaSystem.get_action_cost(ActionType.MOVE) == 10
        assert StaminaSystem.get_action_cost(ActionType.ATTACK) == 15
        assert StaminaSystem.get_action_cost(ActionType.USE_ITEM) == 10
        assert StaminaSystem.get_action_cost(ActionType.CAST_SPELL) >= 20
        assert StaminaSystem.get_action_cost(ActionType.CAST_SPELL) <= 50
        assert StaminaSystem.get_action_cost(ActionType.WAIT) == -20

    def test_can_perform_action(self):
        """Test checking if action can be performed."""
        char = Character("Hero", 5, 5)

        # Full stamina - can do anything
        assert StaminaSystem.can_perform_action(char, ActionType.MOVE) is True
        assert StaminaSystem.can_perform_action(char, ActionType.ATTACK) is True

        # Low stamina
        char.stamina = 5
        assert StaminaSystem.can_perform_action(char, ActionType.MOVE) is False
        assert StaminaSystem.can_perform_action(char, ActionType.WAIT) is True

    def test_execute_action(self):
        """Test executing actions through stamina system."""
        char = Character("Hero", 5, 5)

        # Successful move
        result = StaminaSystem.execute_action(char, ActionType.MOVE)
        assert result is True
        assert char.stamina == 90

        # Successful wait (regenerates)
        result = StaminaSystem.execute_action(char, ActionType.WAIT)
        assert result is True
        assert char.stamina == 100  # 90 + 20 = 110, capped at 100

    def test_regenerate_stamina(self):
        """Test stamina regeneration over turns."""
        char = Character("Hero", 5, 5)
        char.stamina = 50

        # Regenerate 1 turn
        StaminaSystem.regenerate(char, 1)
        assert char.stamina == 55  # +5 per turn

        # Regenerate 5 turns
        StaminaSystem.regenerate(char, 5)
        assert char.stamina == 80  # 55 + 25

        # Regenerate with cap
        StaminaSystem.regenerate(char, 10)
        assert char.stamina == 100  # Capped at max

    def test_force_wait_when_exhausted(self):
        """Test forced wait when stamina too low."""
        char = Character("Hero", 5, 5)
        char.stamina = 5

        # Should force wait
        action_taken = StaminaSystem.force_wait_if_exhausted(char)
        assert action_taken is True
        assert char.stamina == 25  # 5 + 20 from wait

        # Should not force wait when sufficient stamina
        action_taken = StaminaSystem.force_wait_if_exhausted(char)
        assert action_taken is False
        assert char.stamina == 25  # Unchanged

    def test_spell_cost_variation(self):
        """Test that spell costs vary within range."""
        costs = set()
        for _ in range(20):
            cost = StaminaSystem.get_action_cost(ActionType.CAST_SPELL)
            costs.add(cost)
            assert 20 <= cost <= 50

        # Should have some variation
        assert len(costs) > 1

    def test_wait_action_regeneration(self):
        """Test that wait action properly regenerates stamina."""
        char = Character("Hero", 5, 5)
        char.stamina = 30

        # Execute wait
        result = StaminaSystem.execute_action(char, ActionType.WAIT)
        assert result is True
        assert char.stamina == 50  # 30 + 20

    def test_stamina_display_percentage(self):
        """Test stamina percentage calculation."""
        char = Character("Hero", 5, 5)

        assert StaminaSystem.get_stamina_percentage(char) == 100

        char.stamina = 50
        assert StaminaSystem.get_stamina_percentage(char) == 50

        char.stamina = 0
        assert StaminaSystem.get_stamina_percentage(char) == 0


class TestStaminaIntegration:
    """Integration tests for stamina system."""

    def test_full_action_sequence(self):
        """Test a complete sequence of actions."""
        char = Character("Hero", 5, 5)

        # Move 3 times
        for _ in range(3):
            assert StaminaSystem.execute_action(char, ActionType.MOVE) is True
        assert char.stamina == 70

        # Attack twice
        for _ in range(2):
            assert StaminaSystem.execute_action(char, ActionType.ATTACK) is True
        assert char.stamina == 40

        # Cast spell - try to cast, it may succeed or fail based on random cost
        initial_stamina = char.stamina
        result = StaminaSystem.execute_action(char, ActionType.CAST_SPELL)
        
        # If it succeeded, stamina should have decreased
        if result:
            assert char.stamina < initial_stamina
            assert char.stamina >= 0
        else:
            # If it failed, stamina should be unchanged
            assert char.stamina == initial_stamina

        # Wait to recover
        stamina_before_wait = char.stamina
        assert StaminaSystem.execute_action(char, ActionType.WAIT) is True
        # Wait regenerates 20 stamina, capped at 100
        expected_stamina = min(stamina_before_wait + 20, 100)
        assert char.stamina == expected_stamina

    def test_exhaustion_recovery_cycle(self):
        """Test exhaustion and recovery cycle."""
        char = Character("Hero", 5, 5)

        # Exhaust stamina
        while char.stamina >= 10:
            StaminaSystem.execute_action(char, ActionType.MOVE)

        assert char.stamina < 10
        old_stamina = char.stamina

        # Force wait should trigger
        assert StaminaSystem.force_wait_if_exhausted(char) is True
        assert char.stamina > old_stamina

    def test_stamina_ui_states(self):
        """Test stamina states for UI display."""
        char = Character("Hero", 5, 5)

        # Full stamina
        assert StaminaSystem.get_stamina_state(char) == "FULL"

        # High stamina
        char.stamina = 75
        assert StaminaSystem.get_stamina_state(char) == "HIGH"

        # Medium stamina
        char.stamina = 50
        assert StaminaSystem.get_stamina_state(char) == "MEDIUM"

        # Low stamina
        char.stamina = 25
        assert StaminaSystem.get_stamina_state(char) == "LOW"

        # Critical stamina
        char.stamina = 10
        assert StaminaSystem.get_stamina_state(char) == "CRITICAL"

        # Exhausted
        char.stamina = 0
        assert StaminaSystem.get_stamina_state(char) == "EXHAUSTED"

    def test_performance(self):
        """Test stamina system performance."""
        import time

        char = Character("Hero", 5, 5)

        start = time.time()
        # Perform 10000 stamina operations
        for _ in range(10000):
            StaminaSystem.can_perform_action(char, ActionType.MOVE)
            StaminaSystem.get_stamina_percentage(char)
            StaminaSystem.get_stamina_state(char)
        elapsed = time.time() - start

        # Should be very fast
        assert elapsed < 0.1  # 100ms for 10000 operations
