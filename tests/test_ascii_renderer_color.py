"""Tests for ASCII renderer color support - UTF Contract GAME-COLOR-001."""

from unittest.mock import patch

from src.renderers.ascii_renderer import ASCIIRenderer
from src.models.floor import Floor
from src.models.character import Character
from src.enums import EntityType
from src.rendering.color_scheme import ColorScheme, ColorMode
from src.rendering.accessibility import AccessibilityConfig, ColorblindMode


class TestASCIIRendererColor:
    """Test color support in ASCII renderer."""

    def test_renderer_accepts_color_enabled_flag(self):
        """Test renderer can be initialized with color flag."""
        renderer = ASCIIRenderer(color_enabled=True)
        assert renderer.color_enabled is True

        renderer = ASCIIRenderer(color_enabled=False)
        assert renderer.color_enabled is False

    def test_renderer_defaults_to_no_color(self):
        """Test renderer defaults to no color for compatibility."""
        renderer = ASCIIRenderer()
        assert hasattr(renderer, "color_enabled")
        assert renderer.color_enabled is False

    def test_render_with_colors_includes_ansi_codes(self):
        """Test colored output includes ANSI codes."""
        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)  # Center of 20x20 floor

        renderer = ASCIIRenderer(color_enabled=True)
        output = renderer.render(floor, character)

        # Should contain ANSI escape codes
        assert "\033[" in output

    def test_render_without_colors_no_ansi_codes(self):
        """Test non-colored output has no ANSI codes."""
        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)

        renderer = ASCIIRenderer(color_enabled=False)
        output = renderer.render(floor, character)

        # Should not contain ANSI escape codes
        assert "\033[" not in output

    def test_color_scheme_integration(self):
        """Test renderer uses ColorScheme for colors."""
        floor = Floor(seed=1)
        floor.generate()
        Character("Player", 10, 10)

        renderer = ASCIIRenderer(color_enabled=True)

        # Renderer should have a color scheme
        assert hasattr(renderer, "color_scheme")
        assert isinstance(renderer.color_scheme, ColorScheme)

    def test_custom_color_scheme(self):
        """Test renderer accepts custom color scheme."""
        custom_scheme = ColorScheme()
        renderer = ASCIIRenderer(color_enabled=True, color_scheme=custom_scheme)

        assert renderer.color_scheme is custom_scheme

    def test_fog_of_war_affects_colors(self):
        """Test fog of war dims colors."""
        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)

        renderer = ASCIIRenderer(color_enabled=True, fog_radius=3)

        with patch.object(
            renderer, "_apply_color", side_effect=lambda char, color: char
        ) as mock_apply:
            renderer.render(floor, character)

            # Should have called color application with different visibility levels
            assert mock_apply.called
            # Check that it was called with dimmed colors for distant tiles
            call_args = [call[0][1] for call in mock_apply.call_args_list]
            # Some colors should be dimmer than others
            assert any(sum(color) < 500 for color in call_args)  # Some dim colors

    def test_console_vs_gui_color_modes(self):
        """Test renderer supports different color modes."""
        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)

        # Console mode (ANSI)
        renderer = ASCIIRenderer(color_enabled=True, color_mode=ColorMode.ANSI)
        output = renderer.render(floor, character)
        assert "\033[" in output  # ANSI codes

        # GUI mode would return RGB tuples - test the method exists
        renderer = ASCIIRenderer(color_enabled=True, color_mode=ColorMode.RGB)
        assert hasattr(renderer, "get_tile_color_rgb")

    def test_entity_colors_override_tile_colors(self):
        """Test entities are colored differently than tiles."""
        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)

        # Place a monster
        from src.models.entity import Entity

        class Monster(Entity):
            @property
            def entity_type(self) -> EntityType:
                return EntityType.MONSTER

            def update(self) -> None:
                pass

            def render(self) -> str:
                return "M"

        monster = Monster("Monster", 15, 15)
        floor.get_tile(15, 15).occupant = monster

        renderer = ASCIIRenderer(color_enabled=True)

        # Both character and monster should have distinct colors
        assert renderer.get_entity_color(character) != renderer.get_entity_color(monster)

    def test_accessibility_config_integration(self):
        """Test renderer respects accessibility configuration."""
        floor = Floor(seed=1)
        floor.generate()
        Character("Player", 10, 10)

        # Create accessibility config
        config = AccessibilityConfig(
            colorblind_mode=ColorblindMode.DEUTERANOPIA,
            high_contrast_mode=True,
            symbol_only_mode=False,
        )

        renderer = ASCIIRenderer(color_enabled=True, accessibility_config=config)

        assert renderer.accessibility_config is config

    def test_symbol_only_mode_disables_colors(self):
        """Test symbol-only mode overrides color settings."""
        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)

        config = AccessibilityConfig(symbol_only_mode=True)
        renderer = ASCIIRenderer(
            color_enabled=True, accessibility_config=config  # Should be overridden
        )

        output = renderer.render(floor, character)

        # Should not have color codes despite color_enabled=True
        assert "\033[" not in output

    def test_status_effect_colors(self):
        """Test characters with status effects have colored representation."""
        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)

        # Mock a status effect - Character doesn't have status_effects yet
        from src.rendering.color_effects import StatusEffect

        # Create a mock character with status effects
        character.status_effects = [StatusEffect.POISON]

        ASCIIRenderer(color_enabled=True)

        # Test with a non-green base color to see the effect
        test_color = (128, 128, 128)  # Gray

        # Manually apply status effect to verify it works
        from src.rendering.color_effects import apply_status_effect

        poisoned_color = apply_status_effect(test_color, StatusEffect.POISON)

        assert test_color != poisoned_color
        assert poisoned_color[1] > poisoned_color[0]  # Green > Red for poison
        assert poisoned_color[1] > test_color[1]  # More green than original

    def test_damage_flash_animation(self):
        """Test damage flash returns multiple frames."""
        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)

        renderer = ASCIIRenderer(color_enabled=True)

        # Simulate damage flash
        from src.rendering.color_effects import DamageType

        frames = renderer.render_damage_flash(floor, character, DamageType.PHYSICAL)

        assert isinstance(frames, list)
        assert len(frames) > 1
        assert all(isinstance(frame, str) for frame in frames)

    def test_color_reset_at_line_end(self):
        """Test color reset codes are added at line ends."""
        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)

        renderer = ASCIIRenderer(color_enabled=True)
        output = renderer.render(floor, character)

        # Each line should end with reset code
        lines = output.strip().split("\n")
        reset_code = "\033[0m"

        for line in lines:
            if "\033[" in line:  # If line has color
                assert line.endswith(reset_code)

    def test_performance_with_colors(self):
        """Test rendering performance with colors is acceptable."""
        import time

        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)

        renderer = ASCIIRenderer(color_enabled=True, fog_radius=10)

        start = time.time()
        for _ in range(100):
            renderer.render(floor, character)
        elapsed = time.time() - start

        # Should still be fast even with colors
        assert elapsed < 1.0  # 100 renders in under 1 second

    def test_color_legend_generation(self):
        """Test renderer can generate a color legend."""
        renderer = ASCIIRenderer(color_enabled=True)

        legend = renderer.generate_color_legend()

        assert isinstance(legend, str)
        assert "WALL" in legend
        assert "FLOOR" in legend
        assert "PLAYER" in legend

    def test_terrain_colors_in_world_map(self):
        """Test world map renderer uses appropriate terrain colors."""
        # This would test world map specific coloring
        # For now, just verify the basic renderer works with colors
        floor = Floor(seed=1)
        floor.generate()
        character = Character("Player", 10, 10)

        renderer = ASCIIRenderer(color_enabled=True)
        output = renderer.render(floor, character)

        # Should have colors
        assert "\033[" in output  # Has colors
