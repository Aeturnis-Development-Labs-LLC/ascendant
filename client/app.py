"""Entry point for the Ascendant PyQt6 client application."""

import sys

from PyQt6.QtWidgets import QApplication

from client.main_window import MainWindow


def main():
    """Initialize and run the PyQt6 application."""
    # Create QApplication instance
    app = QApplication(sys.argv)
    app.setApplicationName("Ascendant")
    app.setOrganizationName("Aeturnis Development Labs LLC")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run the application event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
