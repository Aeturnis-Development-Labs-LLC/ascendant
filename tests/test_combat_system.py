"""Tests for combat system following UTF contracts.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.2 Combat System Implementation
"""

from unittest.mock import MagicMock, patch

from src.game.combat_system import CombatResult, CombatSystem
from src.models.character import Character
from src.models.monster import AIBehavior, Monster


class TestCombatSystem:
    """Test cases for combat system (GAME-COMBAT-002, GAME-COMBAT-003)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.combat_system = CombatSystem()

        # Create test character
        self.character = Character("Hero", 5, 5)
        self.character.hp = 20
        self.character.hp_max = 20
        self.character.attack = 10
        self.character.defense = 5
        self.character.crit_chance = 0.1  # 10% crit chance

        # Create test monster
        self.monster = Monster(
            x=5,
            y=6,
            name="Goblin",
            display_char="g",
            hp=10,
            hp_max=10,
            attack=6,
            defense=2,
            monster_type="goblin",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

    def test_basic_attack_damage_calculation(self):
        """Test basic attack damage calculation (ATK - DEF, min 1)."""
        # Character attacks monster: 10 ATK - 2 DEF = 8 damage
        damage = self.combat_system.calculate_damage(self.character.attack, self.monster.defense)
        assert damage == 8

        # Monster attacks character: 6 ATK - 5 DEF = 1 damage
        damage = self.combat_system.calculate_damage(self.monster.attack, self.character.defense)
        assert damage == 1

        # Test minimum damage of 1
        damage = self.combat_system.calculate_damage(1, 10)
        assert damage == 1

    def test_critical_hit_calculation(self):
        """Test critical hit calculation (GAME-COMBAT-002)."""
        # Test with 100% crit chance
        is_crit = self.combat_system.calculate_critical(1.0)
        assert is_crit is True

        # Test with 0% crit chance
        is_crit = self.combat_system.calculate_critical(0.0)
        assert is_crit is False

        # Test with 50% crit chance (mock random)
        with patch("random.random", return_value=0.3):
            is_crit = self.combat_system.calculate_critical(0.5)
            assert is_crit is True

        with patch("random.random", return_value=0.7):
            is_crit = self.combat_system.calculate_critical(0.5)
            assert is_crit is False

    def test_critical_hit_doubles_damage(self):
        """Test that critical hits double damage (GAME-COMBAT-002)."""
        base_damage = 8

        # Normal hit
        final_damage = self.combat_system.apply_critical_multiplier(base_damage, False)
        assert final_damage == 8

        # Critical hit (doubles damage)
        final_damage = self.combat_system.apply_critical_multiplier(base_damage, True)
        assert final_damage == 16

    def test_attack_resolution(self):
        """Test full attack resolution (GAME-COMBAT-003)."""
        # Mock combat log
        self.combat_system.combat_log = MagicMock()

        # Character attacks monster (no crit)
        with patch.object(self.combat_system, "calculate_critical", return_value=False):
            result = self.combat_system.attack(self.character, self.monster)

        assert result.damage == 8  # 10 ATK - 2 DEF
        assert result.is_critical is False
        assert result.target_died is False
        assert self.monster.hp == 2  # 10 - 8

        # Verify combat log was called
        self.combat_system.combat_log.add_message.assert_called()

    def test_attack_with_critical(self):
        """Test attack with critical hit."""
        # Mock combat log
        self.combat_system.combat_log = MagicMock()

        # Character attacks monster (with crit)
        with patch.object(self.combat_system, "calculate_critical", return_value=True):
            result = self.combat_system.attack(self.character, self.monster)

        assert result.damage == 16  # (10 ATK - 2 DEF) * 2
        assert result.is_critical is True
        assert result.target_died is True  # 10 HP - 16 damage
        assert self.monster.hp == 0

    def test_target_death_detection(self):
        """Test that death is properly detected (GAME-COMBAT-003)."""
        self.combat_system.combat_log = MagicMock()

        # Set monster to low HP
        self.monster.hp = 1

        # Attack should kill the monster
        result = self.combat_system.attack(self.character, self.monster)

        assert result.target_died is True
        assert self.monster.hp == 0
        assert not self.monster.is_alive()

    def test_combat_result_object(self):
        """Test CombatResult data structure."""
        result = CombatResult(
            attacker="Hero", target="Goblin", damage=10, is_critical=True, target_died=False
        )

        assert result.attacker == "Hero"
        assert result.target == "Goblin"
        assert result.damage == 10
        assert result.is_critical is True
        assert result.target_died is False

    def test_attack_dead_target(self):
        """Test attacking an already dead target."""
        self.monster.hp = 0

        result = self.combat_system.attack(self.character, self.monster)

        assert result is None  # Should not attack dead targets

    def test_utf_contract_game_combat_002(self):
        """Verify UTF contract GAME-COMBAT-002: Critical Hit."""
        # Test crit chance percentage is respected
        hits = 0
        total = 10000
        crit_chance = 0.15  # 15%

        with patch("random.random") as mock_random:
            # Simulate random values
            for i in range(total):
                mock_random.return_value = i / total
                if self.combat_system.calculate_critical(crit_chance):
                    hits += 1

        # Should be close to 15% (allow 1% variance)
        actual_rate = hits / total
        assert 0.14 <= actual_rate <= 0.16

    def test_utf_contract_game_combat_003(self):
        """Verify UTF contract GAME-COMBAT-003: Combat Resolution."""
        initial_hp = self.monster.hp
        expected_damage = 8

        self.combat_system.combat_log = MagicMock()

        # Apply combat
        with patch.object(self.combat_system, "calculate_critical", return_value=False):
            self.combat_system.attack(self.character, self.monster)

        # Verify HP reduced correctly
        assert self.monster.hp == initial_hp - expected_damage

        # Verify combat logged
        self.combat_system.combat_log.add_message.assert_called()

        # Verify death triggered if HP <= 0
        self.monster.hp = 0
        assert not self.monster.is_alive()
