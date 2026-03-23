"""
Tests for the CLI module.

These tests verify the command-line interface functionality including:
- Vault initialization
- Prompt creation and editing
- Prompt selection and clipboard operations

Tests use mocking to avoid filesystem changes and external dependencies,
and prevent side effects on the actual filesystem.
"""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
import typer

from promptkeep import cli
from promptkeep.utils import sanitize_filename


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
        assert 'title: "Example Prompt"' in template_content


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


# NOTE: test_find_vault_path removed - tests utils module, not CLI


@patch("promptkeep.services.SystemEditor.open")
def test_add_command(mock_editor_open):
    """Test that add command creates a new prompt"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))

        # Mock the editor so it doesn't actually open
        mock_editor_open.return_value = None

        # Run add command
        cli.add_command(
            title="Test Prompt",
            description="A test prompt",
            tags=["test", "example"],
            vault_path=str(vault_path),
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
        # Tags are sorted alphabetically
        assert sorted(prompt.tags) == ["example", "test"]


@patch("promptkeep.services.SystemEditor.open")
def test_add_command_editor_failure(mock_editor_open):
    """Test that add command handles editor failure"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))

        # Mock the editor to raise an EditorError
        from promptkeep.exceptions import EditorError

        mock_editor_open.side_effect = EditorError("Editor failed")

        # Run add command
        with pytest.raises(typer.Exit) as exc_info:
            cli.add_command(
                title="Test Prompt",
                description="A test prompt",
                tags=["test", "example"],
                vault_path=str(vault_path),
            )

        assert exc_info.value.exit_code == 1

        # Check that no new prompt file was created
        prompt_files = list(Path(vault_path / "Prompts").glob("*.md"))
        assert len(prompt_files) == 1  # Only the example prompt


@patch("promptkeep.services.SystemEditor.open")
def test_add_command_duplicate_warning(mock_editor_open):
    """Test that add command warns about duplicate prompts"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))

        # Mock the editor so it doesn't actually open
        mock_editor_open.return_value = None

        # Create a prompt with the same title
        cli.add_command(
            title="Test Prompt",
            description="A test prompt",
            tags=["test", "example"],
            vault_path=str(vault_path),
        )

        # Try to create another prompt with the same title
        with patch("promptkeep.cli.typer.confirm") as mock_confirm:
            mock_confirm.return_value = True
            cli.add_command(
                title="Test Prompt",
                description="Another test prompt",
                tags=["test"],
                vault_path=str(vault_path),
            )

            # Verify that confirm was called
            mock_confirm.assert_called_once()


@patch("promptkeep.services.FzfPromptSelector.select")
@patch("promptkeep.services.SystemClipboard.copy")
def test_pick_command(mock_clipboard_copy, mock_selector_select):
    """Test that pick command works correctly"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))

        # Create a test prompt
        test_prompt = vault_path / "Prompts" / "test_prompt.md"
        test_prompt.write_text(
            """---
title: "Test Prompt"
description: "A test prompt"
tags: ["test"]
---
This is the prompt content"""
        )

        # Mock selector to return the test prompt
        mock_selector_select.return_value = test_prompt

        # Test without tags
        cli.pick_command(vault_path=str(vault_path), tags=None)
        mock_clipboard_copy.assert_called_once_with("This is the prompt content")
        mock_clipboard_copy.reset_mock()

        # Test with matching tag
        cli.pick_command(vault_path=str(vault_path), tags=["test"])
        mock_clipboard_copy.assert_called_once_with("This is the prompt content")
        mock_clipboard_copy.reset_mock()

        # Test with non-matching tag
        with pytest.raises(typer.Exit) as exc_info:
            cli.pick_command(vault_path=str(vault_path), tags=["nonexistent"])
        assert exc_info.value.exit_code == 1


def test_pick_command_no_prompts():
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


@patch("promptkeep.services.FzfPromptSelector.select")
def test_pick_command_fzf_not_found(mock_selector_select):
    """Test pick command when fzf is not installed"""
    with TemporaryDirectory() as temp_dir:
        # Create test vault
        vault_path = Path(temp_dir) / "test_vault"
        cli.init_command(str(vault_path))

        # Mock selector to raise SelectorNotFoundError
        from promptkeep.exceptions import SelectorNotFoundError

        mock_selector_select.side_effect = SelectorNotFoundError()

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
    assert sanitize_filename('Test"Prompt') == "test-prompt"
    assert sanitize_filename("Test\\Prompt") == "test-prompt"
    assert sanitize_filename("Test/Prompt") == "test-prompt"
    # Test length limit
    long_title = "Test Prompt" * 100
    assert len(sanitize_filename(long_title)) <= 100


@patch("promptkeep.services.FzfPromptSelector.select")
@patch("promptkeep.services.SystemEditor.open")
def test_edit_command(mock_editor_open, mock_selector_select, tmp_path):
    """Test the edit command."""
    # Create a test vault
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    prompts_dir = vault_dir / "Prompts"
    prompts_dir.mkdir()

    # Create a test prompt
    test_prompt = prompts_dir / "test.md"
    test_prompt.write_text(
        """---
title: "Test Prompt"
tags: ["test", "example"]
---
This is a test prompt."""
    )

    # Mock selector to return our test prompt
    mock_selector_select.return_value = test_prompt
    mock_editor_open.return_value = None

    # Test without tags
    cli.edit_command(vault_path=str(vault_dir), tags=None)

    # Test with tags
    cli.edit_command(vault_path=str(vault_dir), tags=["test"])

    # Verify the editor was called twice
    assert mock_editor_open.call_count == 2
    assert mock_selector_select.call_count == 2


@patch("promptkeep.services.FzfPromptSelector.select")
@patch("promptkeep.services.SystemEditor.open")
def test_edit_command_editor_failure(mock_editor_open, mock_selector_select, tmp_path):
    """Test the edit command when editor fails."""
    # Create a test vault
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    prompts_dir = vault_dir / "Prompts"
    prompts_dir.mkdir()

    # Create a test prompt
    test_prompt = prompts_dir / "test.md"
    test_prompt.write_text(
        """---
title: "Test Prompt"
tags: ["test"]
---
This is a test prompt."""
    )

    # Mock selector to return our test prompt
    mock_selector_select.return_value = test_prompt

    # Mock editor to raise an EditorError
    from promptkeep.exceptions import EditorError

    mock_editor_open.side_effect = EditorError("Editor failed")

    with pytest.raises(typer.Exit) as exc_info:
        cli.edit_command(vault_path=str(vault_dir), tags=None)
    assert exc_info.value.exit_code == 1


@patch("promptkeep.services.FzfPromptSelector.select")
def test_edit_command_fzf_not_found(mock_selector_select, tmp_path):
    """Test the edit command when fzf is not installed."""
    # Create a test vault
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    prompts_dir = vault_dir / "Prompts"
    prompts_dir.mkdir()

    # Create a test prompt
    test_prompt = prompts_dir / "test.md"
    test_prompt.write_text(
        """---
title: "Test Prompt"
tags: ["test"]
---
This is a test prompt."""
    )

    # Mock selector to raise SelectorNotFoundError
    from promptkeep.exceptions import SelectorNotFoundError

    mock_selector_select.side_effect = SelectorNotFoundError()

    with pytest.raises(typer.Exit) as exc_info:
        cli.edit_command(vault_path=str(vault_dir), tags=None)
    assert exc_info.value.exit_code == 1


# =============================================================================
# Security Tests for open_editor - MOVED TO test_utils.py
# =============================================================================
# NOTE: These tests are for the utils module, not the CLI module.
# They should be in test_utils.py instead.
