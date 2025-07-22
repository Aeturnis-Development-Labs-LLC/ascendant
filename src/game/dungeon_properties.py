"""Dungeon properties and level-bracket management."""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Set, Tuple

from src.models.floor import Floor


@dataclass
class DungeonRestrictions:
    """Restrictions for replaying dungeons."""

    xp_multiplier: float = 0.5  # 50% XP on replay
    rare_items_disabled: bool = True  # No rare items on replay
    completion_count: int = 0  # Times completed


class DungeonProperties:
    """Manages dungeon properties by level bracket."""

    # Floor counts by level bracket
    FLOORS_BY_BRACKET: Dict[Tuple[int, int], int] = {
        (1, 9): 3,  # Novice: 3 floors
        (10, 19): 4,  # Apprentice: 4 floors
        (20, 29): 5,  # Journeyman: 5 floors
        (30, 39): 6,  # Expert: 6 floors
        (40, 49): 7,  # Master: 7 floors
        (50, 59): 8,  # Grandmaster: 8 floors
        (60, 69): 9,  # Elder: 9 floors
        (70, 79): 10,  # Ancient: 10 floors
        (80, 89): 11,  # Legendary: 11 floors
        (90, 99): 12,  # Mythic: 12 floors
    }

    # Bracket names for display
    BRACKET_NAMES = {
        (1, 9): "Novice Hollow",
        (10, 19): "Apprentice Caverns",
        (20, 29): "Journeyman Depths",
        (30, 39): "Expert Catacombs",
        (40, 49): "Master Crypts",
        (50, 59): "Grandmaster Tombs",
        (60, 69): "Elder Vaults",
        (70, 79): "Ancient Ruins",
        (80, 89): "Legendary Abyss",
        (90, 99): "Mythic Sanctum",
    }

    def __init__(self):
        """Initialize dungeon properties."""
        # Track completion by character ID and dungeon bracket
        self.completion_tracking: Dict[str, Dict[Tuple[int, int], DungeonRestrictions]] = {}

    def get_floor_count(self, level_bracket: Tuple[int, int]) -> int:
        """Get number of floors for a level bracket.

        Args:
            level_bracket: (min_level, max_level) tuple

        Returns:
            Number of floors in the dungeon
        """
        return self.FLOORS_BY_BRACKET.get(level_bracket, 3)

    def get_bracket_name(self, level_bracket: Tuple[int, int]) -> str:
        """Get display name for a level bracket.

        Args:
            level_bracket: (min_level, max_level) tuple

        Returns:
            Display name of the dungeon
        """
        return self.BRACKET_NAMES.get(level_bracket, f"Unknown Dungeon {level_bracket}")

    def generate_fixed_layout(
        self, seed: int, bracket: Tuple[int, int], floor_number: int
    ) -> Floor:
        """Generate a fixed dungeon floor layout.

        Dungeons use deterministic generation so layouts are
        consistent for all players.

        Args:
            seed: Base seed for the dungeon
            bracket: Level bracket tuple
            floor_number: Which floor in the dungeon (1-based)

        Returns:
            Generated floor with fixed layout
        """
        # Combine seed with bracket and floor for unique but deterministic generation
        combined_seed = seed + bracket[0] * 1000 + bracket[1] * 100 + floor_number

        floor = Floor(seed=combined_seed)
        floor.generate()

        # Add bracket-specific features
        self._add_bracket_features(floor, bracket, floor_number)

        return floor

    def _add_bracket_features(
        self, floor: Floor, bracket: Tuple[int, int], floor_number: int
    ) -> None:
        """Add level-bracket specific features to a floor.

        Args:
            floor: Floor to modify
            bracket: Level bracket
            floor_number: Which floor in the dungeon
        """
        min_level, max_level = bracket

        # Higher brackets have more traps
        trap_density = 0.02 + (min_level / 100) * 0.03  # 2% to 5%
        floor.place_traps(trap_density)

        # Higher brackets have better chest tiers
        # TODO: When chest tiers are implemented, use them here
        # if min_level < 20:
        #     chest_tier = 1
        # elif min_level < 50:
        #     chest_tier = 2
        # else:
        #     chest_tier = 3

        # More chests in higher brackets
        chest_count = 1 + (min_level // 20)
        floor.place_chests(chest_count)

    def track_completion(self, character_id: str, dungeon_bracket: Tuple[int, int]) -> None:
        """Track dungeon completion for replay restrictions.

        Args:
            character_id: Unique character identifier
            dungeon_bracket: Level bracket of completed dungeon
        """
        if character_id not in self.completion_tracking:
            self.completion_tracking[character_id] = {}

        if dungeon_bracket not in self.completion_tracking[character_id]:
            self.completion_tracking[character_id][dungeon_bracket] = DungeonRestrictions()

        restrictions = self.completion_tracking[character_id][dungeon_bracket]
        restrictions.completion_count += 1

    def get_replay_restrictions(
        self, character_id: str, dungeon_bracket: Tuple[int, int]
    ) -> Optional[DungeonRestrictions]:
        """Get replay restrictions for a character in a dungeon.

        Args:
            character_id: Unique character identifier
            dungeon_bracket: Level bracket to check

        Returns:
            Restrictions if dungeon was completed before, None otherwise
        """
        if character_id not in self.completion_tracking:
            return None

        return self.completion_tracking[character_id].get(dungeon_bracket)

    def is_first_completion(self, character_id: str, dungeon_bracket: Tuple[int, int]) -> bool:
        """Check if this is the first time completing a dungeon.

        Args:
            character_id: Unique character identifier
            dungeon_bracket: Level bracket to check

        Returns:
            True if never completed before
        """
        restrictions = self.get_replay_restrictions(character_id, dungeon_bracket)
        return restrictions is None or restrictions.completion_count == 0

    def get_completed_dungeons(self, character_id: str) -> Set[Tuple[int, int]]:
        """Get set of completed dungeon brackets for a character.

        Args:
            character_id: Unique character identifier

        Returns:
            Set of completed dungeon brackets
        """
        if character_id not in self.completion_tracking:
            return set()

        return {
            bracket
            for bracket, restrictions in self.completion_tracking[character_id].items()
            if restrictions.completion_count > 0
        }

    def get_dungeon_info(self, bracket: Tuple[int, int]) -> Dict[str, Any]:
        """Get full information about a dungeon bracket.

        Args:
            bracket: Level bracket tuple

        Returns:
            Dictionary with dungeon information
        """
        return {
            "name": self.get_bracket_name(bracket),
            "level_range": bracket,
            "floor_count": self.get_floor_count(bracket),
            "min_level": bracket[0],
            "max_level": bracket[1],
        }
