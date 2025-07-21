#!/usr/bin/env python3
"""Enhanced floor visualization with statistics."""

from src.models.floor import Floor
from src.enums import TileType


def visualize_floor_with_room_numbers(floor: Floor) -> str:
    """Convert a floor to ASCII with room numbers.

    Args:
        floor: The floor to visualize

    Returns:
        ASCII string representation with numbered rooms
    """
    # Create a map of positions to room numbers
    room_map = {}
    for i, room in enumerate(floor.rooms):
        # Mark the center of each room with its number
        center_x = room.x + room.width // 2
        center_y = room.y + room.height // 2
        room_map[(center_x, center_y)] = str(i + 1)

    lines = []
    lines.append("+" + "-" * floor.FLOOR_WIDTH + "+")

    for y in range(floor.FLOOR_HEIGHT):
        row = "|"
        for x in range(floor.FLOOR_WIDTH):
            if (x, y) in room_map:
                row += room_map[(x, y)]
            else:
                tile = floor.get_tile(x, y)
                if tile is None:
                    row += "?"
                elif tile.tile_type == TileType.WALL:
                    row += "#"
                elif tile.tile_type == TileType.FLOOR:
                    row += "."
                else:
                    row += " "
        row += "|"
        lines.append(row)

    lines.append("+" + "-" * floor.FLOOR_WIDTH + "+")
    return "\n".join(lines)


def calculate_floor_statistics(floor: Floor) -> dict:
    """Calculate statistics about the floor.

    Args:
        floor: The floor to analyze

    Returns:
        Dictionary of statistics
    """
    total_tiles = floor.FLOOR_WIDTH * floor.FLOOR_HEIGHT
    floor_tiles = 0
    wall_tiles = 0

    for y in range(floor.FLOOR_HEIGHT):
        for x in range(floor.FLOOR_WIDTH):
            tile = floor.get_tile(x, y)
            if tile and tile.tile_type == TileType.FLOOR:
                floor_tiles += 1
            else:
                wall_tiles += 1

    total_room_area = sum(room.width * room.height for room in floor.rooms)

    return {
        "total_tiles": total_tiles,
        "floor_tiles": floor_tiles,
        "wall_tiles": wall_tiles,
        "floor_percentage": (floor_tiles / total_tiles) * 100,
        "room_count": len(floor.rooms),
        "average_room_area": total_room_area / len(floor.rooms) if floor.rooms else 0,
        "min_room_area": min(room.width * room.height for room in floor.rooms)
        if floor.rooms
        else 0,
        "max_room_area": max(room.width * room.height for room in floor.rooms)
        if floor.rooms
        else 0,
    }


def main():
    """Generate and display floors with enhanced visualization."""
    print("=== ASCENDANT: Floor Generation Showcase ===")
    print("\nLegend:")
    print("  # = Wall")
    print("  . = Floor")
    print("  1-9 = Room center (room number)")
    print()

    # Show two example floors in detail
    example_seeds = [12345, 77777]

    for seed in example_seeds:
        floor = Floor(seed)
        floor.generate()

        print(f"\n{'='*50}")
        print(f"Floor Generated with Seed: {seed}")
        print(f"{'='*50}")

        # Show room details
        print(f"\nRooms ({len(floor.rooms)} total):")
        for i, room in enumerate(floor.rooms):
            area = room.width * room.height
            print(
                f"  Room {i+1}: Position ({room.x},{room.y}), Size {room.width}x{room.height}, Area {area} tiles"
            )

        # Show statistics
        stats = calculate_floor_statistics(floor)
        print("\nStatistics:")
        print(f"  Total tiles: {stats['total_tiles']}")
        print(f"  Floor tiles: {stats['floor_tiles']} ({stats['floor_percentage']:.1f}%)")
        print(f"  Wall tiles: {stats['wall_tiles']} ({100-stats['floor_percentage']:.1f}%)")
        print(f"  Average room area: {stats['average_room_area']:.1f} tiles")
        print(f"  Room size range: {stats['min_room_area']}-{stats['max_room_area']} tiles")

        # Show visualization
        print("\nFloor Layout:")
        print(visualize_floor_with_room_numbers(floor))

    # Quick comparison of multiple seeds
    print(f"\n\n{'='*50}")
    print("Quick Comparison - 5 Different Seeds")
    print(f"{'='*50}")
    print(f"{'Seed':<10} {'Rooms':<8} {'Floor %':<10} {'Avg Room':<10}")
    print("-" * 40)

    for seed in [12345, 54321, 99999, 11111, 77777]:
        floor = Floor(seed)
        floor.generate()
        stats = calculate_floor_statistics(floor)
        print(
            f"{seed:<10} {stats['room_count']:<8} {stats['floor_percentage']:<10.1f} {stats['average_room_area']:<10.1f}"
        )


if __name__ == "__main__":
    main()
