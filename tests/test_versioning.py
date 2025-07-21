"""Tests for semantic versioning implementation"""

from pathlib import Path
import re


def test_version_file_exists():
    """Test that VERSION file exists"""
    base_path = Path(__file__).parent.parent
    version_file = base_path / "VERSION"
    assert version_file.exists(), "VERSION file does not exist"


def test_version_format():
    """Test that version follows semantic versioning format"""
    base_path = Path(__file__).parent.parent
    version_file = base_path / "VERSION"

    with open(version_file, "r") as f:
        version = f.read().strip()

    # Semantic versioning regex pattern
    pattern = r"^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?(?:\+[a-zA-Z0-9.-]+)?$"
    assert re.match(pattern, version), f"Version '{version}' does not follow semantic versioning"


def test_version_consistency():
    """Test that version is consistent across all files"""
    base_path = Path(__file__).parent.parent

    # Read version from VERSION file
    with open(base_path / "VERSION", "r") as f:
        version_file_content = f.read().strip()

    # Read version from __init__.py
    import importlib.util

    init_file = base_path / "src" / "__init__.py"
    spec = importlib.util.spec_from_file_location("src", init_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    init_version = module.__version__

    # Read version from setup.py (by checking the VERSION file is used)
    setup_file = base_path / "setup.py"
    with open(setup_file, "r") as f:
        setup_content = f.read()
        assert 'with open("VERSION"' in setup_content, "setup.py doesn't read from VERSION file"

    # Compare versions
    assert (
        version_file_content == init_version
    ), f"Version mismatch: VERSION file ({version_file_content}) != __init__.py ({init_version})"


def test_changelog_exists():
    """Test that CHANGELOG.md exists"""
    base_path = Path(__file__).parent.parent
    changelog = base_path / "CHANGELOG.md"
    assert changelog.exists(), "CHANGELOG.md does not exist"

    # Check that current version is documented
    with open(base_path / "VERSION", "r") as f:
        current_version = f.read().strip()

    with open(changelog, "r") as f:
        changelog_content = f.read()
        assert (
            f"[{current_version}]" in changelog_content
        ), f"Current version {current_version} not documented in CHANGELOG.md"


def test_versioning_documentation():
    """Test that versioning strategy is documented"""
    base_path = Path(__file__).parent.parent
    versioning_doc = base_path / "docs" / "VERSIONING.md"
    assert versioning_doc.exists(), "docs/VERSIONING.md does not exist"

    with open(versioning_doc, "r") as f:
        content = f.read()
        assert "Semantic Versioning" in content, "Semantic versioning not mentioned"
        assert "MAJOR.MINOR.PATCH" in content, "Version format not documented"
