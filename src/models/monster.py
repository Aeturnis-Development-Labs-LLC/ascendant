"""Monster class for enemies in the game.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.1 Monster Implementation
"""

from enum import Enum

from src.enums import EntityType
from src.models.entity import Entity


class AIBehavior(Enum):
    """AI behavior patterns for monsters."""

    PASSIVE = "passive"
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    RANGED = "ranged"


class Monster(Entity):
    """Represents a monster enemy."""

    def __init__(
        self,
        x: int,
        y: int,
        name: str,
        display_char: str,
        hp: int,
        hp_max: int,
        attack: int,
        defense: int,
        monster_type: str,
        ai_behavior: AIBehavior,
    ):
        """Initialize a monster with stats.

        Args:
            x: X coordinate
            y: Y coordinate
            name: Monster name
            display_char: Character to display
            hp: Current health points
            hp_max: Maximum health points
            attack: Attack power
            defense: Defense value
            monster_type: Type identifier (e.g., "goblin", "skeleton")
            ai_behavior: AI behavior pattern
        """
        super().__init__(x, y, EntityType.MONSTER)
        self.name = name
        self.display_char = display_char
        self.hp_max = hp_max
        self.hp = min(hp, hp_max)  # Cap HP at max
        self.attack = attack
        self.defense = defense
        self.monster_type = monster_type
        self.ai_behavior = ai_behavior

        # Validate stats
        if hp < 0:
            raise ValueError("HP cannot be negative")
        if hp_max <= 0:
            raise ValueError("Max HP must be positive")
        if attack < 0:
            raise ValueError("Attack cannot be negative")
        if defense < 0:
            raise ValueError("Defense cannot be negative")

    def render(self) -> str:
        """Return display character for monster."""
        return self.display_char

    def update(self, delta_time: float) -> None:
        """Update monster state (placeholder for now)."""
        # AI behavior will be implemented later
        pass

    def take_damage(self, damage: int) -> None:
        """Apply damage to the monster.

        Args:
            damage: Amount of damage to apply
        """
        self.hp = max(0, self.hp - damage)

    def is_alive(self) -> bool:
        """Check if monster is still alive."""
        return self.hp > 0
