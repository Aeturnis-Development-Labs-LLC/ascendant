"""Manual test script to visually verify the map widget."""

if __name__ == "__main__":
    import os
    import sys

    # Add parent directory to path so imports work
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa: E501

    from PyQt6.QtWidgets import QApplication

    from client.main_window import MainWindow
    from src.models.floor import Floor

    # Create application
    app = QApplication(sys.argv)

    # Create main window
    window = MainWindow()

    # Create a test floor
    floor = Floor(seed=42)
    floor.generate()

    # Set the floor and player position
    window.set_floor(floor)
    window.set_player_position(10, 10)

    # Show window
    window.show()

    # Run application
    sys.exit(app.exec())
