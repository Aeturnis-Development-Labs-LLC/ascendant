"""Combat system for handling attacks and damage calculation.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.2 Combat System Implementation
"""

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.game.combat_log import CombatLog
    from src.models.character import Character
    from src.models.monster import Monster


@dataclass
class CombatResult:
    """Result of a combat action."""

    attacker: str
    target: str
    damage: int
    is_critical: bool
    target_died: bool


class CombatSystem:
    """Handles combat mechanics and calculations."""

    def __init__(self, combat_log: Optional["CombatLog"] = None) -> None:
        """Initialize combat system.

        Args:
            combat_log: Optional combat log to use for recording events
        """
        self.combat_log = combat_log

    def calculate_damage(self, attack: int, defense: int) -> int:
        """Calculate base damage using ATK - DEF formula.

        Args:
            attack: Attacker's attack stat
            defense: Defender's defense stat

        Returns:
            Damage amount (minimum 1)
        """
        return max(1, attack - defense)

    def calculate_critical(self, crit_chance: float) -> bool:
        """Determine if attack is critical hit.

        Args:
            crit_chance: Critical hit chance (0.0 to 1.0)

        Returns:
            True if critical hit
        """
        return random.random() < crit_chance

    def apply_critical_multiplier(self, base_damage: int, is_critical: bool) -> int:
        """Apply critical hit multiplier to damage.

        Args:
            base_damage: Base damage amount
            is_critical: Whether this is a critical hit

        Returns:
            Final damage after multiplier
        """
        return base_damage * 2 if is_critical else base_damage

    def attack(
        self, attacker: "Character | Monster", target: "Character | Monster"
    ) -> Optional[CombatResult]:
        """Execute an attack from attacker to target.

        Args:
            attacker: Entity performing the attack
            target: Entity being attacked

        Returns:
            CombatResult or None if attack invalid
        """
        # Don't attack dead targets
        if not target.is_alive():
            return None

        # Calculate critical hit
        crit_chance = getattr(attacker, "crit_chance", 0.0)
        is_critical = self.calculate_critical(crit_chance)

        # Calculate damage
        base_damage = self.calculate_damage(attacker.attack, target.defense)
        final_damage = self.apply_critical_multiplier(base_damage, is_critical)

        # Apply damage
        target.take_damage(final_damage)

        # Check if target died
        target_died = not target.is_alive()

        # Create result
        result = CombatResult(
            attacker=attacker.name,
            target=target.name,
            damage=final_damage,
            is_critical=is_critical,
            target_died=target_died,
        )

        # Log combat message
        if self.combat_log:
            if is_critical:
                msg = f"{attacker.name} critically hits {target.name} for {final_damage} damage!"
            else:
                msg = f"{attacker.name} attacks {target.name} for {final_damage} damage"

            self.combat_log.add_message(msg)

            if target_died:
                self.combat_log.add_message(f"{target.name} is defeated!")

        return result

    def resolve_attack(self, attacker, target):
        """Alias for attack() method to match expected interface.

        Args:
            attacker: Entity performing the attack
            target: Entity being attacked

        Returns:
            Object with damage_dealt attribute
        """
        result = self.attack(attacker, target)
        if result:
            # Add damage_dealt attribute for compatibility
            setattr(result, "damage_dealt", result.damage)
        return result
