#!/usr/bin/env python3
"""Visualize generated floors for debugging."""

from src.enums import TileType
from src.models.floor import Floor


def visualize_floor(floor: Floor) -> str:
    """Convert a floor to ASCII representation.

    Args:
        floor: The floor to visualize

    Returns:
        ASCII string representation of the floor
    """
    lines = []

    # Add top border
    lines.append("+" + "-" * floor.FLOOR_WIDTH + "+")

    # Add each row
    for y in range(floor.FLOOR_HEIGHT):
        row = "|"
        for x in range(floor.FLOOR_WIDTH):
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

    # Add bottom border
    lines.append("+" + "-" * floor.FLOOR_WIDTH + "+")

    return "\n".join(lines)


def main():
    """Generate and display several floors."""
    seeds = [12345, 54321, 99999, 11111, 77777]

    for seed in seeds:
        print(f"\n=== Floor with seed {seed} ===")
        floor = Floor(seed)
        floor.generate()

        print(f"Rooms: {len(floor.rooms)}")
        for i, room in enumerate(floor.rooms):
            print(f"  Room {i+1}: {room}")

        print("\nVisualization:")
        print(visualize_floor(floor))
        print()


if __name__ == "__main__":
    main()
