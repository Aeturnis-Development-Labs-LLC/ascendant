"""Trap class for environmental hazards.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.1 Monster Implementation
"""

from enum import Enum
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.character import Character


class TrapType(Enum):
    """Types of traps in the game."""

    SPIKE = "spike"
    POISON = "poison"
    ALARM = "alarm"


class Trap:
    """Represents a trap hazard on the floor."""

    # Display characters for each trap type
    DISPLAY_CHARS = {
        TrapType.SPIKE: "^",
        TrapType.POISON: "~",
        TrapType.ALARM: "!",
    }

    # Base damage values for each trap type
    BASE_DAMAGE = {TrapType.SPIKE: 5, TrapType.POISON: 3, TrapType.ALARM: 0}

    def __init__(
        self,
        x: int,
        y: int,
        trap_type: TrapType,
        damage: int,
        floor_level: int,
    ):
        """Initialize a trap.

        Args:
            x: X coordinate
            y: Y coordinate
            trap_type: Type of trap
            damage: Damage amount
            floor_level: Floor level (for scaling)
        """
        self.x = x
        self.y = y
        self.trap_type = trap_type
        self.damage = damage
        self.floor_level = floor_level
        self.triggered = False

    @property
    def position(self) -> tuple[int, int]:
        """Get position as tuple."""
        return (self.x, self.y)

    @classmethod
    def create_scaled(
        cls, x: int, y: int, trap_type: TrapType, floor_level: int
    ) -> "Trap":
        """Create a trap with damage scaled by floor level.

        Args:
            x: X coordinate
            y: Y coordinate
            trap_type: Type of trap
            floor_level: Floor level for scaling

        Returns:
            New trap instance with scaled damage
        """
        base_damage = cls.BASE_DAMAGE[trap_type]
        # Scale damage: +1 per 2 floors
        scaled_damage = base_damage + (floor_level - 1) // 2
        return cls(x, y, trap_type, scaled_damage, floor_level)

    def trigger(self, character: "Character") -> Optional[Dict[str, Any]]:
        """Trigger the trap effect on a character.

        Args:
            character: Character that triggered the trap

        Returns:
            Dictionary with trigger results, or None if already triggered
        """
        if self.triggered:
            return None

        self.triggered = True
        result: Dict[str, Any] = {"damage": self.damage, "effect": ""}

        if self.trap_type == TrapType.SPIKE:
            # Direct damage
            character.take_damage(self.damage)
            result["effect"] = "spike_damage"

        elif self.trap_type == TrapType.POISON:
            # Damage + poison status
            character.take_damage(self.damage)
            if hasattr(character, "apply_status"):
                character.apply_status("poisoned", duration=3)
            result["effect"] = "poisoned"

        elif self.trap_type == TrapType.ALARM:
            # Alert monsters in radius
            result["effect"] = "alarm_triggered"
            result["alert_radius"] = 10
            result["alert_position"] = self.position

        return result

    def render(self) -> str:
        """Return display character for trap."""
        if self.triggered:
            return "."
        return self.DISPLAY_CHARS[self.trap_type]

    def description(self) -> str:
        """Get trap description."""
        if self.triggered:
            return f"A triggered {self.trap_type.value} trap"

        descriptions = {
            TrapType.SPIKE: f"A spike trap ({self.damage} damage)",
            TrapType.POISON: f"A poison gas trap ({self.damage} damage + poison)",
            TrapType.ALARM: "An alarm trap (alerts monsters)",
        }
        return descriptions[self.trap_type]
