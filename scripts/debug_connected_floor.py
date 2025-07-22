"""Debug script to visualize connected floors with stairs."""

from src.models.floor import Floor


def visualize_connected_floor(seed: int = 12345) -> None:
    """Generate and display a connected floor with stairs."""
    floor = Floor(seed)
    floor.generate()
    floor.connect_rooms()
    floor.place_stairs()

    print(f"Floor with seed {seed}")
    print(f"Rooms: {len(floor.rooms)}")
    print(f"Fully connected: {floor.is_fully_connected()}")
    print()

    # Create ASCII visualization
    for y in range(floor.FLOOR_HEIGHT):
        for x in range(floor.FLOOR_WIDTH):
            tile = floor.get_tile(x, y)
            if tile:
                if tile.tile_type.name == "WALL":
                    print("#", end="")
                elif tile.tile_type.name == "FLOOR":
                    print(".", end="")
                elif tile.tile_type.name == "STAIRS_UP":
                    print(">", end="")
                else:
                    print("?", end="")
            else:
                print(" ", end="")
        print()

    print("\nLegend: # = wall, . = floor, > = stairs up")


if __name__ == "__main__":
    # Show a few different floors
    for seed in [12345, 54321, 99999]:
        visualize_connected_floor(seed)
        print("\n" + "=" * 40 + "\n")
