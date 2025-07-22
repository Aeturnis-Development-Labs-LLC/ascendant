"""Tests for color effects system - UTF Contract GAME-COLOR-002."""

from src.rendering.color_effects import (
    apply_fog_of_war,
    apply_status_effect,
    flash_damage,
    brightness_adjust,
    StatusEffect,
    DamageType,
)


class TestColorEffects:
    """Test color effect functions."""

    def test_apply_fog_of_war_full_visibility(self):
        """Test fog of war with full visibility."""
        color = (255, 128, 64)
        result = apply_fog_of_war(color, visibility=1.0)

        # Full visibility should not change color
        assert result == color

    def test_apply_fog_of_war_no_visibility(self):
        """Test fog of war with no visibility."""
        color = (255, 128, 64)
        result = apply_fog_of_war(color, visibility=0.0)

        # No visibility should make very dark
        assert all(c < 50 for c in result)
        assert result[0] < color[0]
        assert result[1] < color[1]
        assert result[2] < color[2]

    def test_apply_fog_of_war_partial_visibility(self):
        """Test fog of war with partial visibility."""
        color = (200, 100, 50)
        result = apply_fog_of_war(color, visibility=0.5)

        # Should be darker but not black
        assert result[0] < color[0]
        assert result[1] < color[1]
        assert result[2] < color[2]
        assert all(c > 0 for c in result)

    def test_apply_fog_of_war_bounds(self):
        """Test fog of war respects RGB bounds."""
        color = (255, 255, 255)

        # Test various visibility levels
        for visibility in [0.0, 0.25, 0.5, 0.75, 1.0]:
            result = apply_fog_of_war(color, visibility)
            assert all(0 <= c <= 255 for c in result)

    def test_apply_status_effect_poison(self):
        """Test poison status effect (green tint)."""
        color = (128, 128, 128)
        result = apply_status_effect(color, StatusEffect.POISON)

        # Should have green tint (higher green component)
        assert result[1] > result[0]  # Green > Red
        assert result[1] > result[2]  # Green > Blue

    def test_apply_status_effect_burning(self):
        """Test burning status effect (red/orange tint)."""
        color = (128, 128, 128)
        result = apply_status_effect(color, StatusEffect.BURNING)

        # Should have red/orange tint
        assert result[0] > result[1]  # Red > Green
        assert result[0] > result[2]  # Red > Blue

    def test_apply_status_effect_frozen(self):
        """Test frozen status effect (blue tint)."""
        color = (128, 128, 128)
        result = apply_status_effect(color, StatusEffect.FROZEN)

        # Should have blue tint
        assert result[2] > result[0]  # Blue > Red
        assert result[2] > result[1]  # Blue > Green

    def test_apply_status_effect_confused(self):
        """Test confused status effect (purple tint)."""
        color = (128, 128, 128)
        result = apply_status_effect(color, StatusEffect.CONFUSED)

        # Should have purple tint (red and blue)
        assert result[0] > result[1]  # Red > Green
        assert result[2] > result[1]  # Blue > Green

    def test_apply_status_effect_blessed(self):
        """Test blessed status effect (golden/yellow tint)."""
        color = (128, 128, 128)
        result = apply_status_effect(color, StatusEffect.BLESSED)

        # Should have golden tint (high red and green)
        assert result[0] > color[0]  # Brighter red
        assert result[1] > color[1]  # Brighter green
        assert result[0] > result[2]  # Red > Blue
        assert result[1] > result[2]  # Green > Blue

    def test_status_effect_bounds(self):
        """Test status effects respect RGB bounds."""
        color = (200, 200, 200)

        for effect in StatusEffect:
            result = apply_status_effect(color, effect)
            assert all(0 <= c <= 255 for c in result)

    def test_flash_damage_physical(self):
        """Test damage flash for physical damage."""
        color = (128, 128, 128)

        # Flash should return sequence of colors
        frames = flash_damage(color, DamageType.PHYSICAL)
        assert isinstance(frames, list)
        assert len(frames) >= 2  # At least flash and return

        # Should flash white for physical
        flash_color = frames[0]
        assert all(c > 200 for c in flash_color)

        # Should return to original
        assert frames[-1] == color

    def test_flash_damage_fire(self):
        """Test damage flash for fire damage."""
        color = (128, 128, 128)
        frames = flash_damage(color, DamageType.FIRE)

        # Should flash red/orange
        flash_color = frames[0]
        assert flash_color[0] > flash_color[1]  # Red > Green
        assert flash_color[0] > flash_color[2]  # Red > Blue

    def test_flash_damage_ice(self):
        """Test damage flash for ice damage."""
        color = (128, 128, 128)
        frames = flash_damage(color, DamageType.ICE)

        # Should flash blue/white
        flash_color = frames[0]
        assert flash_color[2] >= flash_color[0]  # Blue >= Red
        assert flash_color[2] >= flash_color[1]  # Blue >= Green

    def test_flash_damage_poison(self):
        """Test damage flash for poison damage."""
        color = (128, 128, 128)
        frames = flash_damage(color, DamageType.POISON)

        # Should flash green
        flash_color = frames[0]
        assert flash_color[1] > flash_color[0]  # Green > Red
        assert flash_color[1] > flash_color[2]  # Green > Blue

    def test_brightness_adjust_increase(self):
        """Test brightness increase."""
        color = (100, 100, 100)
        result = brightness_adjust(color, 50)  # 50% brighter

        assert result[0] > color[0]
        assert result[1] > color[1]
        assert result[2] > color[2]
        assert all(c <= 255 for c in result)

    def test_brightness_adjust_decrease(self):
        """Test brightness decrease."""
        color = (200, 200, 200)
        result = brightness_adjust(color, -50)  # 50% darker

        assert result[0] < color[0]
        assert result[1] < color[1]
        assert result[2] < color[2]
        assert all(c >= 0 for c in result)

    def test_brightness_adjust_bounds(self):
        """Test brightness adjustment respects bounds."""
        # Test extreme cases
        white = (255, 255, 255)
        black = (0, 0, 0)

        # Can't get brighter than white
        result = brightness_adjust(white, 100)
        assert result == white

        # Can't get darker than black
        result = brightness_adjust(black, -100)
        assert result == black

    def test_brightness_adjust_proportional(self):
        """Test brightness maintains color ratios."""
        color = (200, 100, 50)
        result = brightness_adjust(color, 20)

        # Ratios should be maintained
        orig_ratio_rg = color[0] / color[1]
        new_ratio_rg = result[0] / result[1]
        assert abs(orig_ratio_rg - new_ratio_rg) < 0.1

    def test_combined_effects(self):
        """Test combining multiple effects."""
        color = (128, 128, 128)

        # Apply fog then status
        fogged = apply_fog_of_war(color, 0.5)
        poisoned = apply_status_effect(fogged, StatusEffect.POISON)

        # Should be both darker and green-tinted
        assert all(c < color[i] for i, c in enumerate(poisoned))
        assert poisoned[1] > poisoned[0]  # Green tint

    def test_effect_consistency(self):
        """Test effects are deterministic."""
        color = (150, 150, 150)

        # Same input should give same output
        result1 = apply_status_effect(color, StatusEffect.BURNING)
        result2 = apply_status_effect(color, StatusEffect.BURNING)

        assert result1 == result2

    def test_flash_damage_frame_count(self):
        """Test damage flash has appropriate frame count."""
        color = (128, 128, 128)

        for damage_type in DamageType:
            frames = flash_damage(color, damage_type)
            assert 2 <= len(frames) <= 6  # Reasonable animation length
