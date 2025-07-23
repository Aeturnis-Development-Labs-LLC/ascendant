"""Simple movement functions for character movement."""

from typing import Tuple

from src.enums import Direction, TileType


def validate_position(pos: Tuple[int, int], floor) -> bool:
    """Check if a position is valid and walkable on the floor.

    Args:
        pos: (x, y) position to validate
        floor: Floor to check against

    Returns:
        True if position is within bounds and walkable
    """
    x, y = pos
    
    # Check bounds
    if not floor.is_valid_position(x, y):
        return False
    
    # Check if tile is walkable
    tile = floor.get_tile(x, y)
    if tile is None:
        return False
    
    # Check tile type
    walkable_tiles = {TileType.FLOOR, TileType.STAIRS_UP, TileType.STAIRS_DOWN}
    return tile.tile_type in walkable_tiles


def calculate_new_position(current: Tuple[int, int], direction: Direction) -> Tuple[int, int]:
    """Calculate new position based on direction.

    Args:
        current: Current (x, y) position
        direction: Direction to move

    Returns:
        New (x, y) position
    """
    x, y = current
    return (x + direction.dx, y + direction.dy)


def execute_move(character, direction: Direction, floor) -> bool:
    """Execute a move for a character.

    Args:
        character: Character to move
        direction: Direction to move
        floor: Current floor

    Returns:
        True if move was successful
    """
    # Calculate new position
    new_pos = calculate_new_position(character.position, direction)

    # Validate position is in bounds
    if not validate_position(new_pos, floor):
        return False

    # Check if tile is walkable
    tile = floor.get_tile(new_pos[0], new_pos[1])
    if tile is None:
        return False

    # Check tile type
    walkable_tiles = {TileType.FLOOR, TileType.STAIRS_UP, TileType.STAIRS_DOWN}
    if tile.tile_type not in walkable_tiles:
        return False

    # Execute the move
    character.move_to(new_pos)
    return True
