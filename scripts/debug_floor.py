#!/usr/bin/env python3
"""Debug floor generation to show room boundaries clearly."""

from src.enums import TileType
from src.models.floor import Floor


def show_floor_with_boundaries(seed: int):
    """Show a floor with room boundaries marked."""
    floor = Floor(seed)
    floor.generate()

    print(f"\nFloor with seed {seed}:")
    print(f"Number of rooms: {len(floor.rooms)}")

    # First, let's list all the rooms
    for i, room in enumerate(floor.rooms):
        print(
            f"  Room {i+1}: x={room.x}-{room.x2}, y={room.y}-{room.y2} (size: {room.width}x{room.height})"
        )

    print("\nFloor layout (with room numbers):")

    # Create a map that shows which room each tile belongs to
    room_map = {}
    for i, room in enumerate(floor.rooms):
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                room_map[(x, y)] = str(i + 1)

    # Show the floor with room numbers
    for y in range(floor.FLOOR_HEIGHT):
        row = ""
        for x in range(floor.FLOOR_WIDTH):
            if (x, y) in room_map:
                row += room_map[(x, y)]
            else:
                row += "#"
        # Add spaces between characters to make it more square
        print(" ".join(row))

    # Also show a version with just walls and floors
    print("\nFloor layout (walls and floors):")
    for y in range(floor.FLOOR_HEIGHT):
        row = ""
        for x in range(floor.FLOOR_WIDTH):
            tile = floor.get_tile(x, y)
            if tile and tile.tile_type == TileType.FLOOR:
                row += "."
            else:
                row += "#"
        print(" ".join(row))


def test_room_overlap():
    """Test if rooms are actually overlapping or just adjacent."""
    floor = Floor(12345)
    floor.generate()

    print("\nTesting room overlaps for seed 12345:")
    for i, room1 in enumerate(floor.rooms):
        for j, room2 in enumerate(floor.rooms[i + 1 :], i + 1):
            # Check if rooms are adjacent (touching but not overlapping)
            if room1.x2 + 1 == room2.x or room2.x2 + 1 == room1.x:
                if not (room1.y2 < room2.y or room2.y2 < room1.y):
                    print(f"  Rooms {i+1} and {j+1} are horizontally adjacent")
            elif room1.y2 + 1 == room2.y or room2.y2 + 1 == room1.y:
                if not (room1.x2 < room2.x or room2.x2 < room1.x):
                    print(f"  Rooms {i+1} and {j+1} are vertically adjacent")

            # Verify no overlap
            if room1.overlaps(room2):
                print(f"  ERROR: Rooms {i+1} and {j+1} overlap!")


def main():
    """Debug floor generation."""
    print("FLOOR GENERATION DEBUG")
    print("=" * 50)

    # Show floor 12345 in detail
    show_floor_with_boundaries(12345)

    # Test for overlaps/adjacency
    test_room_overlap()


if __name__ == "__main__":
    main()
