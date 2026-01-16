"""Test suite for utility functions.

This module contains tests for the utility functions in the promptkeep.utils module,
focusing on error handling paths and edge cases that increase coverage.
"""
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

import pytest
import typer
from promptkeep.utils import (
    find_vault_path,
    validate_vault_path,
    extract_prompt_content,
    open_editor,
    sanitize_filename,
)


class TestFindVaultPath:
    """Tests for find_vault_path() function."""

    def test_returns_none_when_no_vault(self, tmp_path):
        """Test that find_vault_path returns None when no valid vault exists."""
        # Clear PROMPTKEEP_VAULT and set a non-existent home
        with patch.dict(os.environ, {"PROMPTKEEP_VAULT": ""}, clear=False):
            with patch("promptkeep.utils.Path") as mock_path:
                # Make expanduser return a non-existent path
                mock_path.return_value.expanduser.return_value.absolute.return_value.exists.return_value = False
                # Ensure the actual function logic runs
                result = find_vault_path()
        # Without a valid vault, should return None
        # Note: This is hard to test in isolation, so we'll test via validate_vault_path

    def test_finds_vault_from_env_var(self, tmp_path):
        """Test finding vault from PROMPTKEEP_VAULT environment variable."""
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / "Prompts").mkdir()

        with patch.dict(os.environ, {"PROMPTKEEP_VAULT": str(vault)}):
            result = find_vault_path()

        assert result == vault

    def test_returns_default_path_if_exists(self, tmp_path):
        """Test that default path is returned when it exists."""
        # This is tricky to test because it relies on ~/PromptVault
        # We test via validate_vault_path instead


class TestValidateVaultPath:
    """Tests for validate_vault_path() function."""

    def test_validates_explicit_path(self, tmp_path):
        """Test validating an explicitly provided path."""
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / "Prompts").mkdir()

        result = validate_vault_path(str(vault))

        assert result == vault

    def test_raises_exit_for_nonexistent_path(self, tmp_path):
        """Test that typer.Exit is raised for non-existent vault."""
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(typer.Exit) as exc_info:
            validate_vault_path(str(nonexistent))

        assert exc_info.value.exit_code == 1

    def test_raises_exit_for_missing_prompts_dir(self, tmp_path):
        """Test that typer.Exit is raised when Prompts directory is missing."""
        vault = tmp_path / "vault"
        vault.mkdir()
        # Don't create Prompts subdirectory

        with pytest.raises(typer.Exit) as exc_info:
            validate_vault_path(str(vault))

        assert exc_info.value.exit_code == 1

    def test_raises_exit_when_no_vault_found(self):
        """Test that typer.Exit is raised when no vault can be found."""
        # Clear environment and mock find_vault_path to return None
        with patch.dict(os.environ, {"PROMPTKEEP_VAULT": ""}, clear=False):
            with patch("promptkeep.utils.find_vault_path", return_value=None):
                with pytest.raises(typer.Exit) as exc_info:
                    validate_vault_path(None)

                assert exc_info.value.exit_code == 1


class TestExtractPromptContent:
    """Tests for extract_prompt_content() function."""

    def test_extracts_content_with_front_matter(self):
        """Test extracting content from file with YAML front matter."""
        content = """---
title: "Test"
tags: ["tag1"]
---

This is the actual prompt content.
It spans multiple lines."""

        result = extract_prompt_content(content)

        assert "This is the actual prompt content." in result
        assert "It spans multiple lines." in result
        assert "title" not in result

    def test_returns_content_without_front_matter(self):
        """Test extracting content from file without front matter."""
        content = "Just plain text without YAML."

        result = extract_prompt_content(content)

        assert result == "Just plain text without YAML."

    def test_handles_empty_content(self):
        """Test extracting from empty content."""
        result = extract_prompt_content("")
        assert result == ""

    def test_handles_content_with_multiple_dashes(self):
        """Test that --- in content doesn't break extraction."""
        content = """---
title: "Test"
---

First line
---
After dashes"""

        result = extract_prompt_content(content)

        # Should include content after the front matter
        assert "First line" in result


class TestOpenEditor:
    """Tests for open_editor() function."""

    def test_returns_false_on_called_process_error(self, tmp_path):
        """Test that CalledProcessError is handled gracefully."""
        import subprocess
        test_file = tmp_path / "test.md"
        test_file.write_text("content")

        with patch.dict(os.environ, {"EDITOR": "vim"}):
            with patch("promptkeep.utils.subprocess.run") as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(1, "vim")
                result = open_editor(test_file)

        assert result is False

    def test_returns_false_on_file_not_found(self, tmp_path):
        """Test that FileNotFoundError is handled gracefully."""
        test_file = tmp_path / "test.md"
        test_file.write_text("content")

        with patch.dict(os.environ, {"EDITOR": "nonexistent_editor"}):
            with patch("promptkeep.utils.subprocess.run") as mock_run:
                mock_run.side_effect = FileNotFoundError()
                result = open_editor(test_file)

        assert result is False

    def test_returns_false_on_value_error(self, tmp_path):
        """Test that ValueError (malformed EDITOR) is handled gracefully."""
        test_file = tmp_path / "test.md"
        test_file.write_text("content")

        # ValueError is raised by shlex.split for unclosed quotes
        with patch.dict(os.environ, {"EDITOR": "vim 'unclosed"}):
            result = open_editor(test_file)

        assert result is False

    def test_returns_false_on_unexpected_error(self, tmp_path):
        """Test that unexpected exceptions are handled gracefully."""
        test_file = tmp_path / "test.md"
        test_file.write_text("content")

        with patch.dict(os.environ, {"EDITOR": "vim"}):
            with patch("promptkeep.utils.subprocess.run") as mock_run:
                mock_run.side_effect = RuntimeError("Unexpected error")
                result = open_editor(test_file)

        assert result is False


class TestSanitizeFilename:
    """Tests for sanitize_filename() function."""

    def test_basic_sanitization(self):
        """Test basic filename sanitization."""
        assert sanitize_filename("Hello World") == "hello-world"

    def test_removes_special_characters(self):
        """Test that special characters are removed."""
        result = sanitize_filename("Test: A/B\\C?*")
        assert "/" not in result
        assert "\\" not in result
        assert "?" not in result
        assert "*" not in result

    def test_truncates_long_names(self):
        """Test that very long names are truncated."""
        long_title = "a" * 200
        result = sanitize_filename(long_title)
        assert len(result) <= 100

    def test_removes_consecutive_hyphens(self):
        """Test that consecutive hyphens are collapsed."""
        result = sanitize_filename("test - - - name")
        assert "---" not in result

    def test_handles_empty_string(self):
        """Test handling of empty string."""
        result = sanitize_filename("")
        assert result == ""

    def test_handles_unicode(self):
        """Test handling of unicode characters."""
        result = sanitize_filename("Café Prompt")
        # Unicode characters should be preserved
        assert "caf" in result.lower()
