"""Tests for location entry and exit mechanics."""

from typing import Tuple

import pytest

from src.game.location_actions import LocationActions
from src.models.character import Character
from src.models.location import Location, LocationType


class MockLocation(Location):
    """Mock location for testing."""

    def __init__(self, *args, **kwargs):
        """Initialize mock location."""
        super().__init__(*args, **kwargs)
        self._can_enter_result = (True, "")

    def can_enter(self, character: Character) -> Tuple[bool, str]:
        """Return mock can_enter result."""
        return self._can_enter_result


class TestLocationActions:
    """Tests for location entry/exit functionality."""

    @pytest.fixture
    def location_actions(self):
        """Create a LocationActions instance."""
        return LocationActions()

    @pytest.fixture
    def character(self):
        """Create a test character."""
        character = Character("Test Hero", 10, 10)
        return character

    @pytest.fixture
    def town_location(self):
        """Create a test town location."""
        return MockLocation(
            position=(10, 10),
            name="Test Town",
            location_type=LocationType.VILLAGE,
            description="A small test town.",
        )

    def test_initial_state(self, location_actions):
        """Test initial state has no location."""
        assert location_actions.current_location is None
        assert location_actions.previous_world_position is None
        assert not location_actions.is_in_location()

    def test_enter_location_success(self, location_actions, character, town_location):
        """Test successfully entering a location."""
        success, message = location_actions.enter_location(character, town_location)

        assert success is True
        assert "You enter Test Town" in message
        assert location_actions.current_location == town_location
        assert location_actions.previous_world_position == (10, 10)
        assert location_actions.is_in_location()

    def test_cannot_enter_when_already_in_location(
        self, location_actions, character, town_location
    ):
        """Test cannot enter a new location while in another."""
        # Enter first location
        location_actions.enter_location(character, town_location)

        # Try to enter another location
        other_location = MockLocation(
            position=(20, 20),
            name="Other Place",
            location_type=LocationType.DUNGEON_ENTRANCE,
            description="Another location.",
        )

        success, message = location_actions.enter_location(character, other_location)

        assert success is False
        assert "must exit your current location first" in message
        assert location_actions.current_location == town_location

    def test_location_access_restrictions(self, location_actions, character):
        """Test location can restrict entry."""
        # Create a location that doesn't allow entry
        restricted_location = MockLocation(
            position=(15, 15),
            name="Locked Vault",
            location_type=LocationType.DUNGEON_ENTRANCE,
            description="A heavily guarded vault.",
        )
        # Set can_enter to return False
        restricted_location._can_enter_result = (False, "The vault is sealed.")

        success, message = location_actions.enter_location(character, restricted_location)

        assert success is False
        assert message == "The vault is sealed."
        assert location_actions.current_location is None

    def test_exit_location_success(self, location_actions, character, town_location):
        """Test successfully exiting a location."""
        # Enter location first
        location_actions.enter_location(character, town_location)

        # Change character position to simulate movement inside
        character.move_to((0, 0))

        # Exit location
        success, message = location_actions.exit_location(character)

        assert success is True
        assert "You exit Test Town" in message
        assert location_actions.current_location is None
        assert location_actions.previous_world_position is None
        assert not location_actions.is_in_location()
        # Character position should be restored
        assert character.position == (10, 10)

    def test_cannot_exit_when_not_in_location(self, location_actions, character):
        """Test cannot exit when not in a location."""
        success, message = location_actions.exit_location(character)

        assert success is False
        assert "You are not in a location" in message

    def test_get_current_location(self, location_actions, character, town_location):
        """Test getting current location."""
        assert location_actions.get_current_location() is None

        location_actions.enter_location(character, town_location)
        assert location_actions.get_current_location() == town_location

        location_actions.exit_location(character)
        assert location_actions.get_current_location() is None

    def test_position_restoration_without_previous(self, location_actions, character):
        """Test exit behavior when no previous position stored."""
        # Manually set current location without proper entry
        location_actions.current_location = MockLocation(
            position=(5, 5),
            name="Strange Place",
            location_type=LocationType.VILLAGE,
            description="How did we get here?",
        )
        location_actions.previous_world_position = None

        original_pos = character.position
        success, message = location_actions.exit_location(character)

        assert success is True
        # Position unchanged if no previous position
        assert character.position == original_pos

    def test_multiple_enter_exit_cycles(self, location_actions, character, town_location):
        """Test multiple cycles of entering and exiting."""
        for i in range(3):
            # Set different world positions
            character.move_to((i * 10, i * 10))

            # Enter location
            success, _ = location_actions.enter_location(character, town_location)
            assert success is True
            assert location_actions.previous_world_position == (i * 10, i * 10)

            # Exit location
            success, _ = location_actions.exit_location(character)
            assert success is True
            assert character.position == (i * 10, i * 10)
            assert not location_actions.is_in_location()
