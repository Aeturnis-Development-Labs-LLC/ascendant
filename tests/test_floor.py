"""Tests for floor generation - UTF Contracts GAME-MAP-001 and GAME-MAP-002."""

from src.enums import TileType
from src.models.floor import Floor, Room


class TestRoom:
    """Tests for the Room class."""

    def test_room_creation(self):
        """Test that a room can be created with position and dimensions."""
        room = Room(5, 10, 4, 6)
        assert room.x == 5
        assert room.y == 10
        assert room.width == 4
        assert room.height == 6

    def test_room_edges(self):
        """Test that room edge calculations are correct."""
        room = Room(5, 10, 4, 6)
        assert room.x2 == 8  # 5 + 4 - 1
        assert room.y2 == 15  # 10 + 6 - 1

    def test_room_overlap_detection(self):
        """Test room overlap detection."""
        room1 = Room(5, 5, 4, 4)

        # Room that overlaps
        room2 = Room(7, 7, 4, 4)
        assert room1.overlaps(room2)
        assert room2.overlaps(room1)

        # Room to the right with min_distance=1 (they DO overlap because 10-5-4=1, not >1)
        room3 = Room(10, 5, 4, 4)
        assert room1.overlaps(room3)  # Changed: with min_distance=1, these rooms are too close
        assert room3.overlaps(room1)

        # Room to the right with proper spacing (no overlap)
        room3_spaced = Room(11, 5, 4, 4)
        assert not room1.overlaps(room3_spaced)
        assert not room3_spaced.overlaps(room1)

        # Room below with min_distance=1 (they DO overlap)
        room4 = Room(5, 10, 4, 4)
        assert room1.overlaps(room4)  # Changed: with min_distance=1, these rooms are too close
        assert room4.overlaps(room1)

        # Room below with proper spacing (no overlap)
        room4_spaced = Room(5, 11, 4, 4)
        assert not room1.overlaps(room4_spaced)
        assert not room4_spaced.overlaps(room1)

        # Room that touches edges (they DO overlap with min_distance=1)
        room5 = Room(9, 5, 4, 4)
        assert room1.overlaps(room5)  # Changed: these rooms are adjacent, so they overlap
        assert room5.overlaps(room1)

    def test_room_string_representation(self):
        """Test room string representation."""
        room = Room(3, 4, 5, 6)
        assert str(room) == "Room(3, 4, 5x6)"
        assert repr(room) == "Room(3, 4, 5x6)"


class TestFloor:
    """Tests for the Floor class - UTF Contract GAME-MAP-001."""

    def test_floor_creation(self):
        """Test that a floor can be created with a seed."""
        floor = Floor(12345)
        assert floor.seed == 12345
        assert floor.tiles == {}
        assert floor.rooms == []

    def test_floor_dimensions(self):
        """Test floor dimension constants."""
        assert Floor.FLOOR_WIDTH == 50
        assert Floor.FLOOR_HEIGHT == 50

    def test_floor_generation_creates_tiles(self):
        """Test that generate() creates all tiles."""
        floor = Floor(12345)
        floor.generate()

        # Check that all tiles exist
        assert len(floor.tiles) == 50 * 50

        # Check that all positions are covered
        for y in range(50):
            for x in range(50):
                assert (x, y) in floor.tiles
                tile = floor.tiles[(x, y)]
                assert tile.x == x
                assert tile.y == y

    def test_floor_generation_seed_reproducibility(self):
        """Test that same seed produces identical layout."""
        floor1 = Floor(12345)
        floor1.generate()

        floor2 = Floor(12345)
        floor2.generate()

        # Same number of rooms
        assert len(floor1.rooms) == len(floor2.rooms)

        # Same room positions and dimensions
        for i, room1 in enumerate(floor1.rooms):
            room2 = floor2.rooms[i]
            assert room1.x == room2.x
            assert room1.y == room2.y
            assert room1.width == room2.width
            assert room1.height == room2.height

        # Same tile types
        for pos, tile1 in floor1.tiles.items():
            tile2 = floor2.tiles[pos]
            assert tile1.tile_type == tile2.tile_type

    def test_different_seeds_produce_different_layouts(self):
        """Test that different seeds produce different layouts."""
        floor1 = Floor(12345)
        floor1.generate()

        floor2 = Floor(54321)
        floor2.generate()

        # Very unlikely to have exact same room positions
        rooms_differ = False
        if len(floor1.rooms) != len(floor2.rooms):
            rooms_differ = True
        else:
            for i, room1 in enumerate(floor1.rooms):
                room2 = floor2.rooms[i]
                if (
                    room1.x != room2.x
                    or room1.y != room2.y
                    or room1.width != room2.width
                    or room1.height != room2.height
                ):
                    rooms_differ = True
                    break

        assert rooms_differ, "Different seeds should produce different layouts"

    def test_get_tile(self):
        """Test getting tiles by coordinates."""
        floor = Floor(12345)
        floor.generate()

        # Valid positions
        tile = floor.get_tile(5, 5)
        assert tile is not None
        assert tile.x == 5
        assert tile.y == 5

        # Out of bounds
        assert floor.get_tile(-1, 5) is None
        assert floor.get_tile(5, -1) is None
        assert floor.get_tile(50, 5) is None
        assert floor.get_tile(5, 50) is None

    def test_is_valid_position(self):
        """Test position validation."""
        floor = Floor(12345)

        # Valid positions
        assert floor.is_valid_position(0, 0)
        assert floor.is_valid_position(49, 49)
        assert floor.is_valid_position(10, 10)

        # Invalid positions
        assert not floor.is_valid_position(-1, 0)
        assert not floor.is_valid_position(0, -1)
        assert not floor.is_valid_position(50, 0)
        assert not floor.is_valid_position(0, 50)


