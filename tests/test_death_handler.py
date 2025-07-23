"""Tests for death handling system following UTF contract GAME-COMBAT-004.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.2 Combat System Implementation
"""

from unittest.mock import MagicMock

from src.game.death_handler import DeathHandler, DeathResult
from src.game.loot_system import LootDrop
from src.models.character import Character
from src.models.floor import Floor
from src.models.monster import AIBehavior, Monster


class TestDeathHandler:
    """Test cases for death handling system (GAME-COMBAT-004)."""

    def setup_method(self):
        """Set up test fixtures."""
        self.death_handler = DeathHandler()

        # Create test floor
        self.floor = Floor(width=20, height=20, level=1)

        # Create test character
        self.character = Character("Hero", 5, 5)
        self.character.level = 1
        self.character.experience = 0

        # Create test monster
        self.monster = Monster(
            x=5,
            y=6,
            name="Goblin",
            display_char="g",
            hp=0,  # Dead
            hp_max=10,
            attack=6,
            defense=2,
            monster_type="goblin",
            ai_behavior=AIBehavior.AGGRESSIVE,
        )

        # Add monster to floor's entity list
        if not hasattr(self.floor, "entities"):
            self.floor.entities = {}
        self.floor.entities[(5, 6)] = self.monster

    def test_handle_monster_death(self):
        """Test basic monster death handling."""
        # Mock loot system
        mock_loot = MagicMock()
        mock_loot.generate_loot.return_value = [LootDrop("Gold", 10, "currency")]
        self.death_handler.loot_system = mock_loot

        # Handle death
        result = self.death_handler.handle_death(self.monster, self.floor, self.character)

        assert result is not None
        assert result.entity_name == "Goblin"
        assert result.experience_awarded > 0
        assert len(result.loot_dropped) > 0
        assert result.position == (5, 6)

    def test_entity_removed_from_floor(self):
        """Test that dead entity is removed from floor (GAME-COMBAT-004)."""
        # Verify monster is on floor
        assert (5, 6) in self.floor.entities
        assert self.floor.entities[(5, 6)] == self.monster

        # Handle death
        self.death_handler.handle_death(self.monster, self.floor, self.character)

        # Verify monster removed
        assert (5, 6) not in self.floor.entities

    def test_experience_awarded(self):
        """Test experience points awarded to killer."""
        initial_exp = self.character.experience

        # Handle death
        result = self.death_handler.handle_death(self.monster, self.floor, self.character)

        # Verify experience awarded
        assert result.experience_awarded > 0
        assert self.character.experience == initial_exp + result.experience_awarded

    def test_experience_calculation(self):
        """Test experience calculation based on monster type."""
        # Goblin (level 1 monster)
        exp = self.death_handler.calculate_experience("goblin", 1)
        assert exp == 10  # Base exp for goblin

        # Higher level monster
        exp = self.death_handler.calculate_experience("orc", 5)
        assert exp > 10  # Should scale with level

        # Boss monster
        exp = self.death_handler.calculate_experience("dragon", 10)
        assert exp > 100  # Boss should give lots of exp

    def test_loot_drops(self):
        """Test loot drop generation."""
        # Mock loot system
        mock_loot = MagicMock()
        expected_loot = [
            LootDrop("Gold", 5, "currency"),
            LootDrop("Health Potion", 1, "consumable"),
        ]
        mock_loot.generate_loot.return_value = expected_loot
        self.death_handler.loot_system = mock_loot

        # Handle death
        result = self.death_handler.handle_death(self.monster, self.floor, self.character)

        # Verify loot
        assert len(result.loot_dropped) == 2
        assert result.loot_dropped[0].item_name == "Gold"
        assert result.loot_dropped[1].item_name == "Health Potion"

        # Verify loot system was called with correct params
        mock_loot.generate_loot.assert_called_once_with(
            "goblin",
            1,  # floor level
            self.character.luck if hasattr(self.character, "luck") else 0,
        )

    def test_loot_placed_on_floor(self):
        """Test that loot is placed on floor at death position."""
        # Mock loot
        mock_loot = MagicMock()
        mock_loot.generate_loot.return_value = [LootDrop("Gold", 10, "currency")]
        self.death_handler.loot_system = mock_loot

        # Ensure floor has loot container
        if not hasattr(self.floor, "loot"):
            self.floor.loot = {}

        # Handle death
        self.death_handler.handle_death(self.monster, self.floor, self.character)

        # Verify loot placed at monster position
        assert (5, 6) in self.floor.loot
        assert len(self.floor.loot[(5, 6)]) == 1
        assert self.floor.loot[(5, 6)][0].item_name == "Gold"

    def test_handle_character_death(self):
        """Test player character death handling."""
        self.character.hp = 0

        # Character death returns None (handled differently)
        result = self.death_handler.handle_death(self.character, self.floor, None)

        assert result is None  # Special handling for player

    def test_death_result_object(self):
        """Test DeathResult data structure."""
        loot = [LootDrop("Gold", 10, "currency")]

        result = DeathResult(
            entity_name="Goblin",
            entity_type="monster",
            position=(5, 6),
            experience_awarded=10,
            loot_dropped=loot,
        )

        assert result.entity_name == "Goblin"
        assert result.entity_type == "monster"
        assert result.position == (5, 6)
        assert result.experience_awarded == 10
        assert len(result.loot_dropped) == 1

    def test_multiple_entities_at_position(self):
        """Test handling death when multiple entities at same position."""
        # Add another entity at same position (shouldn't happen but test it)
        Monster(
            x=5,
            y=6,
            name="Rat",
            display_char="r",
            hp=5,
            hp_max=5,
            attack=1,
            defense=0,
            monster_type="rat",
            ai_behavior=AIBehavior.PASSIVE,
        )

        # Store original entity reference for testing
        # original_entity = self.floor.entities[(5, 6)]

        # Handle death of specific entity
        self.death_handler.handle_death(self.monster, self.floor, self.character)

        # Only the dead monster should be removed
        if (5, 6) in self.floor.entities:
            assert self.floor.entities[(5, 6)] != self.monster

    def test_utf_contract_game_combat_004(self):
        """Verify UTF contract GAME-COMBAT-004: Death Handling."""
        # Setup
        assert (5, 6) in self.floor.entities
        if not hasattr(self.floor, "loot"):
            self.floor.loot = {}

        mock_loot = MagicMock()
        mock_loot.generate_loot.return_value = [LootDrop("Gold", 10, "currency")]
        self.death_handler.loot_system = mock_loot

        initial_exp = self.character.experience

        # Handle death
        self.death_handler.handle_death(self.monster, self.floor, self.character)

        # Verify all contract requirements
        # 1. Entity removed from floor
        assert (5, 6) not in self.floor.entities

        # 2. Items dropped
        assert (5, 6) in self.floor.loot
        assert len(self.floor.loot[(5, 6)]) > 0

        # 3. Experience awarded
        assert self.character.experience > initial_exp

        # 4. Entity no longer exists
        assert self.monster not in self.floor.entities.values()
