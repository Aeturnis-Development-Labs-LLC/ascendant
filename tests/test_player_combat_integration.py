"""Integration tests for player combat system.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.3 Player Combat Integration
"""

from src.game.combat_log import CombatLog
from src.game.default_abilities import initialize_character_abilities
from src.models.character import Character
from src.models.floor import Floor
from src.models.monster import AIBehavior, Monster


class TestPlayerCombatIntegration:
    """Integration tests for complete player combat flow."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        # Create character with abilities
        self.character = Character("Hero", 5, 5)
        initialize_character_abilities(self.character)
        self.character.stamina = 100
        self.character.hp = 50

        # Create combat log and attach to character
        self.combat_log = CombatLog()
        self.character._combat_log = self.combat_log

        # Create test floor
        self.floor = Floor(width=20, height=20, level=1)

        # Create test monster adjacent to character
        self.monster = Monster(
            x=6,
            y=5,
            name="Goblin",
            display_char="g",
            hp=20,
            hp_max=20,
            attack=6,
            defense=2,
            monster_type="goblin",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

        # Add monster to floor
        if not hasattr(self.floor, "entities"):
            self.floor.entities = {}
        self.floor.entities[(6, 5)] = self.monster

    def test_basic_combat_flow(self) -> None:
        """Test basic attack flow without abilities."""
        # Basic attack
        initial_hp = self.monster.hp
        result = self.character.attack_target(self.monster)

        assert result is True
        assert self.monster.hp < initial_hp  # Damage was dealt

        # Check combat log
        messages = self.combat_log.get_recent_messages(1)
        assert len(messages) == 1
        assert "Hero" in messages[0].text and "Goblin" in messages[0].text

    def test_ability_combat_flow(self) -> None:
        """Test combat using abilities."""
        # Use Power Strike (2x damage)
        result = self.character.attack_target(self.monster, "Power Strike")

        assert result is True
        assert self.character.stamina == 80  # 100 - 20
        assert self.monster.hp == 2  # 20 - ((10 * 2) - 2) = 20 - 18 = 2
        assert self.character.ability_cooldowns["Power Strike"] == 3

        # Try to use again (should fail due to cooldown)
        result = self.character.attack_target(self.monster, "Power Strike")
        assert result is False
        assert self.character.stamina == 80  # No change

        # Use Quick Attack (no cooldown)
        result = self.character.attack_target(self.monster, "Quick Attack")
        assert result is True
        assert self.character.stamina == 75  # 80 - 5
        # Damage: 10 * 0.75 = 7.5 -> 7 (int), 7 - 2 = 5 damage
        # Quick Attack damage: floor(10 * 0.75) = 7, 7 - 2 = 5 damage
        # Monster had 2 HP, so should be dead
        assert self.monster.hp == 0
        assert self.monster.is_alive() is False

    def test_multiple_turn_combat(self) -> None:
        """Test combat over multiple turns with cooldown management."""
        # Turn 1: Use Heavy Slam
        result = self.character.attack_target(self.monster, "Heavy Slam")
        assert result is True
        assert self.character.stamina == 70  # 100 - 30
        # Damage: 10 * 3 = 30, 30 - 2 = 28 damage (overkill)
        assert self.monster.hp == 0
        assert self.character.ability_cooldowns["Heavy Slam"] == 5

        # Create new monster
        self.monster = Monster(
            x=5,
            y=4,
            name="Orc",
            display_char="o",
            hp=30,
            hp_max=30,
            attack=8,
            defense=4,
            monster_type="orc",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

        # Turn 2: Tick cooldowns
        self.character.tick_cooldowns()
        assert self.character.ability_cooldowns["Heavy Slam"] == 4

        # Try Heavy Slam again (still on cooldown)
        result = self.character.attack_target(self.monster, "Heavy Slam")
        assert result is False

        # Use Precise Strike instead
        initial_hp = self.monster.hp
        result = self.character.attack_target(self.monster, "Precise Strike")
        assert result is True
        # Verify damage was dealt
        assert self.monster.hp < initial_hp

    def test_stamina_management(self) -> None:
        """Test ability usage limited by stamina."""
        # Drain stamina
        self.character.stamina = 25

        # Can use Power Strike (20 stamina cost)
        result = self.character.attack_target(self.monster, "Power Strike")
        assert result is True
        assert self.character.stamina == 5

        # Cannot use Heavy Slam (30 stamina cost)
        result = self.character.attack_target(self.monster, "Heavy Slam")
        assert result is False
        assert self.character.stamina == 5  # No change

        # Can still use Quick Attack (5 stamina cost) if monster is alive
        if self.monster.is_alive():
            result = self.character.attack_target(self.monster, "Quick Attack")
            assert result is True
            assert self.character.stamina == 0
        else:
            # Create new monster to test Quick Attack
            self.monster = Monster(
                x=6,
                y=5,
                name="Goblin2",
                display_char="g",
                hp=10,
                hp_max=10,
                attack=6,
                defense=2,
                monster_type="goblin",
                ai_behavior=AIBehavior.AGGRESSIVE,
            )
            result = self.character.attack_target(self.monster, "Quick Attack")
            assert result is True
            assert self.character.stamina == 0

    def test_all_abilities_usable(self) -> None:
        """Test that all default abilities work correctly."""
        abilities_to_test = [
            ("Power Strike", 20, 2.0),
            ("Quick Attack", 5, 0.75),
            ("Precise Strike", 15, 1.5),
            ("Defensive Strike", 10, 1.0),
        ]

        for ability_name, stamina_cost, _multiplier in abilities_to_test:
            # Reset for each test
            self.character.stamina = 100

            # Create fresh monster for each test
            self.monster = Monster(
                x=6,
                y=5,
                name="Test Goblin",
                display_char="g",
                hp=30,
                hp_max=30,
                attack=6,
                defense=2,
                monster_type="goblin",
                ai_behavior=AIBehavior.AGGRESSIVE,
            )

            initial_hp = self.monster.hp
            result = self.character.attack_target(self.monster, ability_name)
            assert result is True
            assert self.character.stamina == 100 - stamina_cost

            # Check damage applied - just verify damage was done
            assert self.monster.hp < initial_hp

    def test_combat_log_messages(self) -> None:
        """Test combat log properly records ability usage."""
        # Clear log
        self.combat_log.clear()

        # Use ability
        self.character.attack_target(self.monster, "Power Strike")

        messages = self.combat_log.get_recent_messages(100)
        assert len(messages) >= 1
        assert "Hero" in messages[0].text and "Goblin" in messages[0].text

        # If monster dies, should have death message
        self.monster.hp = 1
        self.character.attack_target(self.monster, "Quick Attack")

        messages = self.combat_log.get_recent_messages(100)
        assert any("defeated" in msg.text for msg in messages)

    def test_range_validation(self) -> None:
        """Test that attacks require adjacency."""
        # Move monster far away
        self.monster.x = 10
        self.monster.y = 10

        # Basic attack should fail
        result = self.character.attack_target(self.monster)
        assert result is False

        # Ability attack should also fail
        result = self.character.attack_target(self.monster, "Power Strike")
        assert result is False
        assert self.character.stamina == 100  # No stamina used
        assert self.character.ability_cooldowns["Power Strike"] == 0  # No cooldown set