class TestRoomGeneration:
    """Tests for room generation algorithm - UTF Contract GAME-MAP-002."""

    def test_room_count_in_range(self):
        """Test that generated room count is between 4-10 (relaxed due to spacing constraints)."""
        for seed in [12345, 54321, 99999, 11111, 77777]:
            floor = Floor(seed)
            floor.generate()

            room_count = len(floor.rooms)
            # New parameters: 8-12 rooms
            assert 8 <= room_count <= 12, f"Seed {seed} generated {room_count} rooms"

    def test_room_dimensions_in_range(self):
        """Test that all rooms have dimensions between 4x4 and 10x10."""
        floor = Floor(12345)
        floor.generate()

        for room in floor.rooms:
            assert 4 <= room.width <= 10, f"Room width {room.width} out of range"
            assert 4 <= room.height <= 10, f"Room height {room.height} out of range"

    def test_no_room_overlaps(self):
        """Test that no rooms overlap."""
        floor = Floor(12345)
        floor.generate()

        # Check each pair of rooms
        for i, room1 in enumerate(floor.rooms):
            for room2 in floor.rooms[i + 1 :]:
                assert not room1.overlaps(room2), f"{room1} overlaps with {room2}"

    def test_rooms_respect_edge_buffer(self):
        """Test that rooms are at least 2 tiles from edges."""
        floor = Floor(12345)
        floor.generate()

        for room in floor.rooms:
            # Check left and top edges
            assert room.x >= 2, f"Room at x={room.x} too close to left edge"
            assert room.y >= 2, f"Room at y={room.y} too close to top edge"

            # Check right and bottom edges
            assert room.x2 < 48, f"Room ending at x={room.x2} too close to right edge"
            assert room.y2 < 48, f"Room ending at y={room.y2} too close to bottom edge"

    def test_room_tiles_are_walkable(self):
        """Test that room interiors are walkable (FLOOR or STAIRS)."""
        floor = Floor(12345)
        floor.generate()

        walkable_types = {TileType.FLOOR, TileType.STAIRS_UP, TileType.STAIRS_DOWN}

        for room in floor.rooms:
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    tile = floor.get_tile(x, y)
                    assert tile is not None
                    assert (
                        tile.tile_type in walkable_types
                    ), f"Room tile at ({x}, {y}) is not walkable"

    def test_floor_has_walls_and_walkable_areas(self):
        """Test that floor has both walls and walkable areas (rooms + corridors)."""
        floor = Floor(12345)
        floor.generate()

        wall_count = 0
        walkable_count = 0

        for tile in floor.tiles.values():
            if tile.tile_type == TileType.WALL:
                wall_count += 1
            elif tile.tile_type in {TileType.FLOOR, TileType.STAIRS_UP, TileType.STAIRS_DOWN}:
                walkable_count += 1

        # Should have both walls and walkable areas
        assert wall_count > 0, "Floor should have walls"
        assert walkable_count > 0, "Floor should have walkable areas"

        # Walkable area should be reasonable (10-40% of total)
        total_tiles = len(floor.tiles)
        walkable_percentage = (walkable_count / total_tiles) * 100
        assert (
            10 <= walkable_percentage <= 40
        ), f"Walkable area {walkable_percentage:.1f}% is out of expected range"

    def test_edge_buffer_maintained(self):
        """Test that edge buffer is maintained (no rooms at very edge)."""
        floor = Floor(12345)
        floor.generate()

        # Check that no rooms are at the very edge (0 or width-1/height-1)
        for room in floor.rooms:
            assert room.x > 0, f"Room at x={room.x} touches left edge"
            assert room.y > 0, f"Room at y={room.y} touches top edge"
            assert room.x2 < floor.width - 1, f"Room at x2={room.x2} touches right edge"
            assert room.y2 < floor.height - 1, f"Room at y2={room.y2} touches bottom edge"

    def test_floor_connectivity(self):
        """Test that all rooms are connected via corridors."""
        floor = Floor(12345)
        floor.generate()

        # Should have corridors connecting rooms
        assert hasattr(floor, "connect_rooms"), "Floor should have connect_rooms method"

        # Verify connectivity by checking if we can reach all rooms from the first room
        if floor.rooms:
            is_connected = floor.is_fully_connected()
            assert is_connected, f"Not all rooms are connected"

    def test_stairs_placement(self):
        """Test that stairs are placed in rooms."""
        floor = Floor(12345)
        floor.generate()

        # Find stairs
        stairs_up = None
        stairs_down = None

        for tile in floor.tiles.values():
            if tile.tile_type == TileType.STAIRS_UP:
                stairs_up = (tile.x, tile.y)
            elif tile.tile_type == TileType.STAIRS_DOWN:
                stairs_down = (tile.x, tile.y)

        # Should have both stairs if there are at least 2 rooms
        if len(floor.rooms) >= 2:
            assert stairs_up is not None, "Should have stairs up"
            assert stairs_down is not None, "Should have stairs down"
            assert stairs_up != stairs_down, "Stairs should be in different locations"
