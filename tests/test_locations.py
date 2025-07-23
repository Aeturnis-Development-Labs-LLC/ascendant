"""Tests for location system."""

from src.enums import LocationType, TileType
from src.models.character import Character
from src.models.location import DungeonEntrance, SafeHaven, TowerEntrance


class TestSafeHaven:
    """Tests for SafeHaven location."""

    def test_safe_haven_initialization(self):
        """Test Safe Haven is created correctly."""
        haven = SafeHaven()
        assert haven.position == (37, 37)
        assert haven.name == "Safe Haven"
        assert haven.location_type == LocationType.SAFE_HAVEN
        assert haven.discovered is True  # Always discovered
        assert haven.no_combat is True
        assert haven.interior_size == 5
        assert haven.spawn_point == (2, 2)

    def test_safe_haven_can_always_enter(self):
        """Test Safe Haven can always be entered."""
        haven = SafeHaven()
        char = Character("TestHero", 10, 10)

        can_enter, reason = haven.can_enter(char)
        assert can_enter is True
        assert reason == ""

    def test_safe_haven_display_symbol(self):
        """Test Safe Haven display symbol."""
        haven = SafeHaven()
        assert haven.get_display_symbol() == "[H]"

    def test_safe_haven_interior_creation(self):
        """Test Safe Haven interior layout."""
        haven = SafeHaven()
        interior = haven.create_interior()

        # Floor is always 50x50
        assert interior.width == 50
        assert interior.height == 50

        # Check center 5x5 area is cleared to floor
        center_start = (50 - 5) // 2  # 22
        center_end = center_start + 5  # 27
        floor_count = 0

        for y in range(center_start, center_end):
            for x in range(center_start, center_end):
                if interior.tiles[(x, y)].tile_type == TileType.FLOOR:
                    floor_count += 1

        assert floor_count >= 20  # At least most of the 5x5 area should be floor


class TestDungeonEntrance:
    """Tests for DungeonEntrance location."""

    def test_dungeon_entrance_creation(self):
        """Test creating a dungeon entrance."""
        dungeon = DungeonEntrance(
            position=(10, 20), name="Test Dungeon", min_level=10, max_level=19, floor_count=4
        )

        assert dungeon.position == (10, 20)
        assert dungeon.name == "Test Dungeon"
        assert dungeon.location_type == LocationType.DUNGEON_ENTRANCE
        assert dungeon.min_level == 10
        assert dungeon.max_level == 19
        assert dungeon.floor_count == 4
        assert dungeon.discovered is False
        assert len(dungeon.completed_by) == 0

    def test_dungeon_level_restrictions(self):
        """Test dungeon entry level restrictions."""
        dungeon = DungeonEntrance((10, 10), "Level 10-19", 10, 19, 4)

        # Character with no level defaults to 1
        char_low = Character("LowLevel", 0, 0)
        can_enter, reason = dungeon.can_enter(char_low)
        assert can_enter is False
        assert "at least level 10" in reason

        # Character at min level can enter
        char_min = Character("MinLevel", 0, 0)
        char_min.level = 10
        can_enter, reason = dungeon.can_enter(char_min)
        assert can_enter is True
        assert reason == ""

        # Character at max level can enter
        char_max = Character("MaxLevel", 0, 0)
        char_max.level = 19
        can_enter, reason = dungeon.can_enter(char_max)
        assert can_enter is True
        assert reason == ""

        # Character over max level cannot enter
        char_high = Character("HighLevel", 0, 0)
        char_high.level = 20
        can_enter, reason = dungeon.can_enter(char_high)
        assert can_enter is False
        assert "too high level" in reason

    def test_dungeon_display_symbols(self):
        """Test dungeon bracket display symbols."""
        # Bracket 1 (1-9)
        d1 = DungeonEntrance((0, 0), "D1", 1, 9, 3)
        d1.discovered = True
        assert d1.get_display_symbol() == "[1]"

        # Bracket 2 (10-19)
        d2 = DungeonEntrance((0, 0), "D2", 10, 19, 4)
        d2.discovered = True
        assert d2.get_display_symbol() == "[2]"

        # Bracket 5 (40-49)
        d5 = DungeonEntrance((0, 0), "D5", 40, 49, 7)
        d5.discovered = True
        assert d5.get_display_symbol() == "[5]"

        # High bracket (90-99)
        d10 = DungeonEntrance((0, 0), "D10", 90, 99, 10)
        d10.discovered = True
        assert d10.get_display_symbol() == "[D]"

        # Undiscovered
        d_hidden = DungeonEntrance((0, 0), "Hidden", 1, 9, 3)
        d_hidden.discovered = False
        assert d_hidden.get_display_symbol() == "?"


class TestTowerEntrance:
    """Tests for TowerEntrance location."""

    def test_tower_entrance_initialization(self):
        """Test Tower entrance is created correctly."""
        tower = TowerEntrance()
        assert tower.position == (37, 36)  # 1 north of Safe Haven
        assert tower.name == "The Eternal Spire"
        assert tower.location_type == LocationType.TOWER_ENTRANCE
        assert tower.discovered is False
        assert tower.min_level_requirement == 10
        assert tower.dungeon_requirement == 1

    def test_tower_entry_requirements(self):
        """Test Tower entry requirements."""
        tower = TowerEntrance()

        # Low level character
        char_low = Character("Newbie", 0, 0)
        char_low.level = 5
        char_low.dungeons_completed = 0
        can_enter, reason = tower.can_enter(char_low)
        assert can_enter is False
        assert "level 10" in reason

        # High enough level but no dungeons
        char_no_dungeon = Character("NoDungeons", 0, 0)
        char_no_dungeon.level = 15
        char_no_dungeon.dungeons_completed = 0
        can_enter, reason = tower.can_enter(char_no_dungeon)
        assert can_enter is False
        assert "1 dungeon" in reason

        # Meets all requirements
        char_ready = Character("Ready", 0, 0)
        char_ready.level = 15
        char_ready.dungeons_completed = 2
        can_enter, reason = tower.can_enter(char_ready)
        assert can_enter is True
        assert reason == ""

    def test_tower_display_symbol(self):
        """Test Tower display symbol."""
        tower = TowerEntrance()

        # Undiscovered
        assert tower.get_display_symbol() == "?"

        # Discovered
        tower.discover()
        assert tower.get_display_symbol() == "[T]"


class TestLocationBase:
    """Tests for base Location functionality."""

    def test_location_discovery(self):
        """Test location discovery mechanism."""
        dungeon = DungeonEntrance((10, 10), "Test", 1, 9, 3)

        assert dungeon.discovered is False

        dungeon.discover()
        assert dungeon.discovered is True

    def test_location_description(self):
        """Test location descriptions."""
        haven = SafeHaven()
        assert "peaceful town" in haven.description
        assert "no combat" in haven.description.lower()

        tower = TowerEntrance()
        assert "obsidian" in tower.description
        assert "ultimate challenge" in tower.description

        dungeon = DungeonEntrance((0, 0), "Test", 10, 19, 4)
        assert "level 10-19" in dungeon.description
