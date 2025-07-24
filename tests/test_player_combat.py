"""Tests for player combat integration following UTF contract GAME-COMBAT-005.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.3 Player Combat Integration
"""

from unittest.mock import MagicMock, patch

from src.models.ability import Ability
from src.models.character import Character
from src.models.floor import Floor
from src.models.monster import AIBehavior, Monster


class TestPlayerCombat:
    """Test cases for player combat integration."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.character = Character("Hero", 5, 5)
        self.character.stamina = 100
        self.character.hp = 50

        # Create test floor
        self.floor = Floor(width=20, height=20, level=1)

        # Create test monster adjacent to character
        self.monster = Monster(
            x=6,
            y=5,
            name="Goblin",
            display_char="g",
            hp=10,
            hp_max=10,
            attack=6,
            defense=2,
            monster_type="goblin",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

        # Add monster to floor
        if not hasattr(self.floor, "entities"):
            self.floor.entities = {}
        self.floor.entities[(6, 5)] = self.monster

    def test_character_has_abilities_dict(self) -> None:
        """Test Character has abilities dictionary."""
        assert hasattr(self.character, "abilities")
        assert isinstance(self.character.abilities, dict)

    def test_character_has_ability_cooldowns(self) -> None:
        """Test Character has ability cooldowns tracking."""
        assert hasattr(self.character, "ability_cooldowns")
        assert isinstance(self.character.ability_cooldowns, dict)

    def test_attack_target_basic_attack(self) -> None:
        """Test basic attack without ability."""
        # Mock combat system
        with patch("src.game.combat_system.CombatSystem") as mock_combat:
            mock_instance = MagicMock()
            mock_instance.attack.return_value = MagicMock()  # Return a result
            mock_combat.return_value = mock_instance

            result = self.character.attack_target(self.monster)

            assert result is True
            mock_instance.attack.assert_called_once_with(self.character, self.monster)

    def test_attack_target_with_ability(self) -> None:
        """Test attack with ability (GAME-COMBAT-005)."""
        # Add ability to character
        ability = Ability(
            name="Power Strike",
            description="A powerful attack",
            cooldown_duration=3,
            stamina_cost=20,
            damage_multiplier=2.0,
        )
        self.character.abilities["Power Strike"] = ability
        self.character.ability_cooldowns["Power Strike"] = 0

        with patch("src.game.combat_system.CombatSystem") as mock_combat:
            mock_instance = MagicMock()
            mock_instance.attack.return_value = MagicMock()  # Return a result
            mock_combat.return_value = mock_instance

            result = self.character.attack_target(self.monster, ability_name="Power Strike")

            assert result is True
            # Should deduct stamina
            assert self.character.stamina == 80  # 100 - 20
            # Should set cooldown
            assert self.character.ability_cooldowns["Power Strike"] == 3

    def test_cannot_use_ability_on_cooldown(self) -> None:
        """Test ability blocked by cooldown (GAME-COMBAT-005)."""
        # Add ability with cooldown
        ability = Ability(
            name="Heavy Strike",
            description="A heavy attack",
            cooldown_duration=5,
            stamina_cost=25,
        )
        self.character.abilities["Heavy Strike"] = ability
        self.character.ability_cooldowns["Heavy Strike"] = 2  # On cooldown

        result = self.character.attack_target(self.monster, ability_name="Heavy Strike")

        assert result is False  # Attack failed
        assert self.character.stamina == 100  # No stamina deducted
        assert self.character.ability_cooldowns["Heavy Strike"] == 2  # Cooldown unchanged

    def test_cannot_use_ability_without_stamina(self) -> None:
        """Test ability blocked by insufficient stamina."""
        # Add ability
        ability = Ability(
            name="Draining Strike",
            description="Uses lots of stamina",
            cooldown_duration=2,
            stamina_cost=30,
        )
        self.character.abilities["Draining Strike"] = ability
        self.character.ability_cooldowns["Draining Strike"] = 0
        self.character.stamina = 20  # Not enough

        result = self.character.attack_target(self.monster, ability_name="Draining Strike")

        assert result is False
        assert self.character.stamina == 20  # Unchanged
        assert self.character.ability_cooldowns["Draining Strike"] == 0  # No cooldown set

    def test_tick_cooldowns_decrements_all(self) -> None:
        """Test tick_cooldowns decrements all ability cooldowns."""
        # Set up multiple abilities with cooldowns
        self.character.abilities = {
            "Ability1": Ability("Ability1", "Test", 3, 10),
            "Ability2": Ability("Ability2", "Test", 5, 15),
            "Ability3": Ability("Ability3", "Test", 2, 20),
        }
        self.character.ability_cooldowns = {
            "Ability1": 3,
            "Ability2": 1,
            "Ability3": 0,
        }

        self.character.tick_cooldowns()

        assert self.character.ability_cooldowns["Ability1"] == 2
        assert self.character.ability_cooldowns["Ability2"] == 0
        assert self.character.ability_cooldowns["Ability3"] == 0  # Stays at 0

    def test_tick_cooldowns_never_negative(self) -> None:
        """Test cooldowns never go negative."""
        self.character.abilities = {"Test": Ability("Test", "Test", 1, 5)}
        self.character.ability_cooldowns = {"Test": 0}

        # Tick multiple times
        self.character.tick_cooldowns()
        self.character.tick_cooldowns()
        self.character.tick_cooldowns()

        assert self.character.ability_cooldowns["Test"] == 0  # Never negative

    def test_use_ability_method(self) -> None:
        """Test use_ability method directly."""
        ability = Ability(
            name="Quick Strike",
            description="A quick attack",
            cooldown_duration=1,
            stamina_cost=10,
            damage_multiplier=1.5,
        )
        self.character.abilities["Quick Strike"] = ability
        self.character.ability_cooldowns["Quick Strike"] = 0

        result = self.character.use_ability("Quick Strike", self.monster)

        assert result is not None
        assert self.character.stamina == 90  # 100 - 10
        assert self.character.ability_cooldowns["Quick Strike"] == 1

    def test_invalid_ability_name(self) -> None:
        """Test using non-existent ability."""
        result = self.character.attack_target(self.monster, ability_name="Fake Ability")

        assert result is False

    def test_attack_non_adjacent_target(self) -> None:
        """Test cannot attack non-adjacent target."""
        # Create distant monster
        distant_monster = Monster(
            x=10,
            y=10,
            name="Distant Goblin",
            display_char="g",
            hp=10,
            hp_max=10,
            attack=6,
            defense=2,
            monster_type="goblin",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

        result = self.character.attack_target(distant_monster)

        assert result is False  # Too far away

    def test_utf_contract_game_combat_005_integration(self) -> None:
        """Full integration test for GAME-COMBAT-005."""
        # Create ability
        ability = Ability(
            name="Cooldown Test",
            description="Tests cooldown mechanics",
            cooldown_duration=3,
            stamina_cost=15,
        )
        self.character.abilities["Cooldown Test"] = ability
        self.character.ability_cooldowns["Cooldown Test"] = 0

        # Use ability
        with patch("src.game.combat_system.CombatSystem") as mock_combat:
            mock_instance = MagicMock()
            mock_instance.attack.return_value = MagicMock()
            mock_combat.return_value = mock_instance

            assert self.character.attack_target(self.monster, "Cooldown Test") is True
            assert self.character.ability_cooldowns["Cooldown Test"] == 3

            # Cannot use while on cooldown
            assert self.character.attack_target(self.monster, "Cooldown Test") is False

            # Tick cooldowns
            self.character.tick_cooldowns()
            assert self.character.ability_cooldowns["Cooldown Test"] == 2

            self.character.tick_cooldowns()
            assert self.character.ability_cooldowns["Cooldown Test"] == 1

            self.character.tick_cooldowns()
            assert self.character.ability_cooldowns["Cooldown Test"] == 0

            # Can use again
            self.character.stamina = 100  # Reset stamina
            assert self.character.attack_target(self.monster, "Cooldown Test") is True
