"""Interactive test script for map widget features."""

if __name__ == "__main__":
    import os
    import sys
    
    # Add parent directory to path so imports work
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
    from PyQt6.QtCore import QTimer
    
    from client.main_window import MainWindow
    from src.models.floor import Floor
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    
    # Create a test floor with specific seed for consistency
    floor = Floor(seed=12345)
    floor.generate()
    
    # Set the floor and initial player position
    window.set_floor(floor)
    window.set_player_position(10, 10)
    
    # Add some visual feedback examples
    if window.map_widget:
        # Set some valid moves to show blue highlighting
        window.map_widget.set_valid_moves([(9, 10), (11, 10), (10, 9), (10, 11)])
        
        # Flash a tile for combat effect
        window.map_widget.flash_tile(12, 12, "combat")
        
        # Clear flash after 2 seconds
        QTimer.singleShot(2000, lambda: window.map_widget.clear_flash(12, 12))
    
    # Show window
    window.show()
    
    # Print instructions
    print("Interactive Map Widget Test")
    print("==========================")
    print("Controls:")
    print("- Mouse wheel: Zoom in/out")
    print("- Ctrl++: Zoom in (menu)")
    print("- Ctrl+-: Zoom out (menu)")
    print("- Ctrl+0: Reset zoom")
    print("- M: Toggle mini-map")
    print("- Mouse hover: Highlight tiles")
    print("\nFeatures to observe:")
    print("- Blue tiles: Valid moves (around player)")
    print("- Yellow flash: Combat effect (at position 12,12)")
    print("- Green circle: Player position")
    print("- Mini-map: Shows full floor overview (press M)")
    
    # Run application
    sys.exit(app.exec())