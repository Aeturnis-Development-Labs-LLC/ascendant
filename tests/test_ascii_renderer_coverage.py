"""Additional tests for ASCII renderer to improve coverage."""

import pytest

from src.enums import EntityType, TileType
from src.models.character import Character
from src.models.floor import Floor
from src.models.monster import Monster, AIBehavior, MonsterType
from src.renderers.ascii_renderer import ASCIIRenderer


class TestASCIIRendererCoverage:
    """Tests to improve ASCII renderer coverage."""

    def test_renderer_with_color_enabled(self):
        """Test renderer with colors enabled."""
        floor = Floor(seed=42)
        floor.generate()
        
        renderer = ASCIIRenderer(color_enabled=True, fog_radius=5)
        output = renderer.render(floor, player_pos=(10, 10))
        
        # Should have ANSI color codes
        assert "\033[" in output
        
    def test_renderer_with_high_contrast(self):
        """Test renderer with high contrast mode."""
        floor = Floor(seed=42)
        floor.generate()
        
        renderer = ASCIIRenderer(
            color_enabled=True, 
            fog_radius=5,
            high_contrast=True
        )
        output = renderer.render(floor, player_pos=(10, 10))
        
        assert isinstance(output, str)
        assert len(output) > 0
        
    def test_renderer_with_colorblind_modes(self):
        """Test renderer with different colorblind modes."""
        floor = Floor(seed=42)
        floor.generate()
        
        modes = ["deuteranopia", "protanopia", "tritanopia"]
        
        for mode in modes:
            renderer = ASCIIRenderer(
                color_enabled=True,
                fog_radius=5,
                colorblind_mode=mode
            )
            output = renderer.render(floor, player_pos=(10, 10))
            assert isinstance(output, str)
            
    def test_render_with_info(self):
        """Test render_with_info method."""
        floor = Floor(seed=42)
        floor.generate()
        
        renderer = ASCIIRenderer(color_enabled=True)
        output = renderer.render_with_info(floor, player_pos=(10, 10))
        
        # Should contain floor info
        assert "Floor 1" in output
        assert "Size: 50x50" in output
        assert "Rooms:" in output
        assert "Colors: Enabled" in output
        
    def test_render_with_info_colorblind(self):
        """Test render_with_info with colorblind mode."""
        floor = Floor(seed=42) 
        floor.generate()
        
        renderer = ASCIIRenderer(
            color_enabled=True,
            colorblind_mode="deuteranopia",
            high_contrast=True
        )
        output = renderer.render_with_info(floor, player_pos=(10, 10))
        
        assert "Colorblind Mode: deuteranopia" in output
        assert "High Contrast: On" in output
        
    def test_entity_rendering(self):
        """Test rendering with entities."""
        floor = Floor(seed=42)
        floor.generate()
        
        # Add some entities
        floor.entities = [
            Character("Player", 10, 10),
            Monster(12, 10, "Goblin", "G", 10, 10, 5, 2, 
                   MonsterType.GOBLIN, AIBehavior.AGGRESSIVE)
        ]
        
        renderer = ASCIIRenderer(color_enabled=True, fog_radius=10)
        output = renderer.render(floor, player_pos=(10, 10))
        
        assert "@" in output  # Player character
        assert "M" in output  # Monster (generic display)
        
    def test_empty_tile_rendering(self):
        """Test rendering positions without tiles."""
        floor = Floor(seed=42)
        floor.generate()
        
        # Remove a tile to test empty space
        if (5, 5) in floor.tiles:
            del floor.tiles[(5, 5)]
        
        renderer = ASCIIRenderer()
        output = renderer.render(floor, player_pos=(10, 10))
        
        # Should still work without errors
        assert isinstance(output, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])