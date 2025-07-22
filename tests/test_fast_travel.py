"""Tests for fast travel system."""

import pytest

from src.game.fast_travel import FastTravel, TravelMethod


class TestFastTravel:
    """Tests for fast travel functionality."""

    @pytest.fixture
    def fast_travel(self):
        """Create a FastTravel instance."""
        return FastTravel()

    def test_walk_cost_is_free(self, fast_travel):
        """Test walking has no gold cost."""
        assert fast_travel.calculate_travel_cost(10.0, TravelMethod.WALK) == 0
        assert fast_travel.calculate_travel_cost(100.0, TravelMethod.WALK) == 0
        assert fast_travel.calculate_travel_cost(0.0, TravelMethod.WALK) == 0

    def test_carriage_cost_calculation(self, fast_travel):
        """Test carriage cost is 50g per 10 tiles."""
        # Exact multiples
        assert fast_travel.calculate_travel_cost(10.0, TravelMethod.CARRIAGE) == 50
        assert fast_travel.calculate_travel_cost(20.0, TravelMethod.CARRIAGE) == 100
        assert fast_travel.calculate_travel_cost(50.0, TravelMethod.CARRIAGE) == 250

        # Partial distances
        assert fast_travel.calculate_travel_cost(5.0, TravelMethod.CARRIAGE) == 25
        assert fast_travel.calculate_travel_cost(15.0, TravelMethod.CARRIAGE) == 75
        assert fast_travel.calculate_travel_cost(1.0, TravelMethod.CARRIAGE) == 5

        # Zero distance
        assert fast_travel.calculate_travel_cost(0.0, TravelMethod.CARRIAGE) == 0

    def test_travel_time_walking(self, fast_travel):
        """Test walking travel time calculation."""
        # Base case - no terrain modifier
        assert fast_travel.travel_time(10.0, TravelMethod.WALK, 1.0) == 10.0

        # With terrain modifiers
        assert fast_travel.travel_time(10.0, TravelMethod.WALK, 2.0) == 5.0  # Roads
        assert fast_travel.travel_time(10.0, TravelMethod.WALK, 0.5) == 20.0  # Mountains

    def test_travel_time_carriage(self, fast_travel):
        """Test carriage is 3x faster than walking."""
        # Base case
        walk_time = fast_travel.travel_time(30.0, TravelMethod.WALK, 1.0)
        carriage_time = fast_travel.travel_time(30.0, TravelMethod.CARRIAGE, 1.0)
        assert carriage_time == walk_time / 3.0

        # With terrain modifier
        assert fast_travel.travel_time(30.0, TravelMethod.CARRIAGE, 2.0) == 5.0

    def test_encounter_check_walking(self, fast_travel):
        """Test walking encounter rate is 5% per tile."""
        # Very low rng_value triggers encounter (rng < encounter_chance)
        assert fast_travel.trigger_encounter_check(TravelMethod.WALK, 1.0, 0.01)

        # High rng_value doesn't trigger
        assert not fast_travel.trigger_encounter_check(TravelMethod.WALK, 1.0, 0.99)

        # Multi-tile trip compounds probability
        # 2 tiles: 1 - 0.95^2 = 0.0975 chance
        assert fast_travel.trigger_encounter_check(TravelMethod.WALK, 2.0, 0.05)
        assert not fast_travel.trigger_encounter_check(TravelMethod.WALK, 2.0, 0.98)

        # 10 tiles: 1 - 0.95^10 ≈ 0.401 chance
        assert fast_travel.trigger_encounter_check(TravelMethod.WALK, 10.0, 0.4)
        assert not fast_travel.trigger_encounter_check(TravelMethod.WALK, 10.0, 0.5)

    def test_encounter_check_carriage(self, fast_travel):
        """Test carriage has flat 20% encounter chance."""
        # Below 20% chance triggers (rng < 0.20)
        assert fast_travel.trigger_encounter_check(TravelMethod.CARRIAGE, 10.0, 0.19)
        assert fast_travel.trigger_encounter_check(TravelMethod.CARRIAGE, 50.0, 0.19)

        # Above 20% doesn't trigger
        assert not fast_travel.trigger_encounter_check(TravelMethod.CARRIAGE, 10.0, 0.21)
        assert not fast_travel.trigger_encounter_check(TravelMethod.CARRIAGE, 50.0, 0.21)

        # Distance doesn't matter for carriage
        assert fast_travel.trigger_encounter_check(TravelMethod.CARRIAGE, 1.0, 0.19)
        assert not fast_travel.trigger_encounter_check(TravelMethod.CARRIAGE, 100.0, 0.21)

    def test_can_afford_travel(self, fast_travel):
        """Test affordability check."""
        # Walking is always affordable
        assert fast_travel.can_afford_travel(0, 100.0, TravelMethod.WALK)
        assert fast_travel.can_afford_travel(1000, 100.0, TravelMethod.WALK)

        # Carriage requires gold
        assert fast_travel.can_afford_travel(50, 10.0, TravelMethod.CARRIAGE)  # Exact
        assert fast_travel.can_afford_travel(51, 10.0, TravelMethod.CARRIAGE)  # Extra
        assert not fast_travel.can_afford_travel(49, 10.0, TravelMethod.CARRIAGE)  # Not enough

        # Longer distances
        assert fast_travel.can_afford_travel(250, 50.0, TravelMethod.CARRIAGE)
        assert not fast_travel.can_afford_travel(249, 50.0, TravelMethod.CARRIAGE)

    def test_carriage_route_tiles(self, fast_travel):
        """Test manhattan distance calculation for carriage routes."""
        # Same position
        assert fast_travel.get_carriage_route_tiles((0, 0), (0, 0)) == 0

        # Horizontal/vertical movement
        assert fast_travel.get_carriage_route_tiles((0, 0), (10, 0)) == 10
        assert fast_travel.get_carriage_route_tiles((0, 0), (0, 10)) == 10

        # Diagonal movement uses manhattan distance
        assert fast_travel.get_carriage_route_tiles((0, 0), (3, 4)) == 7
        assert fast_travel.get_carriage_route_tiles((10, 10), (15, 20)) == 15

        # Negative coordinates
        assert fast_travel.get_carriage_route_tiles((-5, -5), (5, 5)) == 20

    def test_validate_travel_destination(self, fast_travel):
        """Test travel destination validation."""
        discovered = {(0, 0), (10, 10), (20, 20)}

        # Can travel to discovered locations
        can_travel, reason = fast_travel.validate_travel_destination((10, 10), discovered)
        assert can_travel is True
        assert reason == ""

        # Cannot travel to undiscovered locations
        can_travel, reason = fast_travel.validate_travel_destination((30, 30), discovered)
        assert can_travel is False
        assert "undiscovered" in reason
