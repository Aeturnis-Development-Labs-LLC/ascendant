"""Additional tests to improve overall coverage."""

import pytest

from src.enums import ActionType, EntityType, TileType
from src.game.stamina_system import regenerate_stamina, get_action_cost
from src.game.loot_system import LootSystem
from src.models.character import Character
from src.models.entity import Entity
from src.models.tile import Tile


class TestStaminaCoverage:
    """Tests to improve stamina system coverage."""
    
    def test_regenerate_stamina_default(self):
        """Test stamina regeneration with default amount."""
        char = Character("Hero", 5, 5)
        char.stamina = 50
        char.stamina_max = 100
        
        regenerate_stamina(char)  # Default 5 points
        assert char.stamina == 55
        
    def test_get_action_cost_unknown(self):
        """Test getting cost for unknown action."""
        # Create a mock action that's not in the cost map
        cost = get_action_cost(None)  # type: ignore
        assert cost == 0
        

class TestEntityCoverage:
    """Tests to improve entity coverage."""
    
    def test_entity_str_repr(self):
        """Test entity string representations."""
        # Use Character since Entity is abstract
        char = Character("Test", 5, 5)
        
        str_repr = str(char)
        assert "Character" in str_repr
        assert "5, 5" in str_repr
        
        repr_str = repr(char)
        assert "Character" in repr_str
        assert "name='Test'" in repr_str
        

class TestTileCoverage:
    """Tests to improve tile coverage."""
    
    def test_tile_str_repr(self):
        """Test tile string representations."""
        tile = Tile(10, 20, TileType.FLOOR)
        
        str_repr = str(tile)
        assert "Tile(10, 20)" in str_repr
        
        repr_str = repr(tile)
        assert "Tile" in repr_str
        assert "type=" in repr_str
        assert "FLOOR" in repr_str
        
        
class TestCharacterCoverage:
    """Tests to improve character coverage."""
    
    def test_character_str_repr(self):
        """Test character string representations."""
        char = Character("Hero", 5, 10)
        
        str_repr = str(char)
        assert "Character(5, 10)" in str_repr
        
        repr_str = repr(char)
        assert "Character" in repr_str
        assert "name='Hero'" in repr_str
        
    def test_character_apply_status(self):
        """Test applying status effects."""
        char = Character("Hero", 5, 5)
        
        char.apply_status("Poisoned", 5)
        assert char.status_effects["Poisoned"] == 5
        
        
class TestLootSystemCoverage:
    """Tests to improve loot system coverage."""
    
    def test_loot_system_initialization(self):
        """Test loot system initialization."""
        loot_system = LootSystem(seed=42)
        assert loot_system._rng is not None
        
        # Test with no seed
        loot_system2 = LootSystem()
        assert loot_system2._rng is not None


class TestMainModule:
    """Tests for __main__ module."""
    
    def test_main_imports(self):
        """Test that main module can be imported."""
        try:
            import src.__main__
            assert hasattr(src.__main__, 'main')
        except SystemExit:
            # Main might exit, that's okay
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])