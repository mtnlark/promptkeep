"""Basic tests for the CLI module"""
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

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
        assert find_vault_path() is None  # Default path doesn't exist
        
        # Test with environment variable
        with patch.dict(os.environ, {"PROMPTKEEP_VAULT": str(vault_path)}):
            found_path = find_vault_path()
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
@patch("promptkeep.cli.subprocess.run")
def test_pick_command(mock_run, mock_check_output):
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
        
        # Mock clipboard copy
        mock_run.return_value = None
        
        # Run pick command
        cli.pick_command(vault_path=str(vault_path))
        
        # Verify clipboard copy was called with correct content
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["pbcopy"]
        assert mock_run.call_args[1]["input"] == b"This is the prompt content"


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
            cli.pick_command(vault_path=str(vault_path))
        
        assert exc_info.value.exit_code == 0  # Should exit with 0 (warning)


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
            cli.pick_command(vault_path=str(vault_path))
        
        assert exc_info.value.exit_code == 1  # Should exit with error


@patch("promptkeep.cli.subprocess.check_output")
@patch("promptkeep.cli.subprocess.run")
def test_pick_command_updates_last_used(mock_run, mock_check_output):
    """Test that pick command updates the last_used field"""
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
        
        # Mock clipboard copy
        mock_run.return_value = None
        
        # Run pick command
        cli.pick_command(vault_path=str(vault_path))
        
        # Verify the file was updated with last_used
        content = test_prompt.read_text()
        assert "last_used" in content


@patch("promptkeep.cli.subprocess.check_output")
@patch("promptkeep.cli.subprocess.run")
def test_pick_command_preview(mock_run, mock_check_output):
    """Test that pick command uses fzf preview"""
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
        
        # Mock clipboard copy
        mock_run.return_value = None
        
        # Run pick command
        cli.pick_command(vault_path=str(vault_path))
        
        # Verify fzf was called with preview options
        mock_check_output.assert_called_once()
        call_args = mock_check_output.call_args[0][0]
        assert "--preview" in call_args
        assert "--preview-window" in call_args


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
    assert sanitize_filename("Test Prompt" * 100) == "test-prompt" * 10  # Length limit 