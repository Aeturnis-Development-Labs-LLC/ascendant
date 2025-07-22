"""Benchmark script for large floor operations (100x100)."""

import time
import statistics
from typing import Dict, List, Optional, Tuple

from src.enums import TileType
from src.models.tile import Tile


class LargeFloor:
    """Test class for 100x100 floor."""
    
    FLOOR_WIDTH = 100
    FLOOR_HEIGHT = 100
    MIN_ROOMS = 25
    MAX_ROOMS = 50
    MIN_ROOM_SIZE = 3
    MAX_ROOM_SIZE = 8
    EDGE_BUFFER = 1

    def __init__(self, seed: int):
        """Initialize a new floor with the given seed."""
        self.seed = seed
        self.tiles: Dict[Tuple[int, int], Tile] = {}
        self.rooms: List = []
        import random
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
        from src.models.floor import Room
        room_count = self._random.randint(self.MIN_ROOMS, self.MAX_ROOMS)

        attempts = 0
        max_attempts = 1000

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
        """Check if all rooms are connected to each other."""
        if len(self.rooms) < 2:
            return True

        # Start from the first room
        start_room = self.rooms[0]
        start_x = start_room.x + start_room.width // 2
        start_y = start_room.y + start_room.height // 2

        # Use BFS to find all reachable floor tiles
        from collections import deque
        visited: set = set()
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

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is valid within the floor."""
        return 0 <= x < self.FLOOR_WIDTH and 0 <= y < self.FLOOR_HEIGHT


def benchmark_operation(operation_name: str, operation, iterations: int = 10) -> Tuple[float, float, float]:
    """Benchmark an operation and return min, avg, max times in milliseconds."""
    times = []
    
    for _ in range(iterations):
        start_time = time.perf_counter()
        operation()
        end_time = time.perf_counter()
        times.append((end_time - start_time) * 1000)  # Convert to milliseconds
    
    return min(times), statistics.mean(times), max(times)


def main():
    """Run benchmarks for 100x100 floor."""
    print("=== EDGE CASE: 100x100 Floor Benchmark ===")
    print("Running 10 iterations for each operation...")
    print()
    
    # Test operations
    seed = 12345
    
    # Floor Generation
    def gen_op():
        floor = LargeFloor(seed)
        floor.generate()
    
    gen_min, gen_avg, gen_max = benchmark_operation("Floor Generation", gen_op)
    
    # Room Connection
    floor = LargeFloor(seed)
    floor.generate()
    def conn_op():
        floor.connect_rooms()
    
    conn_min, conn_avg, conn_max = benchmark_operation("Room Connection", conn_op)
    
    # Pathfinding Check
    floor = LargeFloor(seed)
    floor.generate()
    floor.connect_rooms()
    def path_op():
        floor.is_fully_connected()
    
    path_min, path_avg, path_max = benchmark_operation("Pathfinding Check", path_op)
    
    # Full Floor Creation
    def full_op():
        floor = LargeFloor(seed)
        floor.generate()
        floor.connect_rooms()
        floor.place_stairs()
        floor.is_fully_connected()
    
    full_min, full_avg, full_max = benchmark_operation("Full Floor Creation", full_op, iterations=5)
    
    print("### 100x100 Floor Benchmark Results (milliseconds)")
    print("| Operation | Min | Avg | Max | Target | Status |")
    print("|-----------|-----|-----|-----|--------|--------|")
    print(f"| Floor Generation | {gen_min:.2f} | {gen_avg:.2f} | {gen_max:.2f} | <100ms | {'PASS' if gen_avg < 100 else 'FAIL'} |")
    print(f"| Room Connection | {conn_min:.2f} | {conn_avg:.2f} | {conn_max:.2f} | <50ms | {'PASS' if conn_avg < 50 else 'FAIL'} |")
    print(f"| Pathfinding Check | {path_min:.2f} | {path_avg:.2f} | {path_max:.2f} | <50ms | {'PASS' if path_avg < 50 else 'FAIL'} |")
    print(f"| Full Floor Creation | {full_min:.2f} | {full_avg:.2f} | {full_max:.2f} | <500ms | {'PASS' if full_avg < 500 else 'FAIL'} |")
    
    print()
    print("### Comparison with 20x20 floor")
    print("| Operation | 20x20 avg | 100x100 avg | Scale Factor |")
    print("|-----------|-----------|-------------|--------------|")
    print(f"| Floor Generation | 0.44ms | {gen_avg:.2f}ms | {gen_avg/0.44:.1f}x |")
    print(f"| Room Connection | 0.05ms | {conn_avg:.2f}ms | {conn_avg/0.05:.1f}x |")
    print(f"| Pathfinding Check | 0.17ms | {path_avg:.2f}ms | {path_avg/0.17:.1f}x |")
    
    # Get floor stats
    test_floor = LargeFloor(seed)
    test_floor.generate()
    print()
    print(f"Floor stats: {len(test_floor.rooms)} rooms generated")
    print(f"Grid size: {test_floor.FLOOR_WIDTH}x{test_floor.FLOOR_HEIGHT} = {test_floor.FLOOR_WIDTH * test_floor.FLOOR_HEIGHT} tiles")


if __name__ == "__main__":
    main()