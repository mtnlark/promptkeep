"""Basic tests for the CLI module"""
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
from promptkeep import cli

def test_app_exists():
    """Test that the Typer app exists"""
    assert cli.app is not None

def test_init_creates_vault():
    """Test that init command creates the vault structure"""
    with TemporaryDirectory() as temp_dir:
        # Run init command
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Check that directories were created
        assert vault_path.exists()
        assert (vault_path / "Prompts").exists()
        assert (vault_path / "Prompts" / "example_prompt.md").exists()
        
        # Check template content
        template_content = (vault_path / "Prompts" / "example_prompt.md").read_text()
        assert "---" in template_content
        assert "title: \"Example Prompt\"" in template_content

def test_init_force_overwrites():
    """Test that init --force overwrites existing directory"""
    with TemporaryDirectory() as temp_dir:
        # Create initial vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Create a file that should be removed
        test_file = vault_path / "test.txt"
        test_file.write_text("test")
        
        # Run init with force
        cli.init_command(str(vault_path), force=True)
        
        # Check that test file was removed
        assert not test_file.exists()
        # But template still exists
        assert (vault_path / "Prompts" / "example_prompt.md").exists()

def test_find_vault_path():
    """Test finding the vault path"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Test with explicit path
        assert cli.find_vault_path() is None  # Default path doesn't exist
        
        # Test with environment variable
        with patch.dict(os.environ, {"PROMPTKEEP_VAULT": str(vault_path)}):
            found_path = cli.find_vault_path()
            assert found_path is not None
            assert found_path == vault_path

@patch("promptkeep.cli.open_editor")
def test_add_command(mock_open_editor):
    """Test that add command creates a new prompt"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Mock the editor so it doesn't actually open
        mock_open_editor.return_value = None
        
        # Run add command
        cli.add_command(
            title="Test Prompt",
            description="A test prompt",
            tags=["test", "example"],
            vault_path=str(vault_path)
        )
        
        # Check that the prompt directory contains a file other than the example
        prompt_files = list(Path(vault_path / "Prompts").glob("*.md"))
        assert len(prompt_files) > 1
        
        # Find the non-example file
        new_prompt_file = None
        for file in prompt_files:
            if file.name != "example_prompt.md":
                new_prompt_file = file
                break
        
        assert new_prompt_file is not None
        
        # Check the content
        content = new_prompt_file.read_text()
        assert "title: \"Test Prompt\"" in content
        assert "description: \"A test prompt\"" in content
        assert "\"test\", \"example\"" in content  # Tags 