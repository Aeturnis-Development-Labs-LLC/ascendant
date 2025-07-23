"""Tests for combat log system.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.2 Combat System Implementation
"""

from datetime import datetime
from unittest.mock import patch

from src.game.combat_log import CombatLog, CombatMessage, MessageType


class TestCombatLog:
    """Test cases for combat logging system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.combat_log = CombatLog(max_messages=100)

    def test_add_message(self):
        """Test adding messages to combat log."""
        self.combat_log.add_message("Player attacks Goblin for 8 damage")

        assert len(self.combat_log.messages) == 1
        assert self.combat_log.messages[0].text == "Player attacks Goblin for 8 damage"
        assert self.combat_log.messages[0].message_type == MessageType.ATTACK

    def test_message_types(self):
        """Test different message types."""
        self.combat_log.add_message("Player attacks Goblin", MessageType.ATTACK)
        self.combat_log.add_message("Critical hit!", MessageType.CRITICAL)
        self.combat_log.add_message("Goblin dies", MessageType.DEATH)
        self.combat_log.add_message("You found 10 gold", MessageType.LOOT)
        self.combat_log.add_message("Welcome to floor 2", MessageType.INFO)

        assert self.combat_log.messages[0].message_type == MessageType.ATTACK
        assert self.combat_log.messages[1].message_type == MessageType.CRITICAL
        assert self.combat_log.messages[2].message_type == MessageType.DEATH
        assert self.combat_log.messages[3].message_type == MessageType.LOOT
        assert self.combat_log.messages[4].message_type == MessageType.INFO

    def test_message_timestamp(self):
        """Test messages have timestamps."""
        # Mock datetime
        fixed_time = datetime(2025, 7, 23, 12, 0, 0)
        with patch("src.game.combat_log.datetime") as mock_datetime:
            mock_datetime.now.return_value = fixed_time

            self.combat_log.add_message("Test message")

        assert self.combat_log.messages[0].timestamp == fixed_time

    def test_max_messages_limit(self):
        """Test log respects maximum message limit."""
        # Create log with small limit
        log = CombatLog(max_messages=5)

        # Add more than limit
        for i in range(10):
            log.add_message(f"Message {i}")

        # Should only keep last 5
        assert len(log.messages) == 5
        assert log.messages[0].text == "Message 5"
        assert log.messages[-1].text == "Message 9"

    def test_get_recent_messages(self):
        """Test getting recent messages."""
        # Add 10 messages
        for i in range(10):
            self.combat_log.add_message(f"Message {i}")

        # Get last 3
        recent = self.combat_log.get_recent_messages(3)
        assert len(recent) == 3
        assert recent[0].text == "Message 7"
        assert recent[2].text == "Message 9"

    def test_clear_log(self):
        """Test clearing the combat log."""
        # Add messages
        self.combat_log.add_message("Message 1")
        self.combat_log.add_message("Message 2")
        assert len(self.combat_log.messages) == 2

        # Clear
        self.combat_log.clear()
        assert len(self.combat_log.messages) == 0

    def test_format_attack_message(self):
        """Test formatting attack messages."""
        msg = self.combat_log.format_attack_message(
            attacker="Player", target="Goblin", damage=8, is_critical=False
        )
        assert msg == "Player attacks Goblin for 8 damage"

        # With critical
        msg = self.combat_log.format_attack_message(
            attacker="Player", target="Goblin", damage=16, is_critical=True
        )
        assert msg == "Player critically hits Goblin for 16 damage!"

    def test_format_death_message(self):
        """Test formatting death messages."""
        msg = self.combat_log.format_death_message("Goblin", "Player")
        assert msg == "Goblin is defeated by Player"

        # Self death (trap, etc)
        msg = self.combat_log.format_death_message("Goblin", None)
        assert msg == "Goblin dies"

    def test_format_loot_message(self):
        """Test formatting loot messages."""
        msg = self.combat_log.format_loot_message("Player", ["10 gold", "Health Potion"])
        assert msg == "Player finds: 10 gold, Health Potion"

        # Single item
        msg = self.combat_log.format_loot_message("Player", ["Sword"])
        assert msg == "Player finds: Sword"

        # No items
        msg = self.combat_log.format_loot_message("Player", [])
        assert msg == "Player finds: nothing"

    def test_combat_message_object(self):
        """Test CombatMessage data structure."""
        now = datetime.now()
        msg = CombatMessage(text="Test message", message_type=MessageType.ATTACK, timestamp=now)

        assert msg.text == "Test message"
        assert msg.message_type == MessageType.ATTACK
        assert msg.timestamp == now

    def test_message_filtering(self):
        """Test filtering messages by type."""
        # Add various messages
        self.combat_log.add_message("Attack 1", MessageType.ATTACK)
        self.combat_log.add_message("Death 1", MessageType.DEATH)
        self.combat_log.add_message("Attack 2", MessageType.ATTACK)
        self.combat_log.add_message("Loot 1", MessageType.LOOT)

        # Filter attacks only
        attacks = self.combat_log.get_messages_by_type(MessageType.ATTACK)
        assert len(attacks) == 2
        assert all(m.message_type == MessageType.ATTACK for m in attacks)

    def test_combat_log_integration(self):
        """Test combat log for complete combat sequence."""
        # Simulate combat sequence
        self.combat_log.add_message(
            self.combat_log.format_attack_message("Player", "Goblin", 8, False), MessageType.ATTACK
        )

        self.combat_log.add_message(
            self.combat_log.format_attack_message("Goblin", "Player", 2, False), MessageType.ATTACK
        )

        self.combat_log.add_message(
            self.combat_log.format_attack_message("Player", "Goblin", 16, True),
            MessageType.CRITICAL,
        )

        self.combat_log.add_message(
            self.combat_log.format_death_message("Goblin", "Player"), MessageType.DEATH
        )

        self.combat_log.add_message(
            self.combat_log.format_loot_message("Player", ["5 gold", "Potion"]), MessageType.LOOT
        )

        # Verify sequence
        assert len(self.combat_log.messages) == 5
        assert self.combat_log.messages[0].message_type == MessageType.ATTACK
        assert self.combat_log.messages[2].message_type == MessageType.CRITICAL
        assert self.combat_log.messages[3].message_type == MessageType.DEATH
        assert self.combat_log.messages[4].message_type == MessageType.LOOT
