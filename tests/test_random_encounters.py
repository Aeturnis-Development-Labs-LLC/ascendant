"""Tests for random encounters system."""

import pytest

from src.enums import TerrainType
from src.game.fast_travel import TravelMethod
from src.game.random_encounters import EncounterType, RandomEncounters


class TestRandomEncounters:
    """Tests for random encounter functionality."""

    @pytest.fixture
    def encounters(self):
        """Create a RandomEncounters instance with fixed seed."""
        return RandomEncounters(seed=42)

    def test_no_encounters_on_water(self, encounters):
        """Test that water terrain never generates encounters."""
        haven_pos = (37, 37)
        water_pos = (20, 20)

        # Try many times to ensure it's not just luck
        for _ in range(100):
            encounter = encounters.generate_encounter(water_pos, TerrainType.WATER, haven_pos)
            assert encounter is None

    def test_encounter_generation_by_terrain(self, encounters):
        """Test encounters are generated based on terrain weights."""
        haven_pos = (37, 37)
        test_pos = (40, 40)

        # Generate many encounters to check distribution
        terrain_encounters = {
            TerrainType.PLAINS: [],
            TerrainType.FOREST: [],
            TerrainType.MOUNTAINS: [],
            TerrainType.SHADOWLANDS: [],
            TerrainType.ROADS: [],
        }

        for terrain in terrain_encounters:
            for _ in range(100):
                encounter = encounters.generate_encounter(test_pos, terrain, haven_pos)
                if encounter:
                    terrain_encounters[terrain].append(encounter.encounter_type)

        # Forest should have mostly wild beasts
        forest_beasts = terrain_encounters[TerrainType.FOREST].count(EncounterType.WILD_BEAST)
        assert forest_beasts > 50  # Should be ~70%

        # Roads should have more fortune encounters than other terrains
        road_fortunes = terrain_encounters[TerrainType.ROADS].count(EncounterType.FORTUNE)
        plains_fortunes = terrain_encounters[TerrainType.PLAINS].count(EncounterType.FORTUNE)
        assert road_fortunes > plains_fortunes

        # Shadowlands should have very few fortune encounters
        shadow_fortunes = terrain_encounters[TerrainType.SHADOWLANDS].count(EncounterType.FORTUNE)
        assert shadow_fortunes < 10  # Should be ~5%

    def test_encounter_level_scaling(self, encounters):
        """Test encounter levels scale with distance from haven."""
        # At haven - level 1
        assert encounters.scale_by_distance(0) == 1

        # Close to haven
        assert encounters.scale_by_distance(4) == 1
        assert encounters.scale_by_distance(5) == 2
        assert encounters.scale_by_distance(9) == 2

        # Far from haven
        assert encounters.scale_by_distance(25) == 6
        assert encounters.scale_by_distance(50) == 11

        # Very far - capped at 50
        assert encounters.scale_by_distance(250) == 50
        assert encounters.scale_by_distance(500) == 50

    def test_encounter_descriptions(self, encounters):
        """Test encounters have appropriate descriptions."""
        haven_pos = (37, 37)
        test_pos = (40, 40)

        # Generate encounters on different terrains
        plains_encounter = None
        for _ in range(100):
            enc = encounters.generate_encounter(test_pos, TerrainType.PLAINS, haven_pos)
            if enc and enc.encounter_type == EncounterType.WILD_BEAST:
                plains_encounter = enc
                break

        assert plains_encounter is not None
        assert "wolves" in plains_encounter.description

        # Mountain bandit
        mountain_encounter = None
        for _ in range(100):
            enc = encounters.generate_encounter(test_pos, TerrainType.MOUNTAINS, haven_pos)
            if enc and enc.encounter_type == EncounterType.BANDIT:
                mountain_encounter = enc
                break

        assert mountain_encounter is not None
        assert (
            "cave" in mountain_encounter.description or "Mountain" in mountain_encounter.description
        )

    def test_should_trigger_encounter_walking(self, encounters):
        """Test walking encounter trigger rate."""
        # Single tile - 5% chance
        triggered = 0
        for i in range(1000):
            encounters.rng.seed(i)  # Different seeds for variety
            if encounters.should_trigger_encounter(TravelMethod.WALK, 1):
                triggered += 1

        # Should be around 50 (5%)
        assert 30 < triggered < 70

        # 10 tiles - ~40% chance
        triggered = 0
        for i in range(1000):
            encounters.rng.seed(i)
            if encounters.should_trigger_encounter(TravelMethod.WALK, 10):
                triggered += 1

        # Should be around 400 (40%)
        assert 350 < triggered < 450

    def test_should_trigger_encounter_carriage(self, encounters):
        """Test carriage encounter trigger rate."""
        # Always 20% regardless of distance
        triggered_short = 0
        triggered_long = 0

        for i in range(1000):
            encounters.rng.seed(i)
            if encounters.should_trigger_encounter(TravelMethod.CARRIAGE, 5):
                triggered_short += 1

            encounters.rng.seed(i)  # Same seed
            if encounters.should_trigger_encounter(TravelMethod.CARRIAGE, 50):
                triggered_long += 1

        # Both should be around 200 (20%)
        assert 150 < triggered_short < 250
        assert triggered_short == triggered_long  # Distance doesn't matter

    def test_encounter_properties(self, encounters):
        """Test encounter objects have correct properties."""
        haven_pos = (37, 37)
        test_pos = (50, 50)

        encounter = encounters.generate_encounter(test_pos, TerrainType.FOREST, haven_pos)
        assert encounter is not None

        # Check properties
        assert isinstance(encounter.encounter_type, EncounterType)
        assert encounter.level > 0
        assert encounter.terrain == TerrainType.FOREST
        assert len(encounter.description) > 0

        # Level should match distance scaling
        distance = ((50 - 37) ** 2 + (50 - 37) ** 2) ** 0.5
        expected_level = encounters.scale_by_distance(distance)
        assert encounter.level == expected_level
