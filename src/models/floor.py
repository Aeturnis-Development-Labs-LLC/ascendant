"""Floor generation system for dungeon levels."""

import random
from collections import deque
from typing import Dict, List, Optional, Set, Tuple

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

    def connect_rooms(self) -> None:
        """Connect all rooms with L-shaped corridors."""
        if len(self.rooms) < 2:
            return

        # Connect each room to the next one
        for i in range(len(self.rooms) - 1):
            room1 = self.rooms[i]
            room2 = self.rooms[i + 1]

            # Get center points of rooms
            x1 = room1.x + room1.width // 2
            y1 = room1.y + room1.height // 2
            x2 = room2.x + room2.width // 2
            y2 = room2.y + room2.height // 2

            # Create L-shaped corridor (horizontal then vertical)
            # Randomly choose whether to go horizontal first or vertical first
            if self._random.random() < 0.5:
                # Horizontal first
                self._create_horizontal_corridor(x1, x2, y1)
                self._create_vertical_corridor(y1, y2, x2)
            else:
                # Vertical first
                self._create_vertical_corridor(y1, y2, x1)
                self._create_horizontal_corridor(x1, x2, y2)

    def _create_horizontal_corridor(self, x1: int, x2: int, y: int) -> None:
        """Create a horizontal corridor."""
        start = min(x1, x2)
        end = max(x1, x2) + 1
        for x in range(start, end):
            if self.is_valid_position(x, y):
                self.tiles[(x, y)] = Tile(x, y, TileType.FLOOR)

    def _create_vertical_corridor(self, y1: int, y2: int, x: int) -> None:
        """Create a vertical corridor."""
        start = min(y1, y2)
        end = max(y1, y2) + 1
        for y in range(start, end):
            if self.is_valid_position(x, y):
                self.tiles[(x, y)] = Tile(x, y, TileType.FLOOR)

    def place_stairs(self) -> None:
        """Place stairs in a random room."""
        if not self.rooms:
            return

        # Select a random room
        room = self._random.choice(self.rooms)

        # Try to place stairs in the center of the room
        center_x = room.x + room.width // 2
        center_y = room.y + room.height // 2

        # Check if center is available
        if self.tiles[(center_x, center_y)].tile_type == TileType.FLOOR:
            self.tiles[(center_x, center_y)] = Tile(center_x, center_y, TileType.STAIRS_UP)
        else:
            # Find any floor tile in the room
            floor_tiles = []
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    if self.tiles[(x, y)].tile_type == TileType.FLOOR:
                        floor_tiles.append((x, y))

            if floor_tiles:
                x, y = self._random.choice(floor_tiles)
                self.tiles[(x, y)] = Tile(x, y, TileType.STAIRS_UP)

    def is_fully_connected(self) -> bool:
        """Check if all rooms are connected to each other.

        Returns:
            True if all rooms are reachable from any other room
        """
        if len(self.rooms) < 2:
            return True

        # Start from the first room
        start_room = self.rooms[0]
        start_x = start_room.x + start_room.width // 2
        start_y = start_room.y + start_room.height // 2

        # Use BFS to find all reachable floor tiles
        visited: Set[Tuple[int, int]] = set()
        queue = deque([(start_x, start_y)])

        while queue:
            x, y = queue.popleft()
            if (x, y) in visited:
                continue
            visited.add((x, y))

            # Check all adjacent positions
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x, next_y = x + dx, y + dy
                if (next_x, next_y) not in visited and self.is_valid_position(next_x, next_y):
                    tile = self.tiles.get((next_x, next_y))
                    if tile and tile.tile_type in [TileType.FLOOR, TileType.STAIRS_UP]:
                        queue.append((next_x, next_y))

        # Check if we can reach all rooms
        for room in self.rooms:
            # Check if at least one tile in the room was visited
            room_visited = False
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    if (x, y) in visited:
                        room_visited = True
                        break
                if room_visited:
                    break

            if not room_visited:
                return False

        return True
