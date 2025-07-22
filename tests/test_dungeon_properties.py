"""Tests for dungeon properties system."""

import pytest

from src.game.dungeon_properties import DungeonProperties, DungeonRestrictions
from src.models.floor import Floor


class TestDungeonRestrictions:
    """Tests for DungeonRestrictions dataclass."""

    def test_default_restrictions(self):
        """Test default restriction values."""
        restrictions = DungeonRestrictions()

        assert restrictions.xp_multiplier == 0.5
        assert restrictions.rare_items_disabled is True
        assert restrictions.completion_count == 0


class TestDungeonProperties:
    """Tests for dungeon properties management."""

    @pytest.fixture
    def dungeon_props(self):
        """Create a DungeonProperties instance."""
        return DungeonProperties()

    def test_floor_counts_by_bracket(self, dungeon_props):
        """Test floor counts increase with level brackets."""
        assert dungeon_props.get_floor_count((1, 9)) == 3
        assert dungeon_props.get_floor_count((10, 19)) == 4
        assert dungeon_props.get_floor_count((20, 29)) == 5
        assert dungeon_props.get_floor_count((40, 49)) == 7
        assert dungeon_props.get_floor_count((90, 99)) == 12

    def test_bracket_names(self, dungeon_props):
        """Test bracket display names."""
        assert dungeon_props.get_bracket_name((1, 9)) == "Novice Hollow"
        assert dungeon_props.get_bracket_name((10, 19)) == "Apprentice Caverns"
        assert dungeon_props.get_bracket_name((50, 59)) == "Grandmaster Tombs"
        assert dungeon_props.get_bracket_name((90, 99)) == "Mythic Sanctum"

    def test_unknown_bracket(self, dungeon_props):
        """Test handling of unknown brackets."""
        # Bracket not in predefined list
        assert dungeon_props.get_floor_count((100, 109)) == 3  # Default
        assert "Unknown Dungeon" in dungeon_props.get_bracket_name((100, 109))

    def test_generate_fixed_layout(self, dungeon_props):
        """Test fixed layout generation is deterministic."""
        bracket = (10, 19)

        # Generate same floor twice
        floor1 = dungeon_props.generate_fixed_layout(42, bracket, 1)
        floor2 = dungeon_props.generate_fixed_layout(42, bracket, 1)

        # Should have same layout (deterministic)
        assert floor1.seed == floor2.seed

        # Different floor numbers should have different seeds
        floor3 = dungeon_props.generate_fixed_layout(42, bracket, 2)
        assert floor1.seed != floor3.seed

    def test_bracket_features(self, dungeon_props):
        """Test bracket-specific features are added."""
        # Low level dungeon
        low_floor = dungeon_props.generate_fixed_layout(42, (1, 9), 1)

        # High level dungeon
        high_floor = dungeon_props.generate_fixed_layout(42, (50, 59), 1)

        # Both should be valid floors
        assert isinstance(low_floor, Floor)
        assert isinstance(high_floor, Floor)

        # High level should have more features (tested via trap/chest placement)
        # This is implementation detail, but we can verify floors are generated
        assert low_floor.width == Floor.FLOOR_WIDTH
        assert high_floor.width == Floor.FLOOR_WIDTH

    def test_track_completion(self, dungeon_props):
        """Test tracking dungeon completions."""
        char_id = "hero123"
        bracket = (10, 19)

        # First completion
        dungeon_props.track_completion(char_id, bracket)
        restrictions = dungeon_props.get_replay_restrictions(char_id, bracket)

        assert restrictions is not None
        assert restrictions.completion_count == 1

        # Second completion
        dungeon_props.track_completion(char_id, bracket)
        restrictions = dungeon_props.get_replay_restrictions(char_id, bracket)
        assert restrictions.completion_count == 2

    def test_is_first_completion(self, dungeon_props):
        """Test checking for first completion."""
        char_id = "hero123"
        bracket = (10, 19)

        # Should be first completion
        assert dungeon_props.is_first_completion(char_id, bracket) is True

        # Track completion
        dungeon_props.track_completion(char_id, bracket)

        # No longer first completion
        assert dungeon_props.is_first_completion(char_id, bracket) is False

    def test_replay_restrictions(self, dungeon_props):
        """Test replay restrictions are applied."""
        char_id = "hero123"
        bracket = (10, 19)

        # No restrictions before completion
        assert dungeon_props.get_replay_restrictions(char_id, bracket) is None

        # Complete dungeon
        dungeon_props.track_completion(char_id, bracket)
        restrictions = dungeon_props.get_replay_restrictions(char_id, bracket)

        assert restrictions is not None
        assert restrictions.xp_multiplier == 0.5
        assert restrictions.rare_items_disabled is True

    def test_multiple_characters(self, dungeon_props):
        """Test tracking works independently for different characters."""
        char1 = "hero1"
        char2 = "hero2"
        bracket = (10, 19)

        # Char1 completes dungeon
        dungeon_props.track_completion(char1, bracket)

        # Char2 hasn't completed it
        assert dungeon_props.is_first_completion(char2, bracket) is True
        assert dungeon_props.get_replay_restrictions(char2, bracket) is None

    def test_get_completed_dungeons(self, dungeon_props):
        """Test retrieving set of completed dungeons."""
        char_id = "hero123"

        # No completions initially
        assert len(dungeon_props.get_completed_dungeons(char_id)) == 0

        # Complete some dungeons
        dungeon_props.track_completion(char_id, (1, 9))
        dungeon_props.track_completion(char_id, (10, 19))
        dungeon_props.track_completion(char_id, (20, 29))

        completed = dungeon_props.get_completed_dungeons(char_id)
        assert len(completed) == 3
        assert (1, 9) in completed
        assert (10, 19) in completed
        assert (20, 29) in completed

    def test_get_dungeon_info(self, dungeon_props):
        """Test getting full dungeon information."""
        bracket = (10, 19)
        info = dungeon_props.get_dungeon_info(bracket)

        assert info["name"] == "Apprentice Caverns"
        assert info["level_range"] == bracket
        assert info["floor_count"] == 4
        assert info["min_level"] == 10
        assert info["max_level"] == 19
