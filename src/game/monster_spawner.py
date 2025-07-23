"""Monster spawning system for floor population.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.1 Monster Implementation
"""

import random
from typing import Dict, List, Optional, Tuple, TypedDict

from src.enums import MonsterType, TileType
from src.models.floor import Floor
from src.models.monster import AIBehavior, Monster


class MonsterStats(TypedDict):
    """Type definition for monster stats."""

    name: str
    display_char: str
    base_hp: int
    base_attack: int
    base_defense: int
    ai_behavior: AIBehavior
    min_level: int
    max_level: int


class ScaledMonsterStats(TypedDict):
    """Type definition for scaled monster stats."""

    name: str
    display_char: str
    hp: int
    attack: int
    defense: int
    ai_behavior: AIBehavior


class MonsterSpawner:
    """Handles spawning monsters on floors."""

    # Monster definitions by type
    MONSTER_TYPES: Dict[str, MonsterStats] = {
        "rat": {
            "name": "Giant Rat",
            "display_char": "r",
            "base_hp": 3,
            "base_attack": 1,
            "base_defense": 0,
            "ai_behavior": AIBehavior.PASSIVE,
            "min_level": 1,
            "max_level": 3,
        },
        "goblin": {
            "name": "Goblin",
            "display_char": "g",
            "base_hp": 5,
            "base_attack": 2,
            "base_defense": 1,
            "ai_behavior": AIBehavior.AGGRESSIVE,
            "min_level": 1,
            "max_level": 5,
        },
        "skeleton": {
            "name": "Skeleton",
            "display_char": "s",
            "base_hp": 8,
            "base_attack": 3,
            "base_defense": 0,
            "ai_behavior": AIBehavior.AGGRESSIVE,
            "min_level": 2,
            "max_level": 7,
        },
        "orc": {
            "name": "Orc",
            "display_char": "o",
            "base_hp": 12,
            "base_attack": 4,
            "base_defense": 2,
            "ai_behavior": AIBehavior.AGGRESSIVE,
            "min_level": 4,
            "max_level": 10,
        },
        "troll": {
            "name": "Troll",
            "display_char": "T",
            "base_hp": 20,
            "base_attack": 6,
            "base_defense": 3,
            "ai_behavior": AIBehavior.DEFENSIVE,
            "min_level": 7,
            "max_level": 15,
        },
        "demon": {
            "name": "Lesser Demon",
            "display_char": "d",
            "base_hp": 25,
            "base_attack": 8,
            "base_defense": 4,
            "ai_behavior": AIBehavior.AGGRESSIVE,
            "min_level": 10,
            "max_level": 20,
        },
    }

    def spawn_monsters(
        self,
        floor: Floor,
        count: int,
        level: int,
        exclude_positions: Optional[List[Tuple[int, int]]] = None,
        monster_types: Optional[List[str]] = None,
    ) -> List[Monster]:
        """Spawn monsters on the floor.

        Args:
            floor: Floor to spawn monsters on
            count: Number of monsters to spawn
            level: Floor level for scaling
            exclude_positions: Positions to avoid spawning on
            monster_types: Specific types to spawn (None for random)

        Returns:
            List of spawned monsters
        """
        if exclude_positions is None:
            exclude_positions = []

        # Get valid spawn positions (in rooms, on floor tiles)
        valid_positions = self._get_valid_spawn_positions(floor, exclude_positions)
        if not valid_positions:
            return []

        # Determine which monster types can spawn at this level
        available_types = monster_types or self._get_available_monster_types(level)
        if not available_types:
            return []

        monsters = []
        used_positions = set(exclude_positions)

        for _ in range(count):
            if not valid_positions:
                break

            # Pick random position
            pos = random.choice(valid_positions)
            valid_positions.remove(pos)
            used_positions.add(pos)

            # Pick random monster type
            monster_type = random.choice(available_types)

            # Create monster with scaled stats
            stats = self.get_monster_stats(monster_type, level)
            monster = Monster(
                x=pos[0],
                y=pos[1],
                name=stats["name"],
                display_char=stats["display_char"],
                hp=stats["hp"],
                hp_max=stats["hp"],
                attack=stats["attack"],
                defense=stats["defense"],
                monster_type=MonsterType(monster_type),  # Convert string to enum
                ai_behavior=stats["ai_behavior"],
            )
            monsters.append(monster)

        return monsters

    def get_monster_stats(self, monster_type: str, level: int) -> ScaledMonsterStats:
        """Get scaled monster stats for a given type and level.

        Args:
            monster_type: Type of monster
            level: Floor level for scaling

        Returns:
            Dictionary of monster stats
        """
        base = self.MONSTER_TYPES[monster_type]

        # Scale stats based on level
        hp_scale = 1 + (level - 1) * 0.2  # +20% HP per level
        attack_scale = 1 + (level - 1) * 0.15  # +15% attack per level
        defense_scale = 1 + (level - 1) * 0.1  # +10% defense per level

        return {
            "name": base["name"],
            "display_char": base["display_char"],
            "hp": int(base["base_hp"] * hp_scale),
            "attack": int(base["base_attack"] * attack_scale),
            "defense": int(base["base_defense"] * defense_scale),
            "ai_behavior": base["ai_behavior"],
        }

    def _get_valid_spawn_positions(
        self, floor: Floor, exclude_positions: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """Get all valid positions for spawning monsters.

        Args:
            floor: Floor to check
            exclude_positions: Positions to exclude

        Returns:
            List of valid (x, y) positions
        """
        valid_positions = []
        exclude_set = set(exclude_positions)

        # Only spawn in rooms
        for room in floor.rooms:
            for x in range(room.x, room.x + room.width):
                for y in range(room.y, room.y + room.height):
                    pos = (x, y)

                    # Check if position is valid
                    tile = floor.tiles.get(pos)
                    if (
                        pos not in exclude_set
                        and tile is not None
                        and tile.tile_type == TileType.FLOOR
                        and tile.tile_type not in [TileType.STAIRS_UP, TileType.STAIRS_DOWN]
                    ):
                        valid_positions.append(pos)

        return valid_positions

    def _get_available_monster_types(self, level: int) -> List[str]:
        """Get monster types available at a given level.

        Args:
            level: Floor level

        Returns:
            List of monster type names
        """
        available = []
        for monster_type, info in self.MONSTER_TYPES.items():
            if info["min_level"] <= level <= info["max_level"]:
                available.append(monster_type)

        # Always have at least basic monsters
        if not available and level >= 1:
            available = ["rat", "goblin"]

        return available
