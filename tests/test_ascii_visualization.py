"""Tests for ASCII visualization and map features - UTF Contracts GAME-MAP-005, 006, 007."""

from src.enums import TileType
from src.models.floor import Floor
from src.renderers.ascii_renderer import ASCIIRenderer


class TestASCIIRenderer:
    """Tests for ASCII renderer with fog of war."""

    def test_basic_rendering(self):
        """Test basic floor rendering without fog of war."""
        floor = Floor(seed=12345)
        floor.generate()

        # Get a position in the first room
        room = floor.rooms[0]
        player_pos = (room.x + room.width // 2, room.y + room.height // 2)

        # Render with large vision radius (no fog)
        result = ASCIIRenderer.render_static(floor, player_pos, vision_radius=50)

        # Check basic properties
        lines = result.split("\n")
        assert len(lines) == floor.height
        assert all(len(line) == floor.width for line in lines)

        # Player should be visible
        assert "@" in result

        # Should have walls and floors
        assert "#" in result
        assert "." in result

    def test_fog_of_war(self):
        """Test that fog of war obscures distant areas."""
        floor = Floor(seed=12345)
        floor.generate()

        # Place player in corner
        player_pos = (1, 1)

        # Render with small vision radius
        result = ASCIIRenderer.render_static(floor, player_pos, vision_radius=3)

        # Should have fog characters
        assert "?" in result

        # Count visible vs fog tiles
        visible_count = sum(1 for char in result if char != "?" and char != "\n")
        fog_count = result.count("?")

        # Most of the map should be fogged
        assert fog_count > visible_count

    def test_vision_radius_calculation(self):
        """Test that vision radius is calculated correctly."""
        floor = Floor(seed=12345)
        floor.generate()

        # Place player in center
        player_pos = (10, 10)

        # Render with radius 5
        result = ASCIIRenderer.render_static(floor, player_pos, vision_radius=5)
        lines = result.split("\n")

        # Check that tiles within radius 5 are not fog
        for y in range(floor.height):
            for x in range(floor.width):
                dx = abs(x - player_pos[0])
                dy = abs(y - player_pos[1])
                distance_squared = dx * dx + dy * dy

                if distance_squared <= 25 and (x, y) != player_pos:  # radius 5 squared
                    # Should not be fog (unless it's the player)
                    assert lines[y][x] != "?" or lines[y][x] == "@"

    def test_stairs_rendering(self):
        """Test that stairs are rendered correctly."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_stairs()

        # Find stairs positions
        stairs_up_pos = None
        stairs_down_pos = None
        for (x, y), tile in floor.tiles.items():
            if tile.tile_type == TileType.STAIRS_UP:
                stairs_up_pos = (x, y)
            elif tile.tile_type == TileType.STAIRS_DOWN:
                stairs_down_pos = (x, y)

        assert stairs_up_pos is not None
        assert stairs_down_pos is not None

        # Render with player near stairs (not on them)
        player_pos = (stairs_up_pos[0] + 1, stairs_up_pos[1])
        result = ASCIIRenderer.render_static(
            floor, player_pos, vision_radius=50
        )  # Large radius to see both

        # Stairs should be visible
        assert "^" in result  # Stairs up
        assert "v" in result  # Stairs down

    def test_entity_rendering_priority(self):
        """Test that entities are rendered over tiles."""
        floor = Floor(seed=12345)
        floor.generate()

        # Add a mock monster
        floor.monsters = {(5, 5): {"type": "goblin"}}

        # Render with player at different position
        result = ASCIIRenderer.render_static(floor, (3, 3), vision_radius=10)

        # Monster should be visible
        assert "M" in result

        # Player should override any tile
        result2 = ASCIIRenderer.render_static(floor, (5, 5), vision_radius=10)
        assert "@" in result2
        # Monster shouldn't be visible at player position
        lines = result2.split("\n")
        assert lines[5][5] == "@"


class TestTrapPlacement:
    """Tests for trap placement functionality."""

    def test_trap_placement_basic(self):
        """Test basic trap placement."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()

        # Place traps with 10% density
        floor.place_traps(density=0.1)

        # Should have traps
        assert hasattr(floor, "traps")
        assert len(floor.traps) > 0

        # All traps should be on floor tiles
        for x, y in floor.traps:
            tile = floor.tiles.get((x, y))
            assert tile is not None
            assert tile.tile_type == TileType.FLOOR

    def test_trap_density(self):
        """Test that trap density is respected."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()

        # Count floor tiles
        floor_tiles = sum(1 for tile in floor.tiles.values() if tile.tile_type == TileType.FLOOR)

        # Place with 20% density
        floor.place_traps(density=0.2)

        # Should have approximately 20% of floor tiles as traps
        expected_traps = int(floor_tiles * 0.2)
        actual_traps = len(floor.traps)

        # Allow some variance
        assert abs(actual_traps - expected_traps) <= floor_tiles * 0.1

    def test_traps_not_on_stairs(self):
        """Test that traps are not placed on stairs."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_stairs()

        # Get stairs positions
        stairs_positions = set()
        for (x, y), tile in floor.tiles.items():
            if tile.tile_type in [TileType.STAIRS_UP, TileType.STAIRS_DOWN]:
                stairs_positions.add((x, y))

        # Place traps
        floor.place_traps(density=0.3)

        # No trap should be on stairs
        for trap_pos in floor.traps:
            assert trap_pos not in stairs_positions

    def test_traps_not_on_spawn_points(self):
        """Test that traps avoid room centers (spawn points)."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()

        # Get room centers
        room_centers = set()
        for room in floor.rooms:
            center_x = room.x + room.width // 2
            center_y = room.y + room.height // 2
            room_centers.add((center_x, center_y))

        # Place traps
        floor.place_traps(density=0.3)

        # No trap should be on room centers
        for trap_pos in floor.traps:
            assert trap_pos not in room_centers

    def test_trap_properties(self):
        """Test that traps have correct properties."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_traps(density=0.1)

        for trap_data in floor.traps.values():
            # Should start hidden
            assert "revealed" in trap_data
            assert trap_data["revealed"] is False

            # Should have damage
            assert "damage" in trap_data
            assert 1 <= trap_data["damage"] <= 3

    def test_trap_rendering(self):
        """Test that traps are rendered correctly."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_traps(density=0.1)

        # Get a trap position
        trap_pos = list(floor.traps.keys())[0]

        # Render with trap hidden
        result = ASCIIRenderer.render_static(floor, trap_pos, vision_radius=10)
        lines = result.split("\n")
        # Hidden trap should show as floor
        assert lines[trap_pos[1]][trap_pos[0]] == "@"  # Player is on trap

        # Reveal the trap
        floor.traps[trap_pos]["revealed"] = True

        # Render from nearby position
        nearby_pos = (trap_pos[0] + 1, trap_pos[1])
        result = ASCIIRenderer.render_static(floor, nearby_pos, vision_radius=10)
        lines = result.split("\n")
        # Revealed trap should show as 'T'
        assert lines[trap_pos[1]][trap_pos[0]] == "T"


class TestChestGeneration:
    """Tests for chest generation functionality."""

    def test_chest_placement_basic(self):
        """Test basic chest placement."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()

        # Clear any existing chests from generate()
        floor.chests = {}

        # Place chests
        floor.place_chests(count=3)

        # Should have chests
        assert hasattr(floor, "chests")
        assert len(floor.chests) > 0
        assert len(floor.chests) <= 3

    def test_chests_in_rooms_only(self):
        """Test that chests are placed only in rooms."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_chests(count=5)

        # All chests should be inside rooms
        for x, y in floor.chests:
            in_room = False
            for room in floor.rooms:
                if room.x <= x < room.x + room.width and room.y <= y < room.y + room.height:
                    in_room = True
                    break
            assert in_room

    def test_chests_not_blocking_doorways(self):
        """Test that chests don't block doorways."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_chests(count=10)  # Many chests to test edge cases

        # Chests should not be at room edges (potential doorways)
        for x, y in floor.chests:
            # Find which room contains this chest
            for room in floor.rooms:
                if room.x <= x < room.x + room.width and room.y <= y < room.y + room.height:
                    # Should not be on room edges
                    assert x > room.x and x < room.x + room.width - 1
                    assert y > room.y and y < room.y + room.height - 1
                    break

    def test_chest_properties(self):
        """Test that chests have correct properties."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_chests(count=5)

        for chest_data in floor.chests.values():
            # Should start closed
            assert "opened" in chest_data
            assert chest_data["opened"] is False

            # Should have loot tier
            assert "loot_tier" in chest_data
            assert chest_data["loot_tier"] >= 1

    def test_chest_loot_tiers(self):
        """Test that chest loot tiers increase."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_chests(count=6)

        # Collect loot tiers
        loot_tiers = [chest["loot_tier"] for chest in floor.chests.values()]

        # Should have some variety in tiers
        assert max(loot_tiers) > min(loot_tiers) or len(loot_tiers) < 2

    def test_chest_rendering(self):
        """Test that chests are rendered correctly."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_chests(count=3)

        # Get a chest position
        chest_pos = list(floor.chests.keys())[0]

        # Render from nearby position
        nearby_pos = (chest_pos[0] + 1, chest_pos[1])
        result = ASCIIRenderer.render_static(floor, nearby_pos, vision_radius=10)

        # Chest should be visible
        assert "C" in result
        lines = result.split("\n")
        assert lines[chest_pos[1]][chest_pos[0]] == "C"


class TestIntegratedVisualization:
    """Tests for integrated visualization features."""

    def test_full_floor_with_features(self):
        """Test rendering a complete floor with all features."""
        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_stairs()
        floor.place_traps(density=0.1)
        floor.place_chests(count=3)

        # Add some mock monsters
        floor.monsters = {(5, 5): {"type": "goblin"}, (15, 15): {"type": "orc"}}

        # Render from center with large radius to see everything
        result = ASCIIRenderer.render_static(floor, (25, 25), vision_radius=50)

        # Should have all elements
        assert "@" in result  # Player
        assert "#" in result  # Walls
        assert "." in result  # Floors
        assert "^" in result  # Stairs up
        assert "v" in result  # Stairs down
        assert "M" in result  # Monsters
        assert "C" in result  # Chests

    def test_rendering_performance(self):
        """Test that rendering is performant."""
        import time

        floor = Floor(seed=12345)
        floor.generate()
        floor.connect_rooms()
        floor.place_stairs()
        floor.place_traps(density=0.2)
        floor.place_chests(count=5)

        # Time 100 renders
        start_time = time.time()
        for _ in range(100):
            ASCIIRenderer.render_static(floor, (10, 10), vision_radius=5)
        elapsed = time.time() - start_time

        # Should be fast (less than 500ms for 100 renders on CI)
        # Increased threshold to account for CI performance variance
        assert elapsed < 0.5

    def test_edge_cases(self):
        """Test edge cases for visualization."""
        floor = Floor(seed=12345)
        floor.generate()

        # Player at corner
        result = ASCIIRenderer.render_static(floor, (0, 0), vision_radius=3)
        assert "@" in result

        # Player at edge
        result = ASCIIRenderer.render_static(
            floor, (floor.width - 1, floor.height - 1), vision_radius=3
        )
        assert "@" in result

        # Zero vision radius
        result = ASCIIRenderer.render_static(floor, (10, 10), vision_radius=0)
        # Should only see player
        assert result.count("@") == 1
        assert result.count("?") == (floor.width * floor.height) - 1
