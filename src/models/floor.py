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

    def center(self) -> Tuple[int, int]:
        """Get the center point of the room."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is inside this room."""
        return self.x <= x <= self.x2 and self.y <= y <= self.y2

    def __repr__(self) -> str:
        """Return string representation of the room."""
        return f"Room({self.x}, {self.y}, {self.width}x{self.height})"


class Floor:
    """Represents a single floor/level of the dungeon."""

    FLOOR_WIDTH = 50
    FLOOR_HEIGHT = 50
    MIN_ROOMS = 8
    MAX_ROOMS = 12
    MIN_ROOM_SIZE = 4
    MAX_ROOM_SIZE = 10
    EDGE_BUFFER = 2

    # Direct access to constants is simpler than properties
    width = FLOOR_WIDTH
    height = FLOOR_HEIGHT

    def __init__(
        self,
        seed: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        level: int = 1,
    ):
        """Initialize a new floor with the given parameters.

        Args:
            seed: Random seed for reproducible generation (optional)
            width: Floor width (uses FLOOR_WIDTH if not specified)
            height: Floor height (uses FLOOR_HEIGHT if not specified)
            level: Floor level number (default 1)
        """
        if seed is None:
            seed = random.randint(0, 999999)
        self._seed = seed
        self.seed = seed  # Keep both for compatibility
        self.level = level
        self.width = width or self.FLOOR_WIDTH
        self.height = height or self.FLOOR_HEIGHT
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        self.rooms: List[Room] = []
        self._random = random.Random(seed)

    def generate(self) -> None:
        """Generate the floor layout with rooms."""
        # Initialize all tiles as walls
        for y in range(self.height):
            for x in range(self.width):
                self.tiles[(x, y)] = Tile(x, y, TileType.WALL)

        # Generate rooms
        self._generate_rooms()

        # Carve out rooms from the walls
        self._carve_rooms()

        # Connect rooms with corridors
        self.connect_rooms()

        # Place stairs
        self.place_stairs()

        # Place traps and chests
        self.place_traps(0.02)  # 2% of floor tiles
        self.place_chests(5)  # 5 chests per floor

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
            max_x = self.width - width - self.EDGE_BUFFER
            max_y = self.height - height - self.EDGE_BUFFER

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
        return 0 <= x < self.width and 0 <= y < self.height

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
        """Place stairs up and down in different rooms."""
        if len(self.rooms) < 2:
            return

        # Select two different rooms
        selected_rooms = self._random.sample(self.rooms, 2)

        # Place stairs up in first room
        room_up = selected_rooms[0]
        center_x = room_up.x + room_up.width // 2
        center_y = room_up.y + room_up.height // 2

        if self.tiles[(center_x, center_y)].tile_type == TileType.FLOOR:
            self.tiles[(center_x, center_y)] = Tile(center_x, center_y, TileType.STAIRS_UP)
        else:
            # Find any floor tile in the room
            floor_tiles = []
            for y in range(room_up.y, room_up.y + room_up.height):
                for x in range(room_up.x, room_up.x + room_up.width):
                    if self.tiles[(x, y)].tile_type == TileType.FLOOR:
                        floor_tiles.append((x, y))
            if floor_tiles:
                x, y = self._random.choice(floor_tiles)
                self.tiles[(x, y)] = Tile(x, y, TileType.STAIRS_UP)

        # Place stairs down in second room
        room_down = selected_rooms[1]
        center_x = room_down.x + room_down.width // 2
        center_y = room_down.y + room_down.height // 2

        if self.tiles[(center_x, center_y)].tile_type == TileType.FLOOR:
            self.tiles[(center_x, center_y)] = Tile(center_x, center_y, TileType.STAIRS_DOWN)
        else:
            # Find any floor tile in the room
            floor_tiles = []
            for y in range(room_down.y, room_down.y + room_down.height):
                for x in range(room_down.x, room_down.x + room_down.width):
                    if self.tiles[(x, y)].tile_type == TileType.FLOOR:
                        floor_tiles.append((x, y))
            if floor_tiles:
                x, y = self._random.choice(floor_tiles)
                self.tiles[(x, y)] = Tile(x, y, TileType.STAIRS_DOWN)

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
                    if tile and tile.tile_type in [
                        TileType.FLOOR,
                        TileType.STAIRS_UP,
                        TileType.STAIRS_DOWN,
                    ]:
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

    def place_traps(self, density: float = 0.1) -> None:
        """Place traps on the floor based on density.

        Args:
            density: Percentage of floor tiles that should have traps (0.0-1.0)
        """
        if not hasattr(self, "traps"):
            self.traps = {}

        # Clamp density to valid range
        density = max(0.0, min(1.0, density))

        # Get all valid floor tiles
        valid_positions = []
        for (x, y), tile in self.tiles.items():
            # Skip walls, stairs, and spawn points
            if tile.tile_type == TileType.FLOOR:
                # Skip room center points (potential spawn locations)
                is_room_center = False
                for room in self.rooms:
                    center_x = room.x + room.width // 2
                    center_y = room.y + room.height // 2
                    if (x, y) == (center_x, center_y):
                        is_room_center = True
                        break

                if not is_room_center:
                    valid_positions.append((x, y))

        # Calculate number of traps to place
        num_traps = int(len(valid_positions) * density)

        # Randomly select positions for traps
        if num_traps > 0 and valid_positions:
            trap_positions = self._random.sample(
                valid_positions, min(num_traps, len(valid_positions))
            )
            for pos in trap_positions:
                # Store trap in both the traps dict and on the tile
                self.traps[pos] = {
                    "revealed": False,
                    "damage": self._random.randint(1, 3),  # 1-3 damage
                }
                # Also add trap attribute to tile for test compatibility
                if pos in self.tiles:
                    setattr(self.tiles[pos], "trap", True)  # noqa: B010

    def place_chests(self, count: int = 3) -> None:
        """Place chests in rooms.

        Args:
            count: Number of chests to place
        """
        if not hasattr(self, "chests"):
            self.chests = {}

        # Find valid positions in rooms (not doorways or stairs)
        valid_positions = []
        for room in self.rooms:
            for y in range(room.y + 1, room.y + room.height - 1):
                for x in range(room.x + 1, room.x + room.width - 1):
                    tile = self.tiles.get((x, y))
                    if tile and tile.tile_type == TileType.FLOOR:
                        # Check if it's not a doorway (has walls on opposite sides)
                        adjacent_walls = 0
                        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            adj_tile = self.tiles.get((x + dx, y + dy))
                            if adj_tile and adj_tile.tile_type == TileType.WALL:
                                adjacent_walls += 1

                        # Not a doorway if it doesn't have walls on exactly opposite sides
                        if adjacent_walls < 2:
                            valid_positions.append((x, y))

        # Place chests
        if valid_positions:
            chest_positions = self._random.sample(valid_positions, min(count, len(valid_positions)))
            for i, pos in enumerate(chest_positions):
                # Higher floors have better loot tables
                # For now, just store a simple loot tier based on position
                loot_tier = 1 + (i // 2)  # Every 2 chests increase tier
                self.chests[pos] = {"opened": False, "loot_tier": loot_tier}
                # Also add chest attribute to tile for test compatibility
                if pos in self.tiles:
                    setattr(self.tiles[pos], "chest", True)  # noqa: B010

    def get_random_walkable_position(self) -> Tuple[int, int]:
        """Get a random walkable position on the floor.

        Returns:
            Tuple of (x, y) coordinates
        """
        # Try to place in a room first
        if self.rooms:
            room = self._random.choice(self.rooms)
            # Place away from walls
            x = room.x + self._random.randint(1, max(1, room.width - 2))
            y = room.y + self._random.randint(1, max(1, room.height - 2))
            return (x, y)

        # Fallback: find any walkable tile
        walkable_tiles = [
            (x, y) for (x, y), tile in self.tiles.items() if tile.tile_type == TileType.FLOOR
        ]

        if walkable_tiles:
            return self._random.choice(walkable_tiles)

        # Last resort: center of map
        return (self.width // 2, self.height // 2)

    def find_stairs_up(self) -> Optional[Tuple[int, int]]:
        """Find the position of stairs going up.

        Returns:
            Tuple of (x, y) coordinates if found, None otherwise
        """
        for pos, tile in self.tiles.items():
            if tile.tile_type == TileType.STAIRS_UP:
                return pos
        return None

    def find_stairs_down(self) -> Optional[Tuple[int, int]]:
        """Find the position of stairs going down.

        Returns:
            Tuple of (x, y) coordinates if found, None otherwise
        """
        for pos, tile in self.tiles.items():
            if tile.tile_type == TileType.STAIRS_DOWN:
                return pos
        return None

    def mark_as_seen(self, x: int, y: int) -> None:
        """Mark a tile as seen for fog of war.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        if not hasattr(self, "seen_tiles"):
            self.seen_tiles = set()
        self.seen_tiles.add((x, y))

    def is_seen(self, x: int, y: int) -> bool:
        """Check if a tile has been seen before.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if tile has been seen
        """
        if not hasattr(self, "seen_tiles"):
            return False
        return (x, y) in self.seen_tiles
