"""Floor generation system for dungeon levels."""

import random
from typing import Dict, List, Optional, Tuple

from src.enums import TileType
from src.models.tile import Tile


class Room:
    """Represents a rectangular room in the floor."""

    def __init__(self, x: int, y: int, width: int, height: int):
        """Initialize a room with position and dimensions.

        Args:
            x: Left coordinate of the room
            y: Top coordinate of the room
            width: Width of the room in tiles
            height: Height of the room in tiles
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def x2(self) -> int:
        """Get the right edge coordinate."""
        return self.x + self.width - 1

    @property
    def y2(self) -> int:
        """Get the bottom edge coordinate."""
        return self.y + self.height - 1

    def overlaps(self, other: "Room", min_distance: int = 1) -> bool:
        """Check if this room overlaps with another room.

        Args:
            other: Another room to check overlap with
            min_distance: Minimum distance required between rooms

        Returns:
            True if rooms are too close, False otherwise
        """
        # Expand the room boundaries by min_distance on all sides
        # to ensure rooms have space between them
        self_x1 = self.x - min_distance
        self_y1 = self.y - min_distance
        self_x2 = self.x2 + min_distance
        self_y2 = self.y2 + min_distance

        other_x1 = other.x - min_distance
        other_y1 = other.y - min_distance
        other_x2 = other.x2 + min_distance
        other_y2 = other.y2 + min_distance

        # Check if one room is to the left of the other
        if self_x2 < other_x1 or other_x2 < self_x1:
            return False
        # Check if one room is above the other
        if self_y2 < other_y1 or other_y2 < self_y1:
            return False
        return True

    def __repr__(self) -> str:
        """Return string representation of the room."""
        return f"Room({self.x}, {self.y}, {self.width}x{self.height})"


class Floor:
    """Represents a single floor/level of the dungeon."""

    FLOOR_WIDTH = 20
    FLOOR_HEIGHT = 20
    MIN_ROOMS = 5
    MAX_ROOMS = 10
    MIN_ROOM_SIZE = 3
    MAX_ROOM_SIZE = 8
    EDGE_BUFFER = 1

    def __init__(self, seed: int):
        """Initialize a new floor with the given seed.

        Args:
            seed: Random seed for reproducible generation
        """
        self.seed = seed
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        self.rooms: List[Room] = []
        self._random = random.Random(seed)

    def generate(self) -> None:
        """Generate the floor layout with rooms."""
        # Initialize all tiles as walls
        for y in range(self.FLOOR_HEIGHT):
            for x in range(self.FLOOR_WIDTH):
                self.tiles[(x, y)] = Tile(x, y, TileType.WALL)

        # Generate rooms
        self._generate_rooms()

        # Carve out rooms from the walls
        self._carve_rooms()

    def _generate_rooms(self) -> None:
        """Generate random non-overlapping rooms."""
        room_count = self._random.randint(self.MIN_ROOMS, self.MAX_ROOMS)

        attempts = 0
        max_attempts = 100

        while len(self.rooms) < room_count and attempts < max_attempts:
            attempts += 1

            # Generate random room dimensions
            width = self._random.randint(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)
            height = self._random.randint(self.MIN_ROOM_SIZE, self.MAX_ROOM_SIZE)

            # Generate random position (accounting for edge buffer)
            max_x = self.FLOOR_WIDTH - width - self.EDGE_BUFFER
            max_y = self.FLOOR_HEIGHT - height - self.EDGE_BUFFER

            if max_x <= self.EDGE_BUFFER or max_y <= self.EDGE_BUFFER:
                continue

            x = self._random.randint(self.EDGE_BUFFER, max_x)
            y = self._random.randint(self.EDGE_BUFFER, max_y)

            new_room = Room(x, y, width, height)

            # Check if room overlaps with any existing room
            if not any(new_room.overlaps(room) for room in self.rooms):
                self.rooms.append(new_room)

    def _carve_rooms(self) -> None:
        """Carve out rooms by setting their tiles to FLOOR type."""
        for room in self.rooms:
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    if (x, y) in self.tiles:
                        self.tiles[(x, y)] = Tile(x, y, TileType.FLOOR)

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get the tile at the specified coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            The tile at the position, or None if out of bounds
        """
        return self.tiles.get((x, y))

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is valid within the floor.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if position is within floor bounds
        """
        return 0 <= x < self.FLOOR_WIDTH and 0 <= y < self.FLOOR_HEIGHT
