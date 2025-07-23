"""Combat log system for tracking combat messages.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.2 Combat System Implementation
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class MessageType(Enum):
    """Types of combat messages."""

    ATTACK = "attack"
    CRITICAL = "critical"
    DEATH = "death"
    LOOT = "loot"
    INFO = "info"


@dataclass
class CombatMessage:
    """A single combat log message."""

    text: str
    message_type: MessageType
    timestamp: datetime


class CombatLog:
    """Manages combat messages and history."""

    def __init__(self, max_messages: int = 500):
        """Initialize combat log.

        Args:
            max_messages: Maximum messages to keep in history
        """
        self.max_messages = max_messages
        self.messages: List[CombatMessage] = []

    def add_message(self, text: str, message_type: MessageType = MessageType.ATTACK) -> None:
        """Add a message to the combat log.

        Args:
            text: Message text
            message_type: Type of message
        """
        message = CombatMessage(text=text, message_type=message_type, timestamp=datetime.now())

        self.messages.append(message)

        # Trim to max size
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_recent_messages(self, count: int) -> List[CombatMessage]:
        """Get the most recent messages.

        Args:
            count: Number of messages to retrieve

        Returns:
            List of recent messages
        """
        return self.messages[-count:] if self.messages else []

    def get_messages_by_type(self, message_type: MessageType) -> List[CombatMessage]:
        """Get all messages of a specific type.

        Args:
            message_type: Type to filter by

        Returns:
            Filtered messages
        """
        return [m for m in self.messages if m.message_type == message_type]

    def clear(self) -> None:
        """Clear all messages from the log."""
        self.messages.clear()

    def format_attack_message(
        self, attacker: str, target: str, damage: int, is_critical: bool
    ) -> str:
        """Format an attack message.

        Args:
            attacker: Name of attacker
            target: Name of target
            damage: Damage dealt
            is_critical: Whether it was a critical hit

        Returns:
            Formatted message
        """
        if is_critical:
            return f"{attacker} critically hits {target} for {damage} damage!"
        else:
            return f"{attacker} attacks {target} for {damage} damage"

    def format_death_message(self, entity: str, killer: Optional[str]) -> str:
        """Format a death message.

        Args:
            entity: Name of entity that died
            killer: Name of killer (None for environmental death)

        Returns:
            Formatted message
        """
        if killer:
            return f"{entity} is defeated by {killer}"
        else:
            return f"{entity} dies"

    def format_loot_message(self, entity: str, items: List[str]) -> str:
        """Format a loot message.

        Args:
            entity: Name of entity that found loot
            items: List of item names

        Returns:
            Formatted message
        """
        if items:
            item_list = ", ".join(items)
            return f"{entity} finds: {item_list}"
        else:
            return f"{entity} finds: nothing"
