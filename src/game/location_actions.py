"""Simple location entry and exit mechanics."""

from typing import Optional, Tuple

from src.models.character import Character
from src.models.location import Location


class LocationActions:
    """Handles entering and exiting locations."""

    def __init__(self):
        """Initialize location actions."""
        self.current_location: Optional[Location] = None
        self.previous_world_position: Optional[Tuple[int, int]] = None

    def enter_location(self, character: Character, location: Location) -> Tuple[bool, str]:
        """Enter a location from the world map.

        Args:
            character: Character entering
            location: Location to enter

        Returns:
            Tuple of (success, message)
        """
        # Check if already in a location
        if self.current_location:
            return (False, "You must exit your current location first.")

        # Check if character can enter
        can_enter, reason = location.can_enter(character)
        if not can_enter:
            return (False, reason)

        # Store previous position and enter
        self.previous_world_position = character.position
        self.current_location = location

        return (True, f"You enter {location.name}.")

    def exit_location(self, character: Character) -> Tuple[bool, str]:
        """Exit current location back to world map.

        Args:
            character: Character exiting

        Returns:
            Tuple of (success, message)
        """
        if not self.current_location:
            return (False, "You are not in a location.")

        # Restore world position
        if self.previous_world_position:
            character.move_to(self.previous_world_position)

        location_name = self.current_location.name
        self.current_location = None
        self.previous_world_position = None

        return (True, f"You exit {location_name}.")

    def get_current_location(self) -> Optional[Location]:
        """Get the current location, if any.

        Returns:
            Current location or None
        """
        return self.current_location

    def is_in_location(self) -> bool:
        """Check if currently inside a location.

        Returns:
            True if in a location
        """
        return self.current_location is not None
