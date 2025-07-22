"""Escape mechanics for dungeons and special locations."""

from enum import Enum, auto
from typing import Optional, Tuple

from src.enums import LocationType
from src.models.character import Character
from src.models.location import Location


class RoomType(Enum):
    """Types of dungeon rooms."""

    NORMAL = auto()
    BOSS = auto()
    TREASURE = auto()
    ENTRANCE = auto()
    EXIT = auto()


class Room:
    """Represents a room in a dungeon."""

    def __init__(self, room_type: RoomType = RoomType.NORMAL):
        """Initialize a room.

        Args:
            room_type: Type of room
        """
        self.room_type = room_type
        self.boss_defeated = False

    def is_boss_room(self) -> bool:
        """Check if this is a boss room."""
        return self.room_type == RoomType.BOSS


class EscapeMechanics:
    """Handles escape rope and teleportation mechanics."""

    def __init__(self):
        """Initialize escape mechanics."""
        self.boss_room_lock_active = False
        self.current_location: Optional[Location] = None
        self.current_room: Optional[Room] = None

    def can_use_escape_rope(self, location: Optional[Location] = None) -> Tuple[bool, str]:
        """Check if escape rope can be used at current location.

        Args:
            location: Location to check (uses current if None)

        Returns:
            Tuple of (can_use, reason_if_not)
        """
        if location is None:
            location = self.current_location

        # Can't use in Safe Haven
        if location and location.location_type == LocationType.SAFE_HAVEN:
            return (False, "You're already in Safe Haven!")

        # Can't use in Tower
        if location and location.location_type == LocationType.TOWER_ENTRANCE:
            return (False, "The Tower's magic prevents escape!")

        # Can't use in boss room until boss is defeated
        if self.boss_room_lock(self.current_room):
            return (False, "The boss room is sealed! Defeat the boss first!")

        # Can use in dungeons and overworld
        return (True, "")

    def boss_room_lock(self, room: Optional[Room]) -> bool:
        """Check if room is locked due to boss fight.

        Args:
            room: Room to check

        Returns:
            True if room is locked (boss alive in boss room)
        """
        if room is None:
            return False

        # Boss rooms are locked until boss is defeated
        if room.is_boss_room() and not room.boss_defeated:
            self.boss_room_lock_active = True
            return True

        self.boss_room_lock_active = False
        return False

    def return_to_safe_haven(self, character: Character) -> Tuple[bool, str]:
        """Return character to Safe Haven using escape rope.

        Args:
            character: Character using escape rope

        Returns:
            Tuple of (success, message)
        """
        can_escape, reason = self.can_use_escape_rope()
        if not can_escape:
            return (False, reason)

        # Reset character position to Safe Haven
        # In a real implementation, this would interface with world navigation
        return (True, "You use the escape rope and return to Safe Haven!")

    def enter_location(self, location: Location) -> None:
        """Update current location for escape mechanics.

        Args:
            location: Location being entered
        """
        self.current_location = location
        self.current_room = None
        self.boss_room_lock_active = False

    def enter_room(self, room: Room) -> None:
        """Update current room for escape mechanics.

        Args:
            room: Room being entered
        """
        self.current_room = room

    def defeat_boss(self) -> None:
        """Mark current boss as defeated, unlocking the room."""
        if self.current_room and self.current_room.is_boss_room():
            self.current_room.boss_defeated = True
            self.boss_room_lock_active = False

    def can_use_town_portal(self) -> Tuple[bool, str]:
        """Check if town portal scroll can be used.

        Town portals work like escape ropes but are consumed on use.

        Returns:
            Tuple of (can_use, reason_if_not)
        """
        # Town portals follow same rules as escape ropes
        return self.can_use_escape_rope()

    def can_teleport_to_location(self, target_location: Location) -> Tuple[bool, str]:
        """Check if teleportation to a specific location is allowed.

        Args:
            target_location: Location to teleport to

        Returns:
            Tuple of (can_teleport, reason_if_not)
        """
        # Can't teleport while in boss fight
        if self.boss_room_lock(self.current_room):
            return (False, "Cannot teleport during boss fight!")

        # Can't teleport to undiscovered locations
        if not target_location.discovered:
            return (False, "Cannot teleport to undiscovered locations!")

        # Can't teleport into dungeons directly
        if target_location.location_type == LocationType.DUNGEON_ENTRANCE:
            return (False, "Cannot teleport directly into dungeons!")

        # Can't teleport into the Tower
        if target_location.location_type == LocationType.TOWER_ENTRANCE:
            return (False, "The Tower's magic blocks teleportation!")

        return (True, "")

    def get_escape_cost(self) -> int:
        """Get the cost of escaping from current location.

        Returns:
            Gold cost to escape (0 for escape rope, varies for services)
        """
        if self.current_location is None:
            return 0

        # Escape services might cost more from deeper locations
        # For now, escape rope is always free if you have one
        return 0
