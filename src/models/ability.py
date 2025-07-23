"""Ability model for special combat actions.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.3 Player Combat Integration
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from src.game.combat_system import CombatResult
    from src.models.character import Character
    from src.models.monster import Monster


@dataclass
class Ability:
    """Represents a special ability with cooldown management."""

    name: str
    description: str
    cooldown_duration: int  # turns
    stamina_cost: int
    damage_multiplier: float = 1.0
    effect: Optional[Callable[["Character", "Monster", "CombatResult"], None]] = None

    def can_use(self, current_cooldown: int, current_stamina: int) -> bool:
        """Check if ability can be used.

        Args:
            current_cooldown: Current cooldown remaining (0 = ready)
            current_stamina: Character's current stamina

        Returns:
            True if ability can be used, False otherwise
        """
        return current_cooldown == 0 and current_stamina >= self.stamina_cost
