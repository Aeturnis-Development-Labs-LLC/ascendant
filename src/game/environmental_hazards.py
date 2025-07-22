"""Environmental hazards system for world map."""

import random
from enum import Enum, auto
from typing import Dict, Optional

from src.enums import TerrainType


class Weather(Enum):
    """Weather conditions affecting visibility and movement."""

    CLEAR = auto()  # Normal conditions
    FOG = auto()  # Reduced vision
    STORM = auto()  # Reduced movement speed
    BLIZZARD = auto()  # Mountain-specific, severe penalties


class HazardType(Enum):
    """Types of environmental hazards."""

    AVALANCHE = auto()  # Mountain hazard
    QUICKSAND = auto()  # Swamp/shadowlands hazard
    FOREST_FIRE = auto()  # Forest hazard


class EnvironmentalHazards:
    """Manages weather and environmental hazards."""

    # Weather probabilities by terrain (per GAME-WORLD-016)
    WEATHER_CHANCES: Dict[TerrainType, Dict[Weather, float]] = {
        TerrainType.PLAINS: {
            Weather.CLEAR: 0.7,
            Weather.FOG: 0.2,
            Weather.STORM: 0.1,
            Weather.BLIZZARD: 0.0,
        },
        TerrainType.FOREST: {
            Weather.CLEAR: 0.6,
            Weather.FOG: 0.3,
            Weather.STORM: 0.1,
            Weather.BLIZZARD: 0.0,
        },
        TerrainType.MOUNTAINS: {
            Weather.CLEAR: 0.4,
            Weather.FOG: 0.2,
            Weather.STORM: 0.2,
            Weather.BLIZZARD: 0.2,
        },
        TerrainType.SHADOWLANDS: {
            Weather.CLEAR: 0.3,
            Weather.FOG: 0.5,
            Weather.STORM: 0.2,
            Weather.BLIZZARD: 0.0,
        },
        TerrainType.ROADS: {
            Weather.CLEAR: 0.8,
            Weather.FOG: 0.1,
            Weather.STORM: 0.1,
            Weather.BLIZZARD: 0.0,
        },
        TerrainType.WATER: {
            Weather.CLEAR: 0.7,
            Weather.FOG: 0.2,
            Weather.STORM: 0.1,
            Weather.BLIZZARD: 0.0,
        },
    }

    # Movement penalties by weather condition
    WEATHER_MOVEMENT_PENALTY: Dict[Weather, float] = {
        Weather.CLEAR: 1.0,  # No penalty
        Weather.FOG: 0.9,  # 10% slower
        Weather.STORM: 0.5,  # 50% slower
        Weather.BLIZZARD: 0.3,  # 70% slower
    }

    # Vision penalties by weather condition
    WEATHER_VISION_PENALTY: Dict[Weather, float] = {
        Weather.CLEAR: 1.0,  # No penalty
        Weather.FOG: 0.5,  # 50% reduced vision
        Weather.STORM: 0.7,  # 30% reduced vision
        Weather.BLIZZARD: 0.3,  # 70% reduced vision
    }

    # Hazard chances by terrain (chance per movement)
    HAZARD_CHANCES: Dict[TerrainType, Dict[HazardType, float]] = {
        TerrainType.MOUNTAINS: {HazardType.AVALANCHE: 0.05},  # 5% chance
        TerrainType.SHADOWLANDS: {HazardType.QUICKSAND: 0.03},  # 3% chance
        TerrainType.FOREST: {HazardType.FOREST_FIRE: 0.01},  # 1% chance (rare)
    }

    def __init__(self, seed: Optional[int] = None):
        """Initialize the hazards system.

        Args:
            seed: Random seed for reproducible weather
        """
        self.rng = random.Random(seed)
        self.current_weather = Weather.CLEAR

    def generate_weather(self, terrain: TerrainType) -> Weather:
        """Generate weather for current terrain.

        Args:
            terrain: Current terrain type

        Returns:
            Weather condition
        """
        weather_probs = self.WEATHER_CHANCES.get(terrain, self.WEATHER_CHANCES[TerrainType.PLAINS])

        weathers = list(weather_probs.keys())
        weights = list(weather_probs.values())

        self.current_weather = self.rng.choices(weathers, weights=weights)[0]
        return self.current_weather

    def apply_movement_penalty(self, weather: Weather, terrain: TerrainType) -> float:
        """Calculate total movement penalty from weather and terrain.

        Args:
            weather: Current weather condition
            terrain: Current terrain type

        Returns:
            Movement speed multiplier (0.0 to 1.0)
        """
        weather_penalty = self.WEATHER_MOVEMENT_PENALTY.get(weather, 1.0)

        # Additional terrain-specific penalties during bad weather
        terrain_weather_penalty = 1.0
        if weather == Weather.STORM and terrain == TerrainType.MOUNTAINS:
            terrain_weather_penalty = 0.7  # Extra 30% penalty in mountain storms
        elif weather == Weather.FOG and terrain == TerrainType.FOREST:
            terrain_weather_penalty = 0.8  # Extra 20% penalty in forest fog

        return weather_penalty * terrain_weather_penalty

    def apply_vision_penalty(self, weather: Weather) -> float:
        """Calculate vision radius penalty from weather.

        Args:
            weather: Current weather condition

        Returns:
            Vision radius multiplier (0.0 to 1.0)
        """
        return self.WEATHER_VISION_PENALTY.get(weather, 1.0)

    def check_for_hazard(self, terrain: TerrainType) -> Optional[HazardType]:
        """Check if a hazard triggers based on terrain.

        Args:
            terrain: Current terrain type

        Returns:
            Hazard type if one triggers, None otherwise
        """
        hazards = self.HAZARD_CHANCES.get(terrain, {})

        for hazard_type, chance in hazards.items():
            if self.rng.random() < chance:
                return hazard_type

        return None

    def get_hazard_damage(self, hazard: HazardType) -> int:
        """Get damage dealt by a hazard.

        Args:
            hazard: Type of hazard

        Returns:
            Damage amount
        """
        hazard_damage = {
            HazardType.AVALANCHE: 20,  # High damage
            HazardType.QUICKSAND: 10,  # Medium damage
            HazardType.FOREST_FIRE: 15,  # Medium-high damage
        }
        return hazard_damage.get(hazard, 5)

    def get_hazard_description(self, hazard: HazardType) -> str:
        """Get flavor text for a hazard.

        Args:
            hazard: Type of hazard

        Returns:
            Description text
        """
        descriptions = {
            HazardType.AVALANCHE: (
                "A thunderous roar fills the air as snow cascades down the mountain!"
            ),
            HazardType.QUICKSAND: "The ground beneath you gives way to treacherous quicksand!",
            HazardType.FOREST_FIRE: "Smoke fills the air as flames spread through the trees!",
        }
        return descriptions.get(hazard, "You encounter a dangerous hazard!")

    def weather_affects_encounters(self, weather: Weather) -> float:
        """Get encounter rate modifier based on weather.

        Args:
            weather: Current weather condition

        Returns:
            Encounter rate multiplier
        """
        # Bad weather reduces encounter chances (creatures seek shelter)
        weather_encounter_modifier = {
            Weather.CLEAR: 1.0,  # Normal encounters
            Weather.FOG: 1.2,  # 20% more encounters (reduced visibility)
            Weather.STORM: 0.5,  # 50% fewer encounters
            Weather.BLIZZARD: 0.2,  # 80% fewer encounters
        }
        return weather_encounter_modifier.get(weather, 1.0)
