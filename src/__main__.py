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
    print(f"Ascendant: The Eternal Spire (Client) v{__version__}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
