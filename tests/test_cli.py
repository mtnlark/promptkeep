"""Basic tests for the CLI module"""
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

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