"""Ascendant: The Eternal Spire - Main entry point for the game."""

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
    """Main entry point for the game."""
    print(f"Ascendant: The Eternal Spire v{__version__}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
