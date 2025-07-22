"""Tests for environmental hazards system."""

import pytest

from src.enums import TerrainType
from src.game.environmental_hazards import EnvironmentalHazards, HazardType, Weather


class TestEnvironmentalHazards:
    """Tests for environmental hazards functionality."""

    @pytest.fixture
    def hazards(self):
        """Create an EnvironmentalHazards instance with fixed seed."""
        return EnvironmentalHazards(seed=42)

    def test_weather_generation_by_terrain(self, hazards):
        """Test weather is generated based on terrain probabilities."""
        weather_counts = {terrain: {weather: 0 for weather in Weather} for terrain in TerrainType}

        # Generate many weather instances
        for terrain in TerrainType:
            for i in range(1000):
                hazards.rng.seed(i)  # Vary the seed
                weather = hazards.generate_weather(terrain)
                weather_counts[terrain][weather] += 1

        # Plains should be mostly clear
        assert weather_counts[TerrainType.PLAINS][Weather.CLEAR] > 600  # ~70%

        # Mountains should have blizzards
        assert weather_counts[TerrainType.MOUNTAINS][Weather.BLIZZARD] > 150  # ~20%
        assert weather_counts[TerrainType.PLAINS][Weather.BLIZZARD] == 0  # No blizzards on plains

        # Shadowlands should have lots of fog
        assert weather_counts[TerrainType.SHADOWLANDS][Weather.FOG] > 400  # ~50%

        # Roads should be mostly clear
        assert weather_counts[TerrainType.ROADS][Weather.CLEAR] > 700  # ~80%

    def test_movement_penalties(self, hazards):
        """Test weather movement penalties."""
        # Clear weather - no penalty
        assert hazards.apply_movement_penalty(Weather.CLEAR, TerrainType.PLAINS) == 1.0

        # Fog - 10% penalty
        assert hazards.apply_movement_penalty(Weather.FOG, TerrainType.PLAINS) == 0.9

        # Storm - 50% penalty
        assert hazards.apply_movement_penalty(Weather.STORM, TerrainType.PLAINS) == 0.5

        # Blizzard - 70% penalty
        assert hazards.apply_movement_penalty(Weather.BLIZZARD, TerrainType.MOUNTAINS) == 0.3

        # Extra penalties for certain terrain-weather combos
        # Mountain storm has extra penalty
        assert hazards.apply_movement_penalty(Weather.STORM, TerrainType.MOUNTAINS) == 0.35

        # Forest fog has extra penalty
        assert abs(hazards.apply_movement_penalty(Weather.FOG, TerrainType.FOREST) - 0.72) < 0.001

    def test_vision_penalties(self, hazards):
        """Test weather vision penalties."""
        assert hazards.apply_vision_penalty(Weather.CLEAR) == 1.0
        assert hazards.apply_vision_penalty(Weather.FOG) == 0.5
        assert hazards.apply_vision_penalty(Weather.STORM) == 0.7
        assert hazards.apply_vision_penalty(Weather.BLIZZARD) == 0.3

    def test_hazard_checks_by_terrain(self, hazards):
        """Test hazard occurrences by terrain type."""
        hazard_counts = {
            TerrainType.MOUNTAINS: 0,
            TerrainType.SHADOWLANDS: 0,
            TerrainType.FOREST: 0,
            TerrainType.PLAINS: 0,
        }

        # Run many checks
        for terrain in hazard_counts:
            for i in range(1000):
                hazards.rng.seed(i)
                hazard = hazards.check_for_hazard(terrain)
                if hazard:
                    hazard_counts[terrain] += 1

        # Mountains should have ~5% avalanche chance
        assert 30 < hazard_counts[TerrainType.MOUNTAINS] < 70

        # Shadowlands should have ~3% quicksand chance
        assert 15 < hazard_counts[TerrainType.SHADOWLANDS] < 45

        # Forest should have ~1% fire chance
        assert 5 < hazard_counts[TerrainType.FOREST] < 20

        # Plains should have no hazards
        assert hazard_counts[TerrainType.PLAINS] == 0

    def test_hazard_types_match_terrain(self, hazards):
        """Test correct hazard types occur on correct terrain."""
        # Mountain hazards
        for i in range(100):
            hazards.rng.seed(i)
            hazard = hazards.check_for_hazard(TerrainType.MOUNTAINS)
            if hazard:
                assert hazard == HazardType.AVALANCHE

        # Shadowlands hazards
        for i in range(100):
            hazards.rng.seed(i)
            hazard = hazards.check_for_hazard(TerrainType.SHADOWLANDS)
            if hazard:
                assert hazard == HazardType.QUICKSAND

        # Forest hazards
        for i in range(100):
            hazards.rng.seed(i)
            hazard = hazards.check_for_hazard(TerrainType.FOREST)
            if hazard:
                assert hazard == HazardType.FOREST_FIRE

    def test_hazard_damage_values(self, hazards):
        """Test hazard damage is appropriate."""
        assert hazards.get_hazard_damage(HazardType.AVALANCHE) == 20  # High
        assert hazards.get_hazard_damage(HazardType.QUICKSAND) == 10  # Medium
        assert hazards.get_hazard_damage(HazardType.FOREST_FIRE) == 15  # Medium-high

        # Unknown hazard type
        assert hazards.get_hazard_damage(None) == 5  # type: ignore

    def test_hazard_descriptions(self, hazards):
        """Test hazard descriptions are appropriate."""
        desc = hazards.get_hazard_description(HazardType.AVALANCHE)
        assert "snow" in desc.lower() or "avalanche" in desc.lower()

        desc = hazards.get_hazard_description(HazardType.QUICKSAND)
        assert "quicksand" in desc.lower() or "ground" in desc.lower()

        desc = hazards.get_hazard_description(HazardType.FOREST_FIRE)
        assert "fire" in desc.lower() or "flame" in desc.lower()

    def test_weather_affects_encounters(self, hazards):
        """Test weather modifies encounter rates."""
        assert hazards.weather_affects_encounters(Weather.CLEAR) == 1.0  # Normal
        assert hazards.weather_affects_encounters(Weather.FOG) == 1.2  # 20% more
        assert hazards.weather_affects_encounters(Weather.STORM) == 0.5  # 50% less
        assert hazards.weather_affects_encounters(Weather.BLIZZARD) == 0.2  # 80% less

    def test_current_weather_tracking(self, hazards):
        """Test that current weather is tracked."""
        assert hazards.current_weather == Weather.CLEAR  # Default

        # Generate weather updates current
        weather = hazards.generate_weather(TerrainType.MOUNTAINS)
        assert hazards.current_weather == weather

        # Different terrain can change weather
        new_weather = hazards.generate_weather(TerrainType.PLAINS)
        assert hazards.current_weather == new_weather
