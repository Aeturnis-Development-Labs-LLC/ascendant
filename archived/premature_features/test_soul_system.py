"""Tests for Lost Soul system."""

import pytest

from src.game.soul_system import Achievement, LostSoul, SoulSystem


class TestAchievement:
    """Tests for Achievement dataclass."""

    def test_achievement_creation(self):
        """Test creating an achievement."""
        achievement = Achievement(
            id="test_badge",
            name="Test Badge",
            description="A test achievement",
            bonus_type="hp",
            bonus_value=10,
        )

        assert achievement.id == "test_badge"
        assert achievement.name == "Test Badge"
        assert achievement.bonus_type == "hp"
        assert achievement.bonus_value == 10


class TestLostSoul:
    """Tests for LostSoul dataclass."""

    def test_lost_soul_creation(self):
        """Test creating a Lost Soul."""
        badges = [
            Achievement("badge1", "Badge 1", "Test", "hp", 5),
            Achievement("badge2", "Badge 2", "Test", "attack", 2),
        ]

        soul = LostSoul(
            character_name="Fallen Hero",
            level=15,
            death_floor=8,
            death_message="Slain by a goblin",
            soul_badges=badges,
            total_play_time=3600.0,
            monsters_killed=50,
            floors_cleared=7,
        )

        assert soul.character_name == "Fallen Hero"
        assert soul.level == 15
        assert soul.death_floor == 8
        assert len(soul.soul_badges) == 2
        assert soul.total_play_time == 3600.0


class TestSoulSystem:
    """Tests for soul system mechanics."""

    @pytest.fixture
    def soul_system(self):
        """Create a SoulSystem instance."""
        return SoulSystem()

    def test_create_lost_soul(self, soul_system):
        """Test creating a Lost Soul from a dead character."""
        soul = soul_system.create_lost_soul(
            character_name="Test Hero",
            level=12,
            death_floor=5,
            death_message="Crushed by a boulder",
            play_time=7200.0,  # 2 hours
            monsters_killed=150,
            floors_cleared=4,
        )

        assert soul.character_name == "Test Hero"
        assert soul.level == 12
        assert len(soul_system.lost_souls) == 1
        assert soul_system.lost_souls[0] == soul

    def test_death_badges_level_based(self, soul_system):
        """Test level-based badge awards."""
        # Level 10+ character
        soul1 = soul_system.create_lost_soul("Veteran", 10, 5, "Died", 3600.0, 50, 4)
        badge_ids = {badge.id for badge in soul1.soul_badges}
        assert "veteran_soul" in badge_ids

        # Level 25+ character
        soul2 = soul_system.create_lost_soul("Expert", 25, 10, "Died", 3600.0, 50, 9)
        badge_ids = {badge.id for badge in soul2.soul_badges}
        assert "veteran_soul" in badge_ids
        assert "experienced_soul" in badge_ids

    def test_death_badges_floor_based(self, soul_system):
        """Test floor-based badge awards."""
        soul = soul_system.create_lost_soul("Deep Explorer", 5, 10, "Died", 3600.0, 50, 9)
        badge_ids = {badge.id for badge in soul.soul_badges}
        assert "deep_delver" in badge_ids

    def test_death_badges_combat_based(self, soul_system):
        """Test combat-based badge awards."""
        soul = soul_system.create_lost_soul("Warrior", 5, 3, "Died", 3600.0, 100, 2)
        badge_ids = {badge.id for badge in soul.soul_badges}
        assert "monster_slayer" in badge_ids

    def test_death_badges_time_based(self, soul_system):
        """Test time-based badge awards."""
        soul = soul_system.create_lost_soul("Dedicated", 5, 3, "Died", 18000.0, 50, 2)  # 5 hours
        badge_ids = {badge.id for badge in soul.soul_badges}
        assert "dedicated_soul" in badge_ids

    def test_account_badge_accumulation(self, soul_system):
        """Test badges accumulate across characters."""
        # First character earns veteran badge
        soul_system.create_lost_soul("Hero1", 10, 5, "Died", 3600.0, 50, 4)
        assert len(soul_system.account_badges) == 1

        # Second character earns different badges
        soul_system.create_lost_soul("Hero2", 5, 10, "Died", 3600.0, 100, 9)
        # Should have veteran (from first) + deep_delver + monster_slayer
        assert len(soul_system.account_badges) == 3

    def test_no_duplicate_badges(self, soul_system):
        """Test badges aren't duplicated in account collection."""
        # Two characters earning same badge
        soul_system.create_lost_soul("Hero1", 10, 5, "Died", 3600.0, 50, 4)
        soul_system.create_lost_soul("Hero2", 15, 5, "Died", 3600.0, 50, 4)

        # Should only have one veteran_soul badge
        veteran_count = sum(1 for badge in soul_system.account_badges if badge.id == "veteran_soul")
        assert veteran_count == 1

    def test_calculate_badge_bonuses(self, soul_system):
        """Test bonus calculation from badges."""
        # Manually add some badges
        soul_system.account_badges = [
            Achievement("badge1", "Test", "Test", "hp", 10),
            Achievement("badge2", "Test", "Test", "hp", 15),
            Achievement("badge3", "Test", "Test", "attack", 5),
        ]

        bonuses = soul_system.calculate_badge_bonuses()
        assert bonuses["hp"] == 25  # 10 + 15
        assert bonuses["attack"] == 5

    def test_bonus_caps(self, soul_system):
        """Test bonuses are capped at maximum values."""
        # Add badges that exceed caps
        soul_system.account_badges = [
            Achievement("badge1", "Test", "Test", "hp", 30),
            Achievement("badge2", "Test", "Test", "hp", 30),  # Total 60, cap is 50
            Achievement("badge3", "Test", "Test", "attack", 15),  # Cap is 10
        ]

        bonuses = soul_system.calculate_badge_bonuses()
        assert bonuses["hp"] == 50  # Capped
        assert bonuses["attack"] == 10  # Capped

    def test_transfer_badges(self, soul_system):
        """Test badge transfer to new character."""
        # Set up some account badges
        soul_system.account_badges = [
            Achievement("badge1", "Test", "Test", "hp", 20),
            Achievement("badge2", "Test", "Test", "stamina", 10),
        ]

        bonuses = soul_system.transfer_badges("OldHero", "NewHero")
        assert bonuses["hp"] == 20
        assert bonuses["stamina"] == 10

    def test_memorial_text_empty(self, soul_system):
        """Test memorial text when no souls exist."""
        text = soul_system.get_soul_memorial_text()
        assert len(text) == 1
        assert "No souls" in text[0]

    def test_memorial_text_with_souls(self, soul_system):
        """Test memorial text displays recent souls."""
        # Add some souls
        for i in range(7):
            soul_system.create_lost_soul(
                f"Hero{i}", 10 + i, 5 + i, f"Died to monster {i}", 3600.0, 50, 4
            )

        text = soul_system.get_soul_memorial_text()

        # Should show header
        assert "Lost Soul Memorial" in text[0]

        # Should show last 5 souls
        assert "Hero2" in "\n".join(text)  # Oldest shown
        assert "Hero6" in "\n".join(text)  # Newest
        assert "Hero1" not in "\n".join(text)  # Too old

        # Should show death info
        assert "Level" in "\n".join(text)
        assert "Floor" in "\n".join(text)
