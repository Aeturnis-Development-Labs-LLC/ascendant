#!/usr/bin/env python3
"""Setup development environment for Ascendant: The Eternal Spire."""

import subprocess
import sys


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        subprocess.run(cmd, check=True, shell=True)
        print(f"✓ {description} complete")
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        return False
    return True


def main():
    """Set up the development environment."""
    print("Setting up Ascendant: The Eternal Spire development environment")
    print("=" * 60)

    # Check Python version
    if sys.version_info < (3, 11):
        print("✗ Python 3.11+ is required")
        return 1

    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return 1

    # Install pre-commit hooks
    if not run_command("pre-commit install", "Installing pre-commit hooks"):
        return 1

    # Run pre-commit on all files to check initial state
    print("\nRunning initial code quality checks...")
    run_command("pre-commit run --all-files", "Initial code quality check")

    print("\n" + "=" * 60)
    print("✓ Development environment setup complete!")
    print("\nPre-commit hooks will now run automatically on git commit.")
    print("You can manually run checks with: pre-commit run --all-files")

    return 0


if __name__ == "__main__":
    sys.exit(main())
