"""Integrated client showcasing all implemented features with correct imports."""

if __name__ == "__main__":
    import os
    import sys
    
    # Add parent directory to path so imports work
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from PyQt6.QtWidgets import QApplication, QLabel
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QKeyEvent
    
    from client.main_window import MainWindow
    from src.models.floor import Floor
    from src.models.character import Character
    from src.models.tile import Tile
    from src.enums import TileType, Direction, ActionType
    from src.game import movement
    from src.game import stamina_system
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    
    # Create game components
    floor = Floor(seed=12345)
    floor.generate()
    
    # Find a valid starting position
    start_x, start_y = 10, 10
    for y in range(floor.height):
        for x in range(floor.width):
            tile = floor.get_tile(x, y)
            if tile and tile.tile_type == TileType.FLOOR:
                start_x, start_y = x, y
                break
        else:
            continue
        break
    
    # Create character
    character = Character(name="Hero", x=start_x, y=start_y)
    
    # Add health attributes that Character class doesn't have by default
    character.current_hp = 100
    character.max_hp = 100
    character.level = 1
    
    # Create state tracking
    class GameState:
        def __init__(self):
            self.character = character
            self.floor = floor
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self.update_game)
            self.update_timer.start(100)  # Update every 100ms
            
        def update_game(self):
            # Regenerate stamina
            stamina_system.regenerate_stamina(self.character, 1)
            
            # Update UI
            self.update_ui()
            
        def move_character(self, dx: int, dy: int):
            # Calculate new position
            new_x = self.character.x + dx
            new_y = self.character.y + dy
            new_pos = (new_x, new_y)
            
            # Check if move is valid
            if movement.validate_position(new_pos, self.floor):
                tile = self.floor.get_tile(new_x, new_y)
                if tile and tile.tile_type == TileType.FLOOR:
                    # Check stamina cost
                    cost = stamina_system.get_action_cost(ActionType.MOVE)
                    if stamina_system.use_stamina(self.character, cost):
                        # Perform move
                        old_x, old_y = self.character.x, self.character.y
                        self.character.move_to(new_pos)
                        
                        # Update map display
                        if window.map_widget:
                            window.map_widget.set_player_position(self.character.x, self.character.y)
                            
                            # Flash the old position briefly
                            window.map_widget.flash_tile(old_x, old_y, "move")
                            QTimer.singleShot(200, lambda: window.map_widget.clear_flash(old_x, old_y))
                            
                            # Show valid moves from new position
                            self.update_valid_moves()
                    else:
                        print("Not enough stamina!")
                        if window.map_widget:
                            window.map_widget.flash_tile(new_x, new_y, "blocked")
                            QTimer.singleShot(500, lambda: window.map_widget.clear_flash(new_x, new_y))
                        
        def update_valid_moves(self):
            if window.map_widget:
                valid_moves = []
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), 
                               (1, 1), (1, -1), (-1, 1), (-1, -1)]:
                    new_x = self.character.x + dx
                    new_y = self.character.y + dy
                    new_pos = (new_x, new_y)
                    
                    if movement.validate_position(new_pos, self.floor):
                        tile = self.floor.get_tile(new_x, new_y)
                        if tile and tile.tile_type == TileType.FLOOR:
                            valid_moves.append((new_x, new_y))
                            
                window.map_widget.set_valid_moves(valid_moves)
                
        def update_ui(self):
            # Update status bar with character info
            if window.statusBar():
                status_text = (
                    f"Position: ({self.character.x}, {self.character.y}) | "
                    f"HP: {self.character.current_hp}/{self.character.max_hp} | "
                    f"Stamina: {self.character.stamina}/{self.character.stamina_max} | "
                    f"Level: {self.character.level}"
                )
                window.statusBar().showMessage(status_text)
                
            # Update left panel with character stats
            if hasattr(window, 'left_panel') and window.left_panel.layout():
                # Clear existing widgets
                while window.left_panel.layout().count():
                    item = window.left_panel.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                        
                # Add character info
                info_label = QLabel(
                    f"<h3>Character</h3>"
                    f"<p><b>Name:</b> {self.character.name}</p>"
                    f"<p><b>Level:</b> {self.character.level}</p>"
                    f"<p><b>HP:</b> {self.character.current_hp}/{self.character.max_hp}</p>"
                    f"<p><b>Stamina:</b> {self.character.stamina}/{self.character.stamina_max}</p>"
                    f"<p><b>Position:</b> ({self.character.x}, {self.character.y})</p>"
                    f"<hr>"
                    f"<h3>Controls</h3>"
                    f"<p><b>Movement:</b> WASD or Arrows</p>"
                    f"<p><b>Diagonals:</b> Q/E/Z/C</p>"
                    f"<p><b>Zoom:</b> Mouse wheel</p>"
                    f"<p><b>Minimap:</b> M</p>"
                )
                info_label.setStyleSheet("QLabel { color: #ffffff; padding: 10px; }")
                info_label.setWordWrap(True)
                info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
                window.left_panel.layout().addWidget(info_label)
    
    # Create game state
    game_state = GameState()
    
    # Create keyboard handler
    def handle_key(event: QKeyEvent):
        key = event.key()
        
        # Movement keys
        if key == Qt.Key.Key_W or key == Qt.Key.Key_Up:
            game_state.move_character(0, -1)
        elif key == Qt.Key.Key_S or key == Qt.Key.Key_Down:
            game_state.move_character(0, 1)
        elif key == Qt.Key.Key_A or key == Qt.Key.Key_Left:
            game_state.move_character(-1, 0)
        elif key == Qt.Key.Key_D or key == Qt.Key.Key_Right:
            game_state.move_character(1, 0)
        # Diagonal movement
        elif key == Qt.Key.Key_Q:
            game_state.move_character(-1, -1)
        elif key == Qt.Key.Key_E:
            game_state.move_character(1, -1)
        elif key == Qt.Key.Key_Z:
            game_state.move_character(-1, 1)
        elif key == Qt.Key.Key_C:
            game_state.move_character(1, 1)
        # Other keys
        elif key == Qt.Key.Key_M:
            if window.map_widget:
                window.map_widget.toggle_minimap()
    
    # Set keyboard handler
    window.set_keyboard_handler(handle_key)
    
    # Initialize map display
    window.set_floor(floor)
    window.set_player_position(character.x, character.y)
    
    # Show initial valid moves
    game_state.update_valid_moves()
    
    # Enable minimap by default
    if window.map_widget:
        window.map_widget.show_minimap = True
    
    # Initial UI update
    game_state.update_ui()
    
    # Show window
    window.show()
    
    # Print instructions
    print("\n" + "="*60)
    print("ASCENDANT: Integrated Feature Test")
    print("="*60)
    print("\nThis client demonstrates all implemented features:")
    print("\n1. MAP DISPLAY (Phase 3.2)")
    print("   - Tile-based rendering with proper colors")
    print("   - Player position (green circle)")
    print("   - Zoom functionality (mouse wheel)")
    print("   - Minimap overlay (M key)")
    print("\n2. MOVEMENT SYSTEM (Phase 2.1)")
    print("   - WASD or Arrow keys for movement")
    print("   - Q/E/Z/C for diagonal movement")
    print("   - Valid move highlighting (blue tiles)")
    print("   - Collision detection with walls")
    print("\n3. STAMINA SYSTEM (Phase 2.2)")
    print("   - Movement costs stamina (10 per move)")
    print("   - Stamina regenerates over time")
    print("   - Movement blocked when stamina depleted")
    print("   - Red flash when blocked")
    print("\n4. CHARACTER SYSTEM")
    print("   - Character stats in left panel")
    print("   - Real-time status updates")
    print("   - Position tracking")
    print("\n5. FLOOR GENERATION")
    print("   - Procedurally generated dungeons")
    print("   - Room and corridor system")
    print("   - Proper wall collision")
    print("="*60)
    print("\nWatch your stamina as you move!")
    print("Movement flash = successful move")
    print("Red flash = blocked (no stamina or wall)")
    print("="*60)
    
    # Run application
    sys.exit(app.exec())