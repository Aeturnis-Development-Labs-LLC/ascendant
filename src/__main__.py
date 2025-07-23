"""Ascendant: The Eternal Spire - Game Client entry point."""

try:
    from . import __version__
except ImportError:
    # Handle direct execution
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    from __init__ import __version__ as version

    __version__ = version


def main():
    """Run the main entry point for the game."""
    import sys

    # Check if running in GUI mode
    if "--gui" in sys.argv or len(sys.argv) == 1:
        # Import here to avoid requiring PyQt6 for non-GUI usage
        try:
            from client.app import main as gui_main

            return gui_main()
        except ImportError:
            print("PyQt6 not installed. Please install with: pip install PyQt6")
            return 1
    else:
        # Console mode
        print(f"Ascendant: The Eternal Spire (Client) v{__version__}")
        return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
