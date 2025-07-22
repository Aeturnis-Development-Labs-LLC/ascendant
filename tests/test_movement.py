"""Tests for movement system - UTF Contracts GAME-MOVE-001, GAME-MOVE-002, GAME-MOVE-005."""

import pytest

from src.enums import Direction, EntityType, TileType
from src.game.movement import validate_position, calculate_new_position, execute_move
from src.input.keyboard_handler import KeyboardHandler
from src.models.character import Character
from src.models.floor import Floor
from src.models.tile import Tile


class TestCharacter:
    """Tests for Character model."""

    def test_character_creation(self):
        """Test creating a character with default values."""
        char = Character("Hero", 5, 5)
        assert char.name == "Hero"
        assert char.position == (5, 5)
        assert char.entity_type == EntityType.PLAYER
        assert char.stamina == 100
        assert char.stamina_max == 100

    def test_character_move_to(self):
        """Test moving character to new position."""
        char = Character("Hero", 5, 5)
        char.move_to((6, 5))
        assert char.position == (6, 5)

    def test_character_validate_move(self):
        """Test character move validation."""
        floor = Floor(seed=12345)
        floor.generate()

        # Place character on a floor tile
        char = Character("Hero", 5, 5)
        floor.tiles[(5, 5)] = Tile(5, 5, TileType.FLOOR)
        floor.tiles[(6, 5)] = Tile(6, 5, TileType.FLOOR)
        floor.tiles[(4, 5)] = Tile(4, 5, TileType.WALL)

        # Valid move to floor
        assert char.validate_move(Direction.EAST, floor) is True

        # Invalid move to wall
        assert char.validate_move(Direction.WEST, floor) is False

    def test_character_stamina_management(self):
        """Test stamina properties."""
        char = Character("Hero", 0, 0)
        assert char.stamina == 100

        # Reduce stamina
        char.stamina = 50
        assert char.stamina == 50

        # Cannot exceed max
        char.stamina = 150
        assert char.stamina == 100

        # Cannot go below 0
        char.stamina = -10
        assert char.stamina == 0


class TestMovementSystem:
    """Tests for movement functions."""

    def test_validate_position(self):
        """Test position validation."""
        floor = Floor(seed=12345)
        floor.generate()

        # Valid positions
        assert validate_position((5, 5), floor) is True
        assert validate_position((0, 0), floor) is True
        assert validate_position((19, 19), floor) is True

        # Invalid positions (out of bounds)
        assert validate_position((-1, 5), floor) is False
        assert validate_position((5, -1), floor) is False
        assert validate_position((20, 5), floor) is False
        assert validate_position((5, 20), floor) is False

    def test_calculate_new_position(self):
        """Test new position calculation."""
        # North
        assert calculate_new_position((5, 5), Direction.NORTH) == (5, 4)
        # South
        assert calculate_new_position((5, 5), Direction.SOUTH) == (5, 6)
        # East
        assert calculate_new_position((5, 5), Direction.EAST) == (6, 5)
        # West
        assert calculate_new_position((5, 5), Direction.WEST) == (4, 5)

    def test_execute_move_valid(self):
        """Test executing valid moves."""
        floor = Floor(seed=12345)
        floor.generate()

        # Setup floor tiles
        floor.tiles[(5, 5)] = Tile(5, 5, TileType.FLOOR)
        floor.tiles[(6, 5)] = Tile(6, 5, TileType.FLOOR)

        char = Character("Hero", 5, 5)

        # Execute valid move
        result = execute_move(char, Direction.EAST, floor)
        assert result is True
        assert char.position == (6, 5)

    def test_execute_move_invalid_wall(self):
        """Test that moves into walls are rejected."""
        floor = Floor(seed=12345)
        floor.generate()

        # Setup tiles
        floor.tiles[(5, 5)] = Tile(5, 5, TileType.FLOOR)
        floor.tiles[(5, 4)] = Tile(5, 4, TileType.WALL)

        char = Character("Hero", 5, 5)

        # Try to move into wall
        result = execute_move(char, Direction.NORTH, floor)
        assert result is False
        assert char.position == (5, 5)  # Position unchanged

    def test_execute_move_invalid_bounds(self):
        """Test that moves out of bounds are rejected."""
        floor = Floor(seed=12345)
        floor.generate()

        # Place character at edge
        floor.tiles[(0, 0)] = Tile(0, 0, TileType.FLOOR)
        char = Character("Hero", 0, 0)

        # Try to move out of bounds
        result = execute_move(char, Direction.NORTH, floor)
        assert result is False
        assert char.position == (0, 0)  # Position unchanged

        result = execute_move(char, Direction.WEST, floor)
        assert result is False
        assert char.position == (0, 0)  # Position unchanged

    def test_movement_all_directions(self):
        """Test movement in all four directions."""
        floor = Floor(seed=12345)
        floor.generate()

        # Create open area
        for y in range(4, 8):
            for x in range(4, 8):
                floor.tiles[(x, y)] = Tile(x, y, TileType.FLOOR)

        char = Character("Hero", 5, 5)

        # Move in all directions
        assert execute_move(char, Direction.NORTH, floor) is True
        assert char.position == (5, 4)

        assert execute_move(char, Direction.EAST, floor) is True
        assert char.position == (6, 4)

        assert execute_move(char, Direction.SOUTH, floor) is True
        assert char.position == (6, 5)

        assert execute_move(char, Direction.WEST, floor) is True
        assert char.position == (5, 5)

    def test_diagonal_movement(self):
        """Test diagonal movement for Phase 2.1."""
        floor = Floor(seed=12345)
        floor.generate()

        # Create open area
        for y in range(4, 8):
            for x in range(4, 8):
                floor.tiles[(x, y)] = Tile(x, y, TileType.FLOOR)

        char = Character("Hero", 5, 5)

        # Test diagonal moves (if implemented)
        # This test documents expected behavior for future diagonal support
        # Currently expecting False as diagonals not in Direction enum
        with pytest.raises(AttributeError):
            execute_move(char, "NORTHEAST", floor)


