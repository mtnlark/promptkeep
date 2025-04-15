"""Test suite for the PromptKeep CLI module.

This module contains tests for the command-line interface of PromptKeep.
It tests the following functionality:
- Vault initialization and management
- Prompt creation and editing
- Prompt selection and clipboard operations
- File path validation and sanitization

The tests use temporary directories and mocking to ensure isolation
and prevent side effects on the actual filesystem.
"""
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

import pytest
import typer
from promptkeep import cli
from promptkeep.utils import (
    copy_to_clipboard,
    extract_prompt_content,
    find_vault_path,
    open_editor,
    sanitize_filename,
)


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


def test_init_overwrites():
    """Test that init overwrites existing directory"""
    with TemporaryDirectory() as temp_dir:
        # Create initial vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Create a file that should be removed
        test_file = vault_path / "test.txt"
        test_file.write_text("test")
        
        # Run init again
        cli.init_command(str(vault_path))
        
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
        
        # Mock Path to handle both default and env paths
        with patch("promptkeep.utils.Path") as mock_path:
            # Mock default path to not exist
            mock_default = MagicMock()
            mock_default.exists.return_value = False
            mock_default.expanduser.return_value.absolute.return_value = mock_default
            
            # Mock env path to exist
            mock_env = MagicMock()
            mock_env.exists.return_value = True
            mock_env.expanduser.return_value.absolute.return_value = mock_env
            mock_env.__truediv__.return_value.exists.return_value = True
            
            def path_factory(path_str):
                if path_str == "~/PromptVault":
                    return mock_default
                return mock_env
            
            mock_path.side_effect = path_factory
            
            # Test with no vault
            with patch.dict(os.environ, {}):
                assert find_vault_path() is None
            
            # Test with environment variable
            with patch.dict(os.environ, {"PROMPTKEEP_VAULT": str(vault_path)}):
                found_path = find_vault_path()
                assert found_path is not None
                assert found_path == mock_env


@patch("promptkeep.cli.open_editor")
def test_add_command(mock_open_editor):
    """Test that add command creates a new prompt"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Mock the editor so it doesn't actually open
        mock_open_editor.return_value = True
        
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


@patch("promptkeep.cli.open_editor")
def test_add_command_editor_failure(mock_open_editor):
    """Test that add command handles editor failure"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Mock the editor to fail
        mock_open_editor.return_value = False
        
        # Run add command
        with pytest.raises(typer.Exit) as exc_info:
            cli.add_command(
                title="Test Prompt",
                description="A test prompt",
                tags=["test", "example"],
                vault_path=str(vault_path)
            )
        
        assert exc_info.value.exit_code == 1
        
        # Check that no new prompt file was created
        prompt_files = list(Path(vault_path / "Prompts").glob("*.md"))
        assert len(prompt_files) == 1  # Only the example prompt


@patch("promptkeep.cli.open_editor")
def test_add_command_duplicate_warning(mock_open_editor):
    """Test that add command warns about duplicate prompts"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Mock the editor so it doesn't actually open
        mock_open_editor.return_value = True
        
        # Create a prompt with the same title
        cli.add_command(
            title="Test Prompt",
            description="A test prompt",
            tags=["test", "example"],
            vault_path=str(vault_path)
        )
        
        # Try to create another prompt with the same title
        with patch("promptkeep.cli.typer.confirm") as mock_confirm:
            mock_confirm.return_value = True
            cli.add_command(
                title="Test Prompt",
                description="Another test prompt",
                tags=["test"],
                vault_path=str(vault_path)
            )
            
            # Verify that confirm was called
            mock_confirm.assert_called_once()


@patch("promptkeep.cli.subprocess.check_output")
@patch("promptkeep.utils.pyperclip.copy")
def test_pick_command(mock_copy, mock_check_output):
    """Test that pick command works correctly"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Create a test prompt
        test_prompt = vault_path / "Prompts" / "test_prompt.md"
        test_prompt.write_text("""---
title: "Test Prompt"
description: "A test prompt"
tags: ["test"]
---
This is the prompt content""")
        
        # Mock fzf selection
        mock_check_output.return_value = str(test_prompt).encode()
        
        # Test without tags
        cli.pick_command(vault_path=str(vault_path), tags=None)
        mock_copy.assert_called_once_with("This is the prompt content")
        mock_copy.reset_mock()
        
        # Test with matching tag
        cli.pick_command(vault_path=str(vault_path), tags=["test"])
        mock_copy.assert_called_once_with("This is the prompt content")
        mock_copy.reset_mock()
        
        # Test with non-matching tag
        with pytest.raises(typer.Exit) as exc_info:
            cli.pick_command(vault_path=str(vault_path), tags=["nonexistent"])
        assert exc_info.value.exit_code == 1


@patch("promptkeep.cli.subprocess.check_output")
def test_pick_command_no_prompts(mock_check_output):
    """Test pick command when no prompts exist"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Remove the example prompt
        (vault_path / "Prompts" / "example_prompt.md").unlink()
        
        # Run pick command
        with pytest.raises(typer.Exit) as exc_info:
            cli.pick_command(vault_path=str(vault_path), tags=None)
        
        assert exc_info.value.exit_code == 1  # Should exit with error


@patch("promptkeep.cli.subprocess.check_output")
def test_pick_command_fzf_not_found(mock_check_output):
    """Test pick command when fzf is not installed"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))
        
        # Mock fzf not found
        mock_check_output.side_effect = FileNotFoundError
        
        # Run pick command
        with pytest.raises(typer.Exit) as exc_info:
            cli.pick_command(vault_path=str(vault_path), tags=None)
        
        assert exc_info.value.exit_code == 1  # Should exit with error


def test_sanitize_filename():
    """Test filename sanitization"""
    assert sanitize_filename("Test Prompt") == "test-prompt"
    assert sanitize_filename("Test/Prompt") == "test-prompt"
    assert sanitize_filename("Test:Prompt") == "test-prompt"
    assert sanitize_filename("Test*Prompt") == "test-prompt"
    assert sanitize_filename("Test?Prompt") == "test-prompt"
    assert sanitize_filename("Test<Prompt") == "test-prompt"
    assert sanitize_filename("Test>Prompt") == "test-prompt"
    assert sanitize_filename("Test|Prompt") == "test-prompt"
    assert sanitize_filename("Test\"Prompt") == "test-prompt"
    assert sanitize_filename("Test\\Prompt") == "test-prompt"
    assert sanitize_filename("Test/Prompt") == "test-prompt"
    # Test length limit
    long_title = "Test Prompt" * 100
    assert len(sanitize_filename(long_title)) <= 100 