"""Full demo of the map widget with all features."""

if __name__ == "__main__":
    import os
    import sys
    
    # Add parent directory to path so imports work
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    from client.main_window import MainWindow
    from src.models.floor import Floor
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create main window
    window = MainWindow()
    
    # Create a more interesting floor with a specific seed
    floor = Floor(seed=12345)
    floor.generate()
    
    # Set the floor and player position
    window.set_floor(floor)
    window.set_player_position(10, 10)
    
    if window.map_widget:
        # Show valid moves around the player
        window.map_widget.set_valid_moves([
            (9, 10), (11, 10), (10, 9), (10, 11),
            (9, 9), (11, 11), (9, 11), (11, 9)
        ])
        
        # Add some combat flashes
        window.map_widget.flash_tile(15, 15, "combat")
        window.map_widget.flash_tile(5, 5, "combat")
        
        # Clear flashes after 3 seconds
        QTimer.singleShot(3000, lambda: window.map_widget.clear_flash(15, 15))
        QTimer.singleShot(3000, lambda: window.map_widget.clear_flash(5, 5))
        
        # Start with minimap visible
        window.map_widget.toggle_minimap()
    
    # Show window
    window.show()
    
    # Print instructions
    print("\n" + "="*50)
    print("Ascendant: Map Widget Demo")
    print("="*50)
    print("\nKEYBOARD CONTROLS:")
    print("  Ctrl++     : Zoom in")
    print("  Ctrl+-     : Zoom out") 
    print("  Ctrl+0     : Reset zoom")
    print("  M          : Toggle minimap")
    print("  Ctrl+Q     : Quit")
    print("\nMOUSE CONTROLS:")
    print("  Wheel      : Zoom in/out")
    print("  Hover      : Highlight tiles")
    print("\nVISUAL ELEMENTS:")
    print("  Green ●    : Player position")
    print("  Blue tiles : Valid move locations")
    print("  Yellow □   : Flashing combat tiles")
    print("  Gray ■     : Walls")
    print("  Dark ■     : Floor tiles")
    print("\nMINIMAP (top-right when visible):")
    print("  Shows entire floor layout")
    print("  Yellow box shows current view")
    print("  Green dot shows player location")
    print("="*50)
    
    # Run application
    sys.exit(app.exec())