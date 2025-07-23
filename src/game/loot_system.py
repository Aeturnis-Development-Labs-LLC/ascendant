"""Loot system for item drops.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.2 Combat System Implementation
"""

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LootDrop:
    """Represents a dropped item."""

    item_name: str
    quantity: int
    item_type: str  # "currency", "consumable", "equipment", etc.


class LootSystem:
    """Handles loot generation and drops."""

    # Loot tables by monster type
    LOOT_TABLES: Dict[str, List[Dict[str, Any]]] = {
        "rat": [
            {"item": "Gold", "quantity": (1, 3), "chance": 0.5, "type": "currency"},
            {"item": "Cheese", "quantity": 1, "chance": 0.1, "type": "consumable"},
        ],
        "goblin": [
            {"item": "Gold", "quantity": (3, 8), "chance": 0.7, "type": "currency"},
            {"item": "Health Potion", "quantity": 1, "chance": 0.2, "type": "consumable"},
            {"item": "Rusty Dagger", "quantity": 1, "chance": 0.05, "type": "equipment"},
        ],
        "skeleton": [
            {"item": "Gold", "quantity": (5, 15), "chance": 0.6, "type": "currency"},
            {"item": "Bone", "quantity": (1, 3), "chance": 0.8, "type": "material"},
            {"item": "Old Sword", "quantity": 1, "chance": 0.1, "type": "equipment"},
        ],
        "orc": [
            {"item": "Gold", "quantity": (10, 25), "chance": 0.8, "type": "currency"},
            {"item": "Health Potion", "quantity": 1, "chance": 0.3, "type": "consumable"},
            {"item": "Iron Sword", "quantity": 1, "chance": 0.15, "type": "equipment"},
            {"item": "Iron Armor", "quantity": 1, "chance": 0.1, "type": "equipment"},
        ],
        "troll": [
            {"item": "Gold", "quantity": (20, 50), "chance": 0.9, "type": "currency"},
            {"item": "Greater Health Potion", "quantity": 1, "chance": 0.4, "type": "consumable"},
            {"item": "Troll Blood", "quantity": 1, "chance": 0.3, "type": "material"},
        ],
        "demon": [
            {"item": "Gold", "quantity": (50, 100), "chance": 1.0, "type": "currency"},
            {"item": "Demonic Essence", "quantity": 1, "chance": 0.5, "type": "material"},
            {"item": "Hellfire Sword", "quantity": 1, "chance": 0.05, "type": "equipment"},
        ],
    }

    def __init__(self, seed: Optional[int] = None) -> None:
        """Initialize loot system with optional seed."""
        self._rng = random.Random(seed)

    def generate_loot(self, monster_type: str, floor_level: int, luck: int = 0) -> List[LootDrop]:
        """Generate loot drops for a monster.

        Args:
            monster_type: Type of monster
            floor_level: Current floor level
            luck: Player's luck stat (affects drop rates)

        Returns:
            List of items dropped
        """
        drops = []
        loot_table = self.LOOT_TABLES.get(monster_type, [])

        # Luck increases drop chance by 1% per point
        luck_bonus = luck * 0.01

        for item_data in loot_table:
            # Check if item drops
            drop_chance = float(item_data["chance"]) + luck_bonus
            if random.random() <= drop_chance:
                # Determine quantity
                quantity = item_data["quantity"]
                if isinstance(quantity, tuple):
                    quantity = random.randint(quantity[0], quantity[1])

                # Scale currency with floor level
                if item_data["type"] == "currency":
                    quantity = int(float(quantity) * (1 + (floor_level - 1) * 0.1))

                drops.append(
                    LootDrop(
                        item_name=str(item_data["item"]),
                        quantity=int(quantity),
                        item_type=str(item_data["type"]),
                    )
                )

        return drops
