"""Safe Haven interior layout and mechanics."""

from typing import Dict, Optional, Tuple

from src.enums import TileType
from src.models.character import Character
from src.models.floor import Floor
from src.models.location import SafeHaven as BaseSafeHaven


class SafeHavenInterior:
    """Enhanced Safe Haven with detailed interior layout."""

    # Interior zones in the 5x5 grid
    SPAWN_PLAZA = (2, 2)  # Center
    MERCHANT_QUARTER = (3, 2)  # East
    HALL_OF_SOULS = (1, 2)  # West
    STORAGE_VAULTS = (2, 3)  # South
    LOST_SOUL_MEMORIAL = (2, 1)  # North

    def __init__(self):
        """Initialize Safe Haven interior."""
        self.width = 50  # Full floor width
        self.height = 50  # Full floor height
        self.no_combat_zone = True
        self.respawn_point = self.SPAWN_PLAZA
        self.zones: Dict[Tuple[int, int], str] = {
            self.SPAWN_PLAZA: "Spawn Plaza",
            self.MERCHANT_QUARTER: "Merchant Quarter",
            self.HALL_OF_SOULS: "Hall of Souls",
            self.STORAGE_VAULTS: "Storage Vaults",
            self.LOST_SOUL_MEMORIAL: "Lost Soul Memorial",
        }

    def create_detailed_interior(self) -> Floor:
        """Create detailed interior layout with named zones.

        Returns:
            Floor object with proper zone layout
        """
        # Create base floor
        interior = Floor(seed=42)  # Fixed seed for consistency
        interior.generate()

        # Clear the 5x5 center area
        center_start = (Floor.FLOOR_WIDTH - 5) // 2
        center_end = center_start + 5

        # Set all tiles in Safe Haven to floor
        for y in range(center_start, center_end):
            for x in range(center_start, center_end):
                interior.tiles[(x, y)].tile_type = TileType.FLOOR

        # Mark special zones (could be enhanced with NPCs/objects later)
        # For now, we'll just ensure they're accessible
        return interior

    def get_zone_at(self, position: Tuple[int, int]) -> Optional[str]:
        """Get the zone name at a given position.

        Args:
            position: (x, y) position in interior

        Returns:
            Zone name or None if not in a special zone
        """
        # Convert world position to local 5x5 coordinates
        center_start = (Floor.FLOOR_WIDTH - 5) // 2
        local_x = position[0] - center_start
        local_y = position[1] - center_start

        return self.zones.get((local_x, local_y))

    def is_in_safe_haven(self, position: Tuple[int, int]) -> bool:
        """Check if position is within Safe Haven boundaries.

        Args:
            position: (x, y) position to check

        Returns:
            True if within Safe Haven interior
        """
        center_start = (Floor.FLOOR_WIDTH - 5) // 2
        center_end = center_start + 5

        return center_start <= position[0] < center_end and center_start <= position[1] < center_end

    def can_attack(self, attacker: Character, target_pos: Tuple[int, int]) -> Tuple[bool, str]:
        """Check if attack is allowed in Safe Haven.

        Args:
            attacker: Character attempting to attack
            target_pos: Position being targeted

        Returns:
            Tuple of (allowed, reason)
        """
        if self.no_combat_zone:
            return (False, "Combat is forbidden in Safe Haven by ancient magic.")
        return (True, "")

    def get_respawn_position(self, is_lost_soul: bool = False) -> Tuple[int, int]:
        """Get respawn position based on character type.

        Args:
            is_lost_soul: True if respawning as Lost Soul

        Returns:
            (x, y) respawn position in world coordinates
        """
        center_start = (Floor.FLOOR_WIDTH - 5) // 2

        if is_lost_soul:
            # Lost Souls spawn at memorial
            local_pos = self.LOST_SOUL_MEMORIAL
        else:
            # New characters spawn at plaza
            local_pos = self.SPAWN_PLAZA

        return (center_start + local_pos[0], center_start + local_pos[1])


class EnhancedSafeHaven(BaseSafeHaven):
    """Safe Haven with enhanced interior mechanics."""

    def __init__(self):
        """Initialize enhanced Safe Haven."""
        super().__init__()
        self.interior = SafeHavenInterior()

    def create_interior(self) -> Floor:
        """Create the enhanced interior layout.

        Returns:
            Floor object with detailed zones
        """
        return self.interior.create_detailed_interior()

    def get_spawn_point(self, is_lost_soul: bool = False) -> Tuple[int, int]:
        """Get spawn point for character type.

        Args:
            is_lost_soul: True if character is a Lost Soul

        Returns:
            (x, y) spawn position
        """
        return self.interior.get_respawn_position(is_lost_soul)
