"""Tests for monster spawning system.

Generated with AI assistance (Claude Opus 4) - 2025-07-23
Part of Phase 4.1 Monster Implementation
"""

from src.enums import TileType
from src.game.monster_spawner import MonsterSpawner
from src.models.floor import Floor, Room
from src.models.monster import AIBehavior, Monster
from src.models.tile import Tile


class TestMonsterSpawner:
    """Test cases for monster spawning system."""

    def setup_method(self):
        """Create test floor with rooms."""
        self.floor = Floor(width=30, height=30, level=1)

        # Add some test rooms
        self.room1 = Room(x=2, y=2, width=6, height=6)
        self.room2 = Room(x=12, y=12, width=8, height=8)
        self.room3 = Room(x=22, y=5, width=5, height=5)

        self.floor.rooms = [self.room1, self.room2, self.room3]

        # Mark room tiles as floor
        for room in self.floor.rooms:
            for x in range(room.x, room.x + room.width):
                for y in range(room.y, room.y + room.height):
                    self.floor.tiles[(x, y)] = Tile(x, y, TileType.FLOOR)

        # Add stairs for spawn exclusion testing
        self.floor.tiles[(3, 3)] = Tile(3, 3, TileType.STAIRS_UP)
        self.floor.tiles[(25, 7)] = Tile(25, 7, TileType.STAIRS_DOWN)

    def test_spawner_creation(self):
        """Test monster spawner initialization."""
        spawner = MonsterSpawner()
        assert spawner is not None

    def test_spawn_monsters_basic(self):
        """Test basic monster spawning."""
        spawner = MonsterSpawner()
        monsters = spawner.spawn_monsters(self.floor, count=5, level=1)

        assert len(monsters) == 5
        assert all(isinstance(m, Monster) for m in monsters)

        # Check all monsters are in valid positions
        for monster in monsters:
            tile = self.floor.tiles.get(monster.position)
            assert tile is not None and tile.tile_type == TileType.FLOOR
            # Not on stairs
            assert monster.position not in [(3, 3), (25, 7)]

    def test_monsters_only_spawn_in_rooms(self):
        """Test monsters only spawn inside rooms."""
        spawner = MonsterSpawner()
        monsters = spawner.spawn_monsters(self.floor, count=10, level=1)

        for monster in monsters:
            # Check monster is in at least one room
            in_room = False
            for room in self.floor.rooms:
                if room.contains_point(monster.x, monster.y):
                    in_room = True
                    break
            assert in_room, f"Monster at {monster.position} not in any room"

    def test_no_overlapping_monsters(self):
        """Test monsters don't spawn on top of each other."""
        spawner = MonsterSpawner()
        monsters = spawner.spawn_monsters(self.floor, count=8, level=1)

        positions = [m.position for m in monsters]
        assert len(positions) == len(set(positions)), "Monsters spawned at same position"

    def test_monster_stats_scale_with_level(self):
        """Test monster stats increase with floor level."""
        spawner = MonsterSpawner()

        # Level 1 monsters
        monsters_l1 = spawner.spawn_monsters(self.floor, count=3, level=1)
        avg_hp_l1 = sum(m.hp_max for m in monsters_l1) / len(monsters_l1)
        avg_atk_l1 = sum(m.attack for m in monsters_l1) / len(monsters_l1)

        # Level 5 monsters
        self.floor.level = 5
        monsters_l5 = spawner.spawn_monsters(self.floor, count=3, level=5)
        avg_hp_l5 = sum(m.hp_max for m in monsters_l5) / len(monsters_l5)
        avg_atk_l5 = sum(m.attack for m in monsters_l5) / len(monsters_l5)

        # Level 5 monsters should be stronger
        assert avg_hp_l5 > avg_hp_l1
        assert avg_atk_l5 > avg_atk_l1

    def test_monster_types_by_level(self):
        """Test different monster types appear at different levels."""
        spawner = MonsterSpawner()

        # Low level - basic monsters
        monsters_l1 = spawner.spawn_monsters(self.floor, count=10, level=1)
        types_l1 = {m.monster_type for m in monsters_l1}
        assert "goblin" in types_l1 or "skeleton" in types_l1 or "rat" in types_l1

        # High level - advanced monsters
        self.floor.level = 10
        monsters_l10 = spawner.spawn_monsters(self.floor, count=10, level=10)
        types_l10 = {m.monster_type for m in monsters_l10}
        # Should have some different types at higher levels
        assert types_l10 != types_l1 or any(m.hp_max > 20 for m in monsters_l10)

    def test_spawn_with_no_valid_positions(self):
        """Test spawning handles case with no valid positions."""
        # Fill all room tiles
        for room in self.floor.rooms:
            for x in range(room.x, room.x + room.width):
                for y in range(room.y, room.y + room.height):
                    self.floor.tiles[(x, y)] = Tile(x, y, TileType.WALL)

        spawner = MonsterSpawner()
        monsters = spawner.spawn_monsters(self.floor, count=5, level=1)

        # Should return empty list or partial list
        assert len(monsters) == 0

    def test_spawn_excludes_player_position(self):
        """Test monsters don't spawn on player start position."""
        spawner = MonsterSpawner()

        # Assume player starts at first room center
        player_pos = self.room1.center()
        monsters = spawner.spawn_monsters(
            self.floor, count=20, level=1, exclude_positions=[player_pos]
        )

        for monster in monsters:
            assert monster.position != player_pos

    def test_monster_ai_behavior_assignment(self):
        """Test monsters get appropriate AI behaviors."""
        spawner = MonsterSpawner()
        monsters = spawner.spawn_monsters(self.floor, count=10, level=1)

        behaviors = {m.ai_behavior for m in monsters}
        # Should have at least some variety
        assert len(behaviors) >= 1
        assert all(isinstance(b, AIBehavior) for m in monsters for b in [m.ai_behavior])

    def test_get_monster_stats(self):
        """Test monster stat generation."""
        spawner = MonsterSpawner()

        # Test goblin stats
        stats = spawner.get_monster_stats("goblin", level=1)
        assert stats["hp"] >= 5
        assert stats["attack"] >= 2
        assert stats["defense"] >= 0
        assert stats["display_char"] == "g"

        # Test scaling
        stats_l5 = spawner.get_monster_stats("goblin", level=5)
        assert stats_l5["hp"] > stats["hp"]
        assert stats_l5["attack"] >= stats["attack"]

    def test_spawn_specific_monster_type(self):
        """Test spawning specific monster types."""
        spawner = MonsterSpawner()

        # Spawn only goblins
        monsters = spawner.spawn_monsters(self.floor, count=5, level=1, monster_types=["goblin"])

        assert all(m.monster_type == "goblin" for m in monsters)

    def test_spawn_respects_room_capacity(self):
        """Test spawning doesn't overcrowd small rooms."""
        # Create a tiny room
        tiny_room = Room(x=1, y=1, width=3, height=3)  # 9 tiles total
        self.floor.rooms = [tiny_room]

        # Mark as floor
        for x in range(1, 4):
            for y in range(1, 4):
                self.floor.tiles[(x, y)] = Tile(x, y, TileType.FLOOR)

        spawner = MonsterSpawner()
        # Try to spawn more monsters than room can hold
        monsters = spawner.spawn_monsters(self.floor, count=20, level=1)

        # Should be limited by available space
        assert len(monsters) <= 9  # Can't exceed room size
