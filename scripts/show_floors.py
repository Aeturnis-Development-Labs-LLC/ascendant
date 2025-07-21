#!/usr/bin/env python3
"""Simple floor visualization."""

from src.models.floor import Floor
from src.enums import TileType


def show_floor(seed: int):
    """Show a floor with the given seed."""
    floor = Floor(seed)
    floor.generate()

    print(f"\nFloor with seed {seed}:")
    print(f"Number of rooms: {len(floor.rooms)}")

    # Create the map
    for y in range(floor.FLOOR_HEIGHT):
        row = ""
        for x in range(floor.FLOOR_WIDTH):
            tile = floor.get_tile(x, y)
            if tile and tile.tile_type == TileType.FLOOR:
                row += "."  # Floor tiles are walkable
            else:
                row += "#"  # Wall tiles are solid
        print(row)


def main():
    """Show a few example floors."""
    print("ASCENDANT FLOOR GENERATION")
    print("# = Wall (solid)")
    print(". = Floor (walkable room space)")

    # Show 3 different floors
    for seed in [12345, 54321, 99999]:
        show_floor(seed)
        print()  # Empty line between floors


if __name__ == "__main__":
    main()
