"""Tests for room connection and stairs - UTF Contracts GAME-MAP-003 and GAME-MAP-004."""

from collections import deque

from src.enums import TileType
from src.models.floor import Floor


class TestRoomConnection:
    """Tests for room connection algorithm - UTF Contract GAME-MAP-003."""

    def test_connect_rooms_method_exists(self):
        """Test that Floor has connect_rooms method."""
        floor = Floor(12345)
        floor.generate()
        assert hasattr(floor, "connect_rooms")

    def test_connect_rooms_creates_corridors(self):
        """Test that connect_rooms creates corridors between rooms."""
        floor = Floor(12345)
        floor.generate()

        # Count floor tiles before connection
        floor_tiles_before = sum(
            1 for tile in floor.tiles.values() if tile.tile_type == TileType.FLOOR
        )

        floor.connect_rooms()

        # Count floor tiles after connection
        floor_tiles_after = sum(
            1 for tile in floor.tiles.values() if tile.tile_type == TileType.FLOOR
        )

        # Should have more floor tiles after creating corridors
        assert floor_tiles_after > floor_tiles_before

    def test_is_fully_connected_method_exists(self):
        """Test that Floor has is_fully_connected method."""
        floor = Floor(12345)
        floor.generate()
        assert hasattr(floor, "is_fully_connected")

    def test_all_rooms_connected(self):
        """Test that all rooms are reachable from any other room."""
        # Test multiple seeds to ensure consistency
        for seed in [12345, 54321, 99999, 11111, 77777]:
            floor = Floor(seed)
            floor.generate()
            floor.connect_rooms()

            assert floor.is_fully_connected(), f"Floor with seed {seed} is not fully connected"

    def test_corridors_are_one_tile_wide(self):
        """Test that corridors are exactly 1 tile wide."""
        floor = Floor(12345)
        floor.generate()

        # Get room tiles before connection
        room_tiles = set()
        for room in floor.rooms:
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    room_tiles.add((x, y))

        floor.connect_rooms()

        # Find corridor tiles (floor tiles that aren't in rooms)
        corridor_tiles = []
        for pos, tile in floor.tiles.items():
            if tile.tile_type == TileType.FLOOR and pos not in room_tiles:
                corridor_tiles.append(pos)

        # Check that corridor tiles don't form wide sections
        for x, y in corridor_tiles:
            adjacent_corridor_count = 0
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                adj_pos = (x + dx, y + dy)
                if adj_pos in floor.tiles:
                    adj_tile = floor.tiles[adj_pos]
                    if adj_tile.tile_type == TileType.FLOOR and adj_pos not in room_tiles:
                        adjacent_corridor_count += 1

            # Corridor tiles should have at most 4 adjacent corridor tiles
            # (2 for straight line, 3 for L-shaped turns, 4 for crossroads)
            assert (
                adjacent_corridor_count <= 4
            ), f"Corridor at {x},{y} has {adjacent_corridor_count} adjacent corridors"

    def test_pathfinding_between_rooms(self):
        """Test that pathfinding works between any two rooms."""
        floor = Floor(12345)
        floor.generate()
        floor.connect_rooms()

        # Test pathfinding between each pair of rooms
        for i, room1 in enumerate(floor.rooms):
            for room2 in floor.rooms[i + 1 :]:
                # Get center of each room
                start = (room1.x + room1.width // 2, room1.y + room1.height // 2)
                end = (room2.x + room2.width // 2, room2.y + room2.height // 2)

                # Simple BFS pathfinding
                visited = set()
                queue = deque([start])
                found = False

                while queue and not found:
                    current = queue.popleft()
                    if current in visited:
                        continue
                    visited.add(current)

                    if current == end:
                        found = True
                        break

                    x, y = current
                    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        next_x, next_y = x + dx, y + dy
                        next_pos = (next_x, next_y)

                        if next_pos in floor.tiles:
                            tile = floor.tiles[next_pos]
                            if tile.tile_type == TileType.FLOOR and next_pos not in visited:
                                queue.append(next_pos)

                assert found, f"No path found between rooms at {start} and {end}"


class TestStairsPlacement:
    """Tests for stairs placement - UTF Contract GAME-MAP-004."""

    def test_place_stairs_method_exists(self):
        """Test that Floor has place_stairs method."""
        floor = Floor(12345)
        floor.generate()
        assert hasattr(floor, "place_stairs")

    def test_stairs_placed_in_room(self):
        """Test that stairs are placed inside a room."""
        floor = Floor(12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_stairs()

        # Find the stairs
        stairs_pos = None
        for pos, tile in floor.tiles.items():
            if tile.tile_type == TileType.STAIRS_UP:
                stairs_pos = pos
                break

        assert stairs_pos is not None, "No stairs found on floor"

        # Check if stairs are in any room
        x, y = stairs_pos
        in_room = False
        for room in floor.rooms:
            if room.x <= x < room.x + room.width and room.y <= y < room.y + room.height:
                in_room = True
                break

        assert in_room, f"Stairs at {stairs_pos} are not inside any room"

    def test_exactly_one_stairs(self):
        """Test that exactly one stairs is placed per floor."""
        floor = Floor(12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_stairs()

        stairs_count = sum(
            1 for tile in floor.tiles.values() if tile.tile_type == TileType.STAIRS_UP
        )

        assert stairs_count == 1, f"Expected 1 stairs, found {stairs_count}"

    def test_stairs_not_in_doorway(self):
        """Test that stairs are not placed in doorways."""
        floor = Floor(12345)
        floor.generate()

        # Get room tiles before connection
        room_tiles = set()
        for room in floor.rooms:
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    room_tiles.add((x, y))

        floor.connect_rooms()
        floor.place_stairs()

        # Find stairs position
        stairs_pos = None
        for pos, tile in floor.tiles.items():
            if tile.tile_type == TileType.STAIRS_UP:
                stairs_pos = pos
                break

        assert stairs_pos is not None

        # Check if stairs are at a doorway (edge of room adjacent to corridor)
        x, y = stairs_pos
        is_doorway = False

        # Check if this is at the edge of a room
        for room in floor.rooms:
            # Check if on room boundary
            on_edge = (
                (x == room.x or x == room.x + room.width - 1) and room.y <= y < room.y + room.height
            ) or (
                (y == room.y or y == room.y + room.height - 1) and room.x <= x < room.x + room.width
            )

            if on_edge:
                # Check if adjacent to a corridor
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    adj_pos = (x + dx, y + dy)
                    if adj_pos in floor.tiles:
                        adj_tile = floor.tiles[adj_pos]
                        if adj_tile.tile_type == TileType.FLOOR and adj_pos not in room_tiles:
                            is_doorway = True
                            break

            if is_doorway:
                break

        assert not is_doorway, f"Stairs at {stairs_pos} are placed in a doorway"

    def test_stairs_accessible_from_all_rooms(self):
        """Test that stairs can be reached from every room."""
        floor = Floor(12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_stairs()

        # Find stairs position
        stairs_pos = None
        for pos, tile in floor.tiles.items():
            if tile.tile_type == TileType.STAIRS_UP:
                stairs_pos = pos
                break

        assert stairs_pos is not None

        # Test pathfinding from each room to stairs
        for room in floor.rooms:
            # Get center of room
            start = (room.x + room.width // 2, room.y + room.height // 2)

            # BFS to stairs
            visited = set()
            queue = deque([start])
            found = False

            while queue and not found:
                current = queue.popleft()
                if current in visited:
                    continue
                visited.add(current)

                if current == stairs_pos:
                    found = True
                    break

                x, y = current
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    next_x, next_y = x + dx, y + dy
                    next_pos = (next_x, next_y)

                    if next_pos in floor.tiles:
                        tile = floor.tiles[next_pos]
                        if (
                            tile.tile_type in [TileType.FLOOR, TileType.STAIRS_UP]
                            and next_pos not in visited
                        ):
                            queue.append(next_pos)

            assert found, f"Stairs at {stairs_pos} not reachable from room at {start}"

    def test_stairs_placement_random(self):
        """Test that stairs placement varies with different generation."""
        positions = []

        # Generate same floor multiple times with different stairs placement
        for i in range(5):
            floor = Floor(12345)  # Same seed for consistent room layout
            floor.generate()
            floor.connect_rooms()
            floor._random.seed(12345 + i)  # Different seed for stairs placement
            floor.place_stairs()

            # Find stairs position
            for pos, tile in floor.tiles.items():
                if tile.tile_type == TileType.STAIRS_UP:
                    positions.append(pos)
                    break

        # Check that we got some variety in positions
        unique_positions = set(positions)
        assert len(unique_positions) > 1, "Stairs placement should vary"
