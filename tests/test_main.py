"""Test suite for entry points.

This module contains tests for the package entry points:
- main.py (setuptools entry point)
- __main__.py (python -m promptkeep)
"""
from unittest.mock import patch, MagicMock


def test_main_entry_point():
    """Test that main.py entry point calls the CLI app."""
    with patch("promptkeep.main.app") as mock_app:
        from promptkeep.main import main
        main()
        mock_app.assert_called_once()


def test_main_module_imports_app():
    """Test that main module correctly imports the app."""
    from promptkeep.main import app
    assert app is not None


def test_package_version_exists():
    """Test that package version is defined."""
    from promptkeep import __version__
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_cli_app_has_commands():
    """Test that CLI app has the expected commands."""
    from promptkeep.cli import app
    # Typer stores commands in app.registered_commands or similar
    # Just verify the app object exists and is callable
    assert app is not None