class TestKeyboardHandler:
    """Tests for KeyboardHandler input mapping."""

    def test_keyboard_handler_creation(self):
        """Test creating keyboard handler."""
        handler = KeyboardHandler()
        assert handler.command_queue == []
        assert handler.key_map is not None

    def test_key_mapping(self):
        """Test key to direction mapping."""
        handler = KeyboardHandler()

        # WASD keys
        assert handler.map_key_to_direction("w") == Direction.NORTH
        assert handler.map_key_to_direction("W") == Direction.NORTH
        assert handler.map_key_to_direction("s") == Direction.SOUTH
        assert handler.map_key_to_direction("S") == Direction.SOUTH
        assert handler.map_key_to_direction("d") == Direction.EAST
        assert handler.map_key_to_direction("D") == Direction.EAST
        assert handler.map_key_to_direction("a") == Direction.WEST
        assert handler.map_key_to_direction("A") == Direction.WEST

        # Arrow keys (if supported)
        # These might be special key codes depending on implementation

    def test_invalid_key_mapping(self):
        """Test invalid keys return None."""
        handler = KeyboardHandler()

        assert handler.map_key_to_direction("x") is None
        assert handler.map_key_to_direction("1") is None
        assert handler.map_key_to_direction(" ") is None
        assert handler.map_key_to_direction("") is None

    def test_queue_command(self):
        """Test queuing valid commands."""
        handler = KeyboardHandler()

        # Queue valid movement
        handler.queue_command("w")
        assert len(handler.command_queue) == 1
        assert handler.command_queue[0] == Direction.NORTH

        # Queue multiple commands
        handler.queue_command("a")
        handler.queue_command("s")
        handler.queue_command("d")
        assert len(handler.command_queue) == 4
        assert handler.command_queue[1] == Direction.WEST
        assert handler.command_queue[2] == Direction.SOUTH
        assert handler.command_queue[3] == Direction.EAST

    def test_ignore_invalid_commands(self):
        """Test that invalid keys are ignored."""
        handler = KeyboardHandler()

        # Try to queue invalid commands
        handler.queue_command("x")
        handler.queue_command("1")
        handler.queue_command("")

        assert len(handler.command_queue) == 0  # Nothing queued

    def test_get_next_command(self):
        """Test getting next command from queue."""
        handler = KeyboardHandler()

        # Queue some commands
        handler.queue_command("w")
        handler.queue_command("d")

        # Get commands in order
        assert handler.get_next_command() == Direction.NORTH
        assert handler.get_next_command() == Direction.EAST
        assert handler.get_next_command() is None  # Queue empty

    def test_clear_queue(self):
        """Test clearing command queue."""
        handler = KeyboardHandler()

        # Queue commands
        handler.queue_command("w")
        handler.queue_command("a")
        handler.queue_command("s")

        # Clear queue
        handler.clear_queue()
        assert len(handler.command_queue) == 0
        assert handler.get_next_command() is None


class TestMovementIntegration:
    """Integration tests for complete movement system."""

    def test_full_movement_flow(self):
        """Test complete movement flow from input to position update."""
        # Setup
        floor = Floor(seed=12345)
        floor.generate()

        # Create clear path
        for i in range(5, 10):
            floor.tiles[(i, 5)] = Tile(i, 5, TileType.FLOOR)

        char = Character("Hero", 5, 5)
        handler = KeyboardHandler()

        # Simulate keyboard input
        handler.queue_command("d")  # East
        handler.queue_command("d")  # East
        handler.queue_command("w")  # North (wall above)
        handler.queue_command("d")  # East

        # Process commands
        moves_executed = 0
        while True:
            direction = handler.get_next_command()
            if direction is None:
                break

            if execute_move(char, direction, floor):
                moves_executed += 1

        # Should have moved east 3 times (north was blocked)
        assert char.position == (8, 5)
        assert moves_executed == 3

    def test_movement_performance(self):
        """Test movement system performance."""
        import time

        floor = Floor(seed=12345)
        floor.generate()

        # Make entire floor walkable for testing
        for pos, _tile in floor.tiles.items():
            floor.tiles[pos] = Tile(pos[0], pos[1], TileType.FLOOR)

        char = Character("Hero", 10, 10)

        # Time 1000 moves
        start = time.time()
        for _ in range(1000):
            for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
                execute_move(char, direction, floor)
        elapsed = time.time() - start

        # Should complete 4000 moves in under 100ms
        assert elapsed < 0.1
