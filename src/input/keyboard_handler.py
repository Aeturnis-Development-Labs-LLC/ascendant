"""Keyboard input handler for character movement."""

from typing import Dict, List, Optional

from src.enums import Direction


class KeyboardHandler:
    """Handles keyboard input and maps keys to game commands."""

    def __init__(self):
        """Initialize keyboard handler with key mappings."""
        self.command_queue: List[Direction] = []
        self.key_map: Dict[str, Direction] = {
            # WASD keys
            'w': Direction.NORTH,
            'W': Direction.NORTH,
            'a': Direction.WEST,
            'A': Direction.WEST,
            's': Direction.SOUTH,
            'S': Direction.SOUTH,
            'd': Direction.EAST,
            'D': Direction.EAST,
            # Arrow keys could be added here with proper key codes
            # For now, focusing on WASD as specified in UTF contract
        }

    def map_key_to_direction(self, key: str) -> Optional[Direction]:
        """Map a key press to a direction.

        Args:
            key: Key character pressed

        Returns:
            Direction enum if valid key, None otherwise
        """
        return self.key_map.get(key)

    def queue_command(self, key: str) -> None:
        """Queue a command based on key press.

        Args:
            key: Key character pressed
        """
        direction = self.map_key_to_direction(key)
        if direction is not None:
            self.command_queue.append(direction)

    def get_next_command(self) -> Optional[Direction]:
        """Get the next command from the queue.

        Returns:
            Next Direction command or None if queue is empty
        """
        if self.command_queue:
            return self.command_queue.pop(0)
        return None

    def clear_queue(self) -> None:
        """Clear all queued commands."""
        self.command_queue.clear()