"""Fast travel system for world map movement."""

from enum import Enum, auto
from typing import Tuple


class TravelMethod(Enum):
    """Methods of fast travel."""

    WALK = auto()  # Free but slow
    CARRIAGE = auto()  # Costs gold, faster, encounter risk


class FastTravel:
    """Handles fast travel mechanics on the world map."""

    # Travel costs per GAME-WORLD-005 and GAME-WORLD-021
    CARRIAGE_COST_PER_10_TILES = 50  # 50 gold per 10 tiles
    CARRIAGE_SPEED_MULTIPLIER = 3.0  # 3x speed boost

    # Encounter chances per GAME-WORLD-006
    WALK_ENCOUNTER_CHANCE_PER_TILE = 0.05  # 5% per tile
    CARRIAGE_ENCOUNTER_CHANCE_TOTAL = 0.20  # 20% total for carriage trip

    def calculate_travel_cost(self, distance: float, method: TravelMethod) -> int:
        """Calculate the gold cost for travel.

        Args:
            distance: Distance in tiles
            method: Method of travel

        Returns:
            Cost in gold (0 for walking)
        """
        if method == TravelMethod.WALK:
            return 0
        else:  # TravelMethod.CARRIAGE
            # Carriage costs 50g per 10 tiles
            tile_blocks = distance / 10.0
            return int(tile_blocks * self.CARRIAGE_COST_PER_10_TILES)

    def travel_time(
        self, distance: float, method: TravelMethod, terrain_modifier: float = 1.0
    ) -> float:
        """Calculate travel time based on method and terrain.

        Args:
            distance: Distance in tiles
            method: Method of travel
            terrain_modifier: Terrain movement cost modifier

        Returns:
            Time in turns
        """
        base_time = distance / terrain_modifier

        if method == TravelMethod.CARRIAGE:
            # Carriage is 3x faster
            return base_time / self.CARRIAGE_SPEED_MULTIPLIER

        return base_time

    def trigger_encounter_check(
        self, method: TravelMethod, distance: float, rng_value: float
    ) -> bool:
        """Check if an encounter should trigger during travel.

        Args:
            method: Method of travel
            distance: Distance traveled
            rng_value: Random value [0, 1) for encounter check

        Returns:
            True if encounter should trigger
        """
        if method == TravelMethod.WALK:
            # 5% per tile, compounded
            no_encounter_chance = (1.0 - self.WALK_ENCOUNTER_CHANCE_PER_TILE) ** distance
            encounter_chance = 1.0 - no_encounter_chance
            return bool(rng_value < encounter_chance)
        else:  # TravelMethod.CARRIAGE
            # Flat 20% for entire trip
            return bool(rng_value < self.CARRIAGE_ENCOUNTER_CHANCE_TOTAL)

    def can_afford_travel(self, player_gold: int, distance: float, method: TravelMethod) -> bool:
        """Check if player can afford the travel cost.

        Args:
            player_gold: Player's current gold
            distance: Distance to travel
            method: Method of travel

        Returns:
            True if player can afford it
        """
        cost = self.calculate_travel_cost(distance, method)
        return player_gold >= cost

    def validate_travel_destination(
        self, destination: Tuple[int, int], discovered_locations: set[Tuple[int, int]]
    ) -> Tuple[bool, str]:
        """Validate if player can travel to destination.

        Args:
            destination: Target location coordinates
            discovered_locations: Set of discovered location positions

        Returns:
            Tuple of (can_travel, reason_if_not)
        """
        if destination not in discovered_locations:
            return (False, "You cannot travel to undiscovered locations.")
        return (True, "")

    def get_carriage_route_tiles(self, start: Tuple[int, int], end: Tuple[int, int]) -> int:
        """Calculate manhattan distance for carriage routes.

        Carriages follow roads/direct paths, not diagonal movement.

        Args:
            start: Starting position (x, y)
            end: Ending position (x, y)

        Returns:
            Number of tiles for the route
        """
        dx = abs(end[0] - start[0])
        dy = abs(end[1] - start[1])
        return dx + dy
