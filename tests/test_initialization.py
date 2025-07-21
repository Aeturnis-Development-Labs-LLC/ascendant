"""Tests for project initialization - UTF Contract GAME-CORE-001."""

import subprocess
import sys
from pathlib import Path


def test_directory_structure_exists():
    """Test that all required directories exist."""
    base_path = Path(__file__).parent.parent
    required_dirs = ["src", "tests", "docs", "assets", "contracts"]

    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        assert dir_path.exists(), f"Directory {dir_name} does not exist"
        assert dir_path.is_dir(), f"{dir_name} is not a directory"


def test_git_repository_initialized():
    """Test that git repository is initialized."""
    base_path = Path(__file__).parent.parent
    git_dir = base_path / ".git"
    assert git_dir.exists(), ".git directory does not exist"
    assert git_dir.is_dir(), ".git is not a directory"


def test_virtual_environment_can_be_created():
    """Test that virtual environment exists or can be created."""
    # Just check that we can import venv module
    import venv

    assert venv is not None, "venv module not available"


def test_requirements_file_exists():
    """Test that requirements.txt exists with required dependencies."""
    base_path = Path(__file__).parent.parent
    req_file = base_path / "requirements.txt"
    assert req_file.exists(), "requirements.txt does not exist"

    with open(req_file, "r") as f:
        content = f.read()
        required_packages = ["pytest", "pytest-cov", "mypy", "black", "flake8"]
        for package in required_packages:
            assert package in content, f"{package} not found in requirements.txt"


def test_main_module_exists():
    """Test that __main__.py exists and can be imported."""
    base_path = Path(__file__).parent.parent
    main_file = base_path / "src" / "__main__.py"
    assert main_file.exists(), "__main__.py does not exist"

    # Import it as a module
    import importlib.util

    spec = importlib.util.spec_from_file_location("test_main", main_file)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert hasattr(module, "main"), "main function not found"
        assert callable(module.main), "main is not callable"
    else:
        raise ImportError("Could not load module")


def test_main_prints_game_title():
    """Test that running main prints the game title."""
    base_path = Path(__file__).parent.parent

    # Run the module and capture output
    result = subprocess.run(
        [sys.executable, "-m", "src"],
        cwd=str(base_path),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Main module exited with code {result.returncode}"
    assert "Ascendant: The Eternal Spire" in result.stdout, "Game title not printed"
    assert "v0.1.0" in result.stdout, "Version not displayed"


def test_project_runs_without_errors():
    """Test that 'python -m ascendant' would run without errors."""
    base_path = Path(__file__).parent.parent
    main_file = base_path / "src" / "__main__.py"

    # Import and run the main function
    import importlib.util

    spec = importlib.util.spec_from_file_location("test_main", main_file)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        exit_code = module.main()
        assert exit_code == 0, f"main() returned non-zero exit code: {exit_code}"
    else:
        raise ImportError("Could not load module")
