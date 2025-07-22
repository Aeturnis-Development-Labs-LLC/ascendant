"""Lost Soul system for character persistence after death."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Achievement:
    """Represents an achievement/badge earned by a character."""

    id: str
    name: str
    description: str
    bonus_type: str  # "hp", "attack", "defense", "stamina", etc.
    bonus_value: int


@dataclass
class LostSoul:
    """Represents a dead character's soul with earned achievements."""

    character_name: str
    level: int
    death_floor: int
    death_message: str
    soul_badges: List[Achievement]
    total_play_time: float  # in seconds
    monsters_killed: int
    floors_cleared: int


class SoulSystem:
    """Manages Lost Soul mechanics and badge transfers."""

    # Badge bonus caps
    BONUS_CAPS = {
        "hp": 50,
        "attack": 10,
        "defense": 10,
        "stamina": 20,
        "movement_speed": 0.2,  # 20% max
        "experience_rate": 0.3,  # 30% max
    }

    def __init__(self):
        """Initialize soul system."""
        self.lost_souls: List[LostSoul] = []
        self.account_badges: List[Achievement] = []

    def create_lost_soul(
        self,
        character_name: str,
        level: int,
        death_floor: int,
        death_message: str,
        play_time: float,
        monsters_killed: int,
        floors_cleared: int,
    ) -> LostSoul:
        """Create a Lost Soul from a dead character.

        Args:
            character_name: Name of the dead character
            level: Character level at death
            death_floor: Floor number where death occurred
            death_message: How the character died
            play_time: Total time played in seconds
            monsters_killed: Total monsters killed
            floors_cleared: Total floors cleared

        Returns:
            New LostSoul instance
        """
        # Award badges based on achievements
        badges = self._calculate_death_badges(
            level, death_floor, monsters_killed, floors_cleared, play_time
        )

        soul = LostSoul(
            character_name=character_name,
            level=level,
            death_floor=death_floor,
            death_message=death_message,
            soul_badges=badges,
            total_play_time=play_time,
            monsters_killed=monsters_killed,
            floors_cleared=floors_cleared,
        )

        self.lost_souls.append(soul)
        self._update_account_badges(badges)

        return soul

    def transfer_badges(self, old_character_name: str, new_character_name: str) -> Dict[str, int]:
        """Transfer badge bonuses from account to new character.

        Args:
            old_character_name: Previous character (for record keeping)
            new_character_name: New character receiving bonuses

        Returns:
            Dictionary of bonus types and values
        """
        return self.calculate_badge_bonuses()

    def calculate_badge_bonuses(self) -> Dict[str, int]:
        """Calculate total bonuses from all account badges.

        Returns:
            Dictionary of bonus types and capped values
        """
        bonuses: Dict[str, int] = {}

        for badge in self.account_badges:
            current = bonuses.get(badge.bonus_type, 0)
            bonuses[badge.bonus_type] = current + badge.bonus_value

        # Apply caps
        for bonus_type, value in bonuses.items():
            cap = self.BONUS_CAPS.get(bonus_type, float("inf"))
            bonuses[bonus_type] = min(value, int(cap) if isinstance(cap, int) else int(cap * 100))

        return bonuses

    def _calculate_death_badges(
        self,
        level: int,
        death_floor: int,
        monsters_killed: int,
        floors_cleared: int,
        play_time: float,
    ) -> List[Achievement]:
        """Calculate badges earned from this character's achievements.

        Args:
            level: Character level at death
            death_floor: Floor where character died
            monsters_killed: Total monsters killed
            floors_cleared: Total floors cleared
            play_time: Total play time in seconds

        Returns:
            List of earned achievements
        """
        badges = []

        # Level-based badges
        if level >= 10:
            badges.append(
                Achievement(
                    id="veteran_soul",
                    name="Veteran Soul",
                    description="Reached level 10",
                    bonus_type="hp",
                    bonus_value=10,
                )
            )
        if level >= 25:
            badges.append(
                Achievement(
                    id="experienced_soul",
                    name="Experienced Soul",
                    description="Reached level 25",
                    bonus_type="stamina",
                    bonus_value=5,
                )
            )

        # Floor-based badges
        if death_floor >= 10:
            badges.append(
                Achievement(
                    id="deep_delver",
                    name="Deep Delver",
                    description="Reached floor 10",
                    bonus_type="defense",
                    bonus_value=2,
                )
            )

        # Combat badges
        if monsters_killed >= 100:
            badges.append(
                Achievement(
                    id="monster_slayer",
                    name="Monster Slayer",
                    description="Killed 100 monsters",
                    bonus_type="attack",
                    bonus_value=2,
                )
            )

        # Time-based badges
        hours_played = play_time / 3600
        if hours_played >= 5:
            badges.append(
                Achievement(
                    id="dedicated_soul",
                    name="Dedicated Soul",
                    description="Played for 5+ hours",
                    bonus_type="experience_rate",
                    bonus_value=5,  # 5% bonus
                )
            )

        return badges

    def _update_account_badges(self, new_badges: List[Achievement]) -> None:
        """Update account-wide badge collection.

        Args:
            new_badges: Badges earned by the deceased character
        """
        # Add only badges not already earned
        existing_ids = {badge.id for badge in self.account_badges}
        for badge in new_badges:
            if badge.id not in existing_ids:
                self.account_badges.append(badge)

    def get_soul_memorial_text(self) -> List[str]:
        """Get memorial text for display in Safe Haven.

        Returns:
            List of memorial lines
        """
        if not self.lost_souls:
            return ["No souls have yet passed through these halls..."]

        lines = ["=== Lost Soul Memorial ===", ""]
        for soul in self.lost_souls[-5:]:  # Show last 5 souls
            lines.append(f"{soul.character_name} (Level {soul.level})")
            lines.append(f"  {soul.death_message}")
            lines.append(f"  Floor {soul.death_floor}")
            lines.append("")

        return lines
