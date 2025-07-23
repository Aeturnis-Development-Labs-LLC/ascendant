"""Trap damage handler for combat system.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.2 Combat System Implementation
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.game.combat_log import CombatLog
    from src.models.character import Character
    from src.models.trap import Trap, TrapType


@dataclass
class TrapResult:
    """Result of a trap trigger."""

    trap_type: "TrapType"
    damage_dealt: int
    status_applied: Optional[str]
    trap_disarmed: bool
    alert_radius: int = 0


class TrapHandler:
    """Handles trap damage and effects following GAME-COMBAT-006."""

    def __init__(self) -> None:
        """Initialize trap handler."""
        self.combat_log: Optional["CombatLog"] = None

    def handle_trap(self, character: "Character", trap: "Trap") -> Optional[TrapResult]:
        """Handle trap trigger and damage.

        Args:
            character: Character that triggered the trap
            trap: The trap that was triggered

        Returns:
            TrapResult or None if trap already triggered
        """
        # Use the trap's built-in trigger method
        trigger_result = trap.trigger(character)

        if trigger_result is None:
            return None  # Trap already triggered

        # Extract results
        damage = trigger_result.get("damage", 0)
        effect = trigger_result.get("effect", "")

        # Determine status applied
        status_applied = None
        if effect == "poisoned":
            status_applied = "poisoned"

        # Get alert radius for alarm traps
        alert_radius = trigger_result.get("alert_radius", 0)

        # Create result
        result = TrapResult(
            trap_type=trap.trap_type,
            damage_dealt=damage,
            status_applied=status_applied,
            trap_disarmed=True,
            alert_radius=alert_radius,
        )

        # Log the trap trigger
        if self.combat_log:
            if damage > 0:
                msg = (
                    f"{character.name} triggered a {trap.trap_type.value} trap for {damage} damage!"
                )
            else:
                msg = f"{character.name} triggered an {trap.trap_type.value} trap!"

            self.combat_log.add_message(msg)

            if status_applied:
                self.combat_log.add_message(f"{character.name} is {status_applied}!")

        return result
