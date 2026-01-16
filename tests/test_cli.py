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
        
        # Check the content - verify using the Prompt model for format-agnostic parsing
        from promptkeep.models import Prompt
        content = new_prompt_file.read_text()
        prompt = Prompt.from_markdown(content)
        assert prompt.title == "Test Prompt"
        assert prompt.description == "A test prompt"
        assert sorted(prompt.tags) == ["example", "test"]  # Tags (sorted alphabetically)


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


@patch("promptkeep.cli.subprocess.check_output")
@patch("promptkeep.cli.open_editor")
def test_edit_command(mock_open_editor, mock_check_output, tmp_path):
    """Test the edit command."""
    # Create a test vault
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    prompts_dir = vault_dir / "Prompts"
    prompts_dir.mkdir()

    # Create a test prompt
    test_prompt = prompts_dir / "test.md"
    test_prompt.write_text("""---
title: "Test Prompt"
tags: ["test", "example"]
---
This is a test prompt.""")

    # Mock fzf to return our test prompt
    mock_check_output.return_value = str(test_prompt).encode()
    mock_open_editor.return_value = True

    # Test without tags
    cli.edit_command(vault_path=str(vault_dir), tags=None)

    # Test with tags
    cli.edit_command(vault_path=str(vault_dir), tags=["test"])

    # Verify the editor was called twice
    assert mock_open_editor.call_count == 2
    assert mock_check_output.call_count == 2

@patch("promptkeep.cli.subprocess.check_output")
@patch("promptkeep.cli.open_editor")
def test_edit_command_editor_failure(mock_open_editor, mock_check_output, tmp_path):
    """Test the edit command when editor fails."""
    # Create a test vault
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    prompts_dir = vault_dir / "Prompts"
    prompts_dir.mkdir()

    # Create a test prompt
    test_prompt = prompts_dir / "test.md"
    test_prompt.write_text("""---
title: "Test Prompt"
tags: ["test"]
---
This is a test prompt.""")

    # Mock fzf to return our test prompt
    mock_check_output.return_value = str(test_prompt).encode()
    mock_open_editor.return_value = False

    with pytest.raises(typer.Exit) as exc_info:
        cli.edit_command(vault_path=str(vault_dir), tags=None)
    assert exc_info.value.exit_code == 1

@patch("promptkeep.cli.subprocess.check_output")
def test_edit_command_fzf_not_found(mock_check_output, tmp_path):
    """Test the edit command when fzf is not installed."""
    # Create a test vault
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    prompts_dir = vault_dir / "Prompts"
    prompts_dir.mkdir()

    # Create a test prompt
    test_prompt = prompts_dir / "test.md"
    test_prompt.write_text("""---
title: "Test Prompt"
tags: ["test"]
---
This is a test prompt.""")

    # Mock fzf to raise FileNotFoundError
    mock_check_output.side_effect = FileNotFoundError()

    with pytest.raises(typer.Exit) as exc_info:
        cli.edit_command(vault_path=str(vault_dir), tags=None)
    assert exc_info.value.exit_code == 1


# =============================================================================
# Security Tests for open_editor
# =============================================================================


def test_open_editor_with_spaces_in_command(tmp_path):
    """Test that editor commands with arguments like 'code --wait' work safely."""
    test_file = tmp_path / "test.md"
    test_file.write_text("test content")

    with patch.dict(os.environ, {"EDITOR": "code --wait"}):
        with patch("promptkeep.utils.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = open_editor(test_file)

            assert result is True
            mock_run.assert_called_once()
            call_args = mock_run.call_args

            # Verify list-based call (not shell=True)
            # The first positional argument should be a list
            assert isinstance(call_args[0][0], list), "subprocess.run should be called with a list"
            # shell should not be True
            assert call_args[1].get("shell") is not True, "shell=True should not be used"


def test_open_editor_does_not_use_shell(tmp_path):
    """Test that open_editor never uses shell=True with user input."""
    test_file = tmp_path / "test.md"
    test_file.write_text("test content")

    # Test with simple editor
    with patch.dict(os.environ, {"EDITOR": "vim"}):
        with patch("promptkeep.utils.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            open_editor(test_file)

            call_kwargs = mock_run.call_args[1]
            assert call_kwargs.get("shell") is not True, "shell=True should not be used"


def test_open_editor_handles_shell_metacharacters_safely(tmp_path):
    """Test that shell metacharacters in EDITOR are not interpreted."""
    test_file = tmp_path / "test.md"
    test_file.write_text("test content")

    # Malicious EDITOR attempting command injection
    with patch.dict(os.environ, {"EDITOR": "vim; echo INJECTED"}):
        with patch("promptkeep.utils.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            open_editor(test_file)

            call_args = mock_run.call_args[0][0]
            # The command should be passed as a list, treating the whole
            # "vim; echo INJECTED" as a single command name (which will fail to find)
            # or properly split by shlex (which treats ; as part of the string)
            assert isinstance(call_args, list), "Command should be a list"
            # The semicolon should NOT cause shell command separation
            # With shlex.split, "vim; echo INJECTED" -> ["vim;", "echo", "INJECTED"]
            # which means "vim;" is treated as the command name, not "vim" followed by shell command
            assert "vim;" in str(call_args) or "vim; echo INJECTED" in str(call_args[0])


def test_open_editor_with_quoted_paths(tmp_path):
    """Test that paths with spaces are handled correctly."""
    dir_with_space = tmp_path / "path with spaces"
    dir_with_space.mkdir()
    test_file = dir_with_space / "test file.md"
    test_file.write_text("test content")

    with patch.dict(os.environ, {"EDITOR": "vim"}):
        with patch("promptkeep.utils.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = open_editor(test_file)

            assert result is True
            call_args = mock_run.call_args[0][0]
            # The file path should be properly included in the list
            assert str(test_file) in call_args