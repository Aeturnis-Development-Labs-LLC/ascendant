"""Death handling system for entity deaths.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.2 Combat System Implementation
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from src.game.loot_system import LootDrop, LootSystem
    from src.models.character import Character
    from src.models.floor import Floor
    from src.models.monster import Monster


@dataclass
class DeathResult:
    """Result of handling an entity death."""

    entity_name: str
    entity_type: str
    position: Tuple[int, int]
    experience_awarded: int
    loot_dropped: List["LootDrop"]


class DeathHandler:
    """Handles entity death, loot drops, and experience awards."""

    # Base experience values by monster type
    MONSTER_EXPERIENCE = {
        "rat": 5,
        "goblin": 10,
        "skeleton": 15,
        "orc": 25,
        "troll": 40,
        "demon": 60,
        "dragon": 500,  # Boss
    }

    def __init__(self) -> None:
        """Initialize death handler."""
        self.loot_system: Optional["LootSystem"] = None

    def handle_death(
        self, entity: "Character | Monster", floor: "Floor", killer: Optional["Character | Monster"]
    ) -> Optional[DeathResult]:
        """Handle entity death.

        Args:
            entity: Entity that died
            floor: Current floor
            killer: Entity that killed it (None for environmental)

        Returns:
            DeathResult or None for player death
        """
        # Special handling for player death
        from src.enums import EntityType

        if hasattr(entity, "entity_type") and entity.entity_type == EntityType.PLAYER:
            return None  # Player death handled elsewhere

        # Get entity info before removal
        entity_name = entity.name
        entity_type = getattr(entity, "monster_type", "unknown")
        position = (entity.x, entity.y)

        # Remove entity from floor
        if (
            hasattr(floor, "entities")
            and position in floor.entities
            and floor.entities[position] == entity
        ):
            del floor.entities[position]

        # Calculate experience
        experience = self.calculate_experience(entity_type, floor.level)

        # Award experience to killer if it's the player
        if killer and hasattr(killer, "experience"):
            killer.experience = getattr(killer, "experience", 0) + experience

        # Generate loot
        loot_dropped = []
        if self.loot_system:
            luck = getattr(killer, "luck", 0) if killer else 0
            loot_dropped = self.loot_system.generate_loot(entity_type, floor.level, luck)

            # Place loot on floor
            if loot_dropped and hasattr(floor, "loot"):
                if position not in floor.loot:
                    floor.loot[position] = []
                floor.loot[position].extend(loot_dropped)

        return DeathResult(
            entity_name=entity_name,
            entity_type=entity_type,
            position=position,
            experience_awarded=experience,
            loot_dropped=loot_dropped,
        )

    def calculate_experience(self, monster_type: str, floor_level: int) -> int:
        """Calculate experience points for killing a monster.

        Args:
            monster_type: Type of monster
            floor_level: Current floor level

        Returns:
            Experience points to award
        """
        base_exp = self.MONSTER_EXPERIENCE.get(monster_type, 10)

        # Scale with floor level (10% per level)
        level_multiplier = 1 + (floor_level - 1) * 0.1

        return int(base_exp * level_multiplier)
