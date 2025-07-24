"""Tests for ability system following UTF contract GAME-COMBAT-005.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.3 Player Combat Integration
"""

from unittest.mock import MagicMock

from src.models.ability import Ability


class TestAbility:
    """Test cases for ability system (GAME-COMBAT-005)."""

    def test_ability_creation(self) -> None:
        """Test creating an ability with all fields."""
        ability = Ability(
            name="Power Strike",
            description="A powerful attack that deals double damage",
            cooldown_duration=3,
            stamina_cost=20,
            damage_multiplier=2.0,
        )

        assert ability.name == "Power Strike"
        assert ability.description == "A powerful attack that deals double damage"
        assert ability.cooldown_duration == 3
        assert ability.stamina_cost == 20
        assert ability.damage_multiplier == 2.0
        assert ability.effect is None

    def test_ability_with_effect(self) -> None:
        """Test creating an ability with a custom effect."""
        mock_effect = MagicMock()

        ability = Ability(
            name="Stun Strike",
            description="Stuns the target",
            cooldown_duration=5,
            stamina_cost=30,
            effect=mock_effect,
        )

        assert ability.effect is not None
        assert ability.effect == mock_effect

    def test_can_use_with_no_cooldown_and_enough_stamina(self) -> None:
        """Test ability can be used when cooldown is 0 and stamina sufficient."""
        ability = Ability(
            name="Quick Attack",
            description="A fast attack",
            cooldown_duration=1,
            stamina_cost=10,
        )

        # No cooldown, enough stamina
        assert ability.can_use(current_cooldown=0, current_stamina=20) is True

    def test_cannot_use_during_cooldown(self) -> None:
        """Test ability cannot be used when on cooldown (GAME-COMBAT-005)."""
        ability = Ability(
            name="Heavy Strike",
            description="A heavy attack",
            cooldown_duration=3,
            stamina_cost=15,
        )

        # On cooldown (2 turns remaining)
        assert ability.can_use(current_cooldown=2, current_stamina=50) is False

        # On cooldown (1 turn remaining)
        assert ability.can_use(current_cooldown=1, current_stamina=50) is False

    def test_cannot_use_with_insufficient_stamina(self) -> None:
        """Test ability cannot be used without enough stamina."""
        ability = Ability(
            name="Draining Strike",
            description="Uses lots of stamina",
            cooldown_duration=2,
            stamina_cost=30,
        )

        # Not enough stamina
        assert ability.can_use(current_cooldown=0, current_stamina=20) is False

        # Exactly enough stamina
        assert ability.can_use(current_cooldown=0, current_stamina=30) is True

    def test_cannot_use_with_both_cooldown_and_low_stamina(self) -> None:
        """Test ability blocked by both cooldown and stamina."""
        ability = Ability(
            name="Ultimate Attack",
            description="The ultimate technique",
            cooldown_duration=10,
            stamina_cost=50,
        )

        # Both cooldown and insufficient stamina
        assert ability.can_use(current_cooldown=5, current_stamina=10) is False

    def test_default_damage_multiplier(self) -> None:
        """Test default damage multiplier is 1.0."""
        ability = Ability(
            name="Basic Strike",
            description="A basic attack",
            cooldown_duration=0,
            stamina_cost=5,
        )

        assert ability.damage_multiplier == 1.0

    def test_zero_cooldown_ability(self) -> None:
        """Test ability with no cooldown can always be used (with stamina)."""
        ability = Ability(
            name="Basic Attack",
            description="No cooldown attack",
            cooldown_duration=0,
            stamina_cost=5,
        )

        # Can use repeatedly
        assert ability.can_use(current_cooldown=0, current_stamina=10) is True
        assert ability.can_use(current_cooldown=0, current_stamina=5) is True

    def test_utf_contract_game_combat_005(self) -> None:
        """Verify UTF contract GAME-COMBAT-005: Ability Cooldowns."""
        ability = Ability(
            name="Test Ability",
            description="For contract testing",
            cooldown_duration=3,
            stamina_cost=10,
        )

        # Verify cooldown prevents use
        assert ability.can_use(current_cooldown=3, current_stamina=100) is False
        assert ability.can_use(current_cooldown=2, current_stamina=100) is False
        assert ability.can_use(current_cooldown=1, current_stamina=100) is False

        # Verify usable when cooldown reaches 0
        assert ability.can_use(current_cooldown=0, current_stamina=100) is True

        # Verify cooldown_duration is stored
        assert ability.cooldown_duration == 3
