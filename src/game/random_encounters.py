"""Random encounter system for world map travel."""

import random
from enum import Enum, auto
from typing import Optional, Tuple

from src.enums import TerrainType
from src.game.fast_travel import TravelMethod


class EncounterType(Enum):
    """Types of random encounters."""

    WILD_BEAST = auto()  # Combat encounter with animals
    BANDIT = auto()  # Combat encounter with bandits
    FORTUNE = auto()  # Positive encounter (merchant, treasure)


class Encounter:
    """Represents a random encounter."""

    def __init__(
        self,
        encounter_type: EncounterType,
        level: int,
        description: str,
        terrain: TerrainType,
    ):
        """Initialize an encounter.

        Args:
            encounter_type: Type of encounter
            level: Difficulty level
            description: Flavor text
            terrain: Terrain where encounter occurred
        """
        self.encounter_type = encounter_type
        self.level = level
        self.description = description
        self.terrain = terrain


class RandomEncounters:
    """Manages random encounter generation."""

    # Encounter chances by travel method (per GAME-WORLD-006)
    ENCOUNTER_CHANCE_BY_METHOD = {
        TravelMethod.WALK: 0.05,  # 5% per tile
        TravelMethod.CARRIAGE: 0.20,  # 20% total
    }

    # Encounter type weights by terrain
    TERRAIN_ENCOUNTER_WEIGHTS = {
        TerrainType.PLAINS: {
            EncounterType.WILD_BEAST: 0.5,
            EncounterType.BANDIT: 0.3,
            EncounterType.FORTUNE: 0.2,
        },
        TerrainType.FOREST: {
            EncounterType.WILD_BEAST: 0.7,
            EncounterType.BANDIT: 0.2,
            EncounterType.FORTUNE: 0.1,
        },
        TerrainType.MOUNTAINS: {
            EncounterType.WILD_BEAST: 0.4,
            EncounterType.BANDIT: 0.5,
            EncounterType.FORTUNE: 0.1,
        },
        TerrainType.SHADOWLANDS: {
            EncounterType.WILD_BEAST: 0.8,
            EncounterType.BANDIT: 0.15,
            EncounterType.FORTUNE: 0.05,
        },
        TerrainType.ROADS: {
            EncounterType.WILD_BEAST: 0.2,
            EncounterType.BANDIT: 0.4,
            EncounterType.FORTUNE: 0.4,
        },
        TerrainType.WATER: {
            EncounterType.WILD_BEAST: 0.0,
            EncounterType.BANDIT: 0.0,
            EncounterType.FORTUNE: 0.0,  # No encounters on water
        },
    }

    # Encounter descriptions by type and terrain
    ENCOUNTER_DESCRIPTIONS = {
        (
            EncounterType.WILD_BEAST,
            TerrainType.PLAINS,
        ): "A pack of wild wolves emerges from the tall grass!",
        (
            EncounterType.WILD_BEAST,
            TerrainType.FOREST,
        ): "A massive bear blocks your path through the trees!",
        (EncounterType.WILD_BEAST, TerrainType.MOUNTAINS): "Mountain lions prowl the rocky crags!",
        (
            EncounterType.WILD_BEAST,
            TerrainType.SHADOWLANDS,
        ): "Corrupted beasts with glowing eyes attack!",
        (EncounterType.WILD_BEAST, TerrainType.ROADS): "Rabid dogs block the road ahead!",
        (EncounterType.BANDIT, TerrainType.PLAINS): "Bandits on horseback surround you!",
        (EncounterType.BANDIT, TerrainType.FOREST): "Highwaymen drop from the trees!",
        (
            EncounterType.BANDIT,
            TerrainType.MOUNTAINS,
        ): "Mountain bandits emerge from a hidden cave!",
        (
            EncounterType.BANDIT,
            TerrainType.SHADOWLANDS,
        ): "Desperate outlaws attack from the shadows!",
        (EncounterType.BANDIT, TerrainType.ROADS): "A bandit roadblock demands your gold!",
        (
            EncounterType.FORTUNE,
            TerrainType.PLAINS,
        ): "You find a merchant caravan willing to trade!",
        (EncounterType.FORTUNE, TerrainType.FOREST): "You discover a hidden cache of supplies!",
        (
            EncounterType.FORTUNE,
            TerrainType.MOUNTAINS,
        ): "An old hermit offers valuable information!",
        (
            EncounterType.FORTUNE,
            TerrainType.SHADOWLANDS,
        ): "You find the remains of a less fortunate traveler...",
        (EncounterType.FORTUNE, TerrainType.ROADS): "A friendly merchant offers a good deal!",
    }

    def __init__(self, seed: Optional[int] = None):
        """Initialize the encounter system.

        Args:
            seed: Random seed for reproducible encounters
        """
        self.rng = random.Random(seed)

    def generate_encounter(
        self, position: Tuple[int, int], terrain: TerrainType, haven_position: Tuple[int, int]
    ) -> Optional[Encounter]:
        """Generate an encounter based on position and terrain.

        Args:
            position: Current position (x, y)
            terrain: Current terrain type
            haven_position: Safe Haven position for distance scaling

        Returns:
            Encounter if one occurs, None otherwise
        """
        # No encounters on water
        if terrain == TerrainType.WATER:
            return None

        # Get encounter type based on terrain weights
        weights = self.TERRAIN_ENCOUNTER_WEIGHTS.get(
            terrain, self.TERRAIN_ENCOUNTER_WEIGHTS[TerrainType.PLAINS]
        )

        # Choose encounter type
        encounter_types = list(weights.keys())
        encounter_weights = list(weights.values())

        # If all weights are 0 (shouldn't happen), return None
        if sum(encounter_weights) == 0:
            return None

        encounter_type = self.rng.choices(encounter_types, weights=encounter_weights)[0]

        # Calculate distance from haven for level scaling
        distance = self._calculate_distance(position, haven_position)
        level = self.scale_by_distance(distance)

        # Get description
        description_key = (encounter_type, terrain)
        description = self.ENCOUNTER_DESCRIPTIONS.get(
            description_key, f"A {encounter_type.name.lower()} encounter!"
        )

        return Encounter(encounter_type, level, description, terrain)

    def scale_by_distance(self, distance_from_haven: float) -> int:
        """Scale encounter difficulty by distance from Safe Haven.

        Args:
            distance_from_haven: Distance in tiles

        Returns:
            Scaled encounter level (1-50)
        """
        # Base level 1, +1 per 5 tiles from haven, max 50
        level = 1 + int(distance_from_haven / 5)
        return min(level, 50)

    def _calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Euclidean distance between positions.

        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)

        Returns:
            Distance in tiles
        """
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        return float((dx * dx + dy * dy) ** 0.5)

    def should_trigger_encounter(self, method: TravelMethod, tiles_traveled: int) -> bool:
        """Determine if an encounter should trigger.

        Args:
            method: Travel method used
            tiles_traveled: Number of tiles traveled

        Returns:
            True if encounter should trigger
        """
        if method == TravelMethod.WALK:
            # 5% per tile, compound probability
            no_encounter_chance = (
                1 - self.ENCOUNTER_CHANCE_BY_METHOD[TravelMethod.WALK]
            ) ** tiles_traveled
            return self.rng.random() > no_encounter_chance
        else:  # TravelMethod.CARRIAGE
            # Flat 20% for entire trip
            return self.rng.random() < self.ENCOUNTER_CHANCE_BY_METHOD[TravelMethod.CARRIAGE]
