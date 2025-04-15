"""Basic tests for the CLI module"""
from promptkeep import cli

def test_app_exists():
    """Test that the Typer app exists"""
    assert cli.app is not None 