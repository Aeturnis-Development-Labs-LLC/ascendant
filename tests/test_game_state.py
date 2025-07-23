"""Tests for game state management."""

import pytest

from src.game.game_state import GameState, GameStateManager


class TestGameState:
    """Tests for GameState dataclass."""

    def test_game_state_initialization(self):
        """Test GameState initializes with correct defaults."""
        state = GameState()
        
        assert state.character is None
        assert state.current_floor is None
        assert state.monsters == []
        assert state.combat_log is None
        # UI update flags default to False
        assert state.ui_needs_update["character"] is False
        assert state.ui_needs_update["map"] is False
        assert state.ui_needs_update["combat_log"] is False
        assert state.ui_needs_update["floor_info"] is False

    def test_mark_dirty(self):
        """Test marking UI components as dirty."""
        state = GameState()
        
        # Clear all flags
        for key in state.ui_needs_update:
            state.ui_needs_update[key] = False
        
        # Mark character dirty
        state.mark_dirty("character")
        assert state.ui_needs_update["character"] is True
        assert state.ui_needs_update["map"] is False
        
    def test_mark_all_dirty(self):
        """Test marking all UI components as dirty."""
        state = GameState()
        
        # Clear all flags
        for key in state.ui_needs_update:
            state.ui_needs_update[key] = False
            
        # Mark all dirty
        state.mark_all_dirty()
        
        # All should be True
        for value in state.ui_needs_update.values():
            assert value is True


class TestGameStateManager:
    """Tests for GameStateManager."""

    def test_manager_initialization(self):
        """Test GameStateManager initializes correctly."""
        manager = GameStateManager()
        
        assert isinstance(manager.state, GameState)
        assert manager.main_window is None
        
    def test_new_game(self):
        """Test starting a new game."""
        manager = GameStateManager()
        manager.new_game("TestHero")
        
        # Character should be created
        assert manager.state.character is not None
        assert manager.state.character.name == "TestHero"
        assert manager.state.character.x == 10
        assert manager.state.character.y == 10
        
        # Floor should be generated
        assert manager.state.current_floor is not None
        assert manager.state.current_floor.level == 1
        assert manager.state.current_floor.width == 50
        assert manager.state.current_floor.height == 50
        
        # Combat log should exist
        assert manager.state.combat_log is not None
        
        # UI should be marked dirty
        for value in manager.state.ui_needs_update.values():
            assert value is True
            
    def test_update_ui_without_window(self):
        """Test update_ui does nothing without window."""
        manager = GameStateManager()
        manager.new_game()
        
        # Should not raise any errors
        manager.update_ui()
        
    def test_movement_functions(self):
        """Test movement helper functions."""
        manager = GameStateManager()
        manager.new_game()
        
        # Get initial position
        start_x = manager.state.character.x
        start_y = manager.state.character.y
        
        # Try to move (may or may not succeed depending on floor layout)
        manager.move_character(0, -1)  # Try to move north
        
        # UI should be marked dirty regardless
        assert manager.state.ui_needs_update["character"] is True
        assert manager.state.ui_needs_update["map"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])