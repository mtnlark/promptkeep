"""Tests for service implementations."""

import subprocess
from unittest.mock import patch

import pytest

from promptkeep.exceptions import (
    EditorError,
    EditorNotFoundError,
    SelectorNotFoundError,
)
from promptkeep.services import FzfPromptSelector, SystemClipboard, SystemEditor


class TestSystemClipboard:
    """Tests for SystemClipboard service."""

    def test_copy_calls_pyperclip(self):
        """Should delegate to pyperclip.copy()."""
        with patch("promptkeep.services.pyperclip") as mock_pyperclip:
            clipboard = SystemClipboard()
            clipboard.copy("test text")
            mock_pyperclip.copy.assert_called_once_with("test text")


class TestSystemEditor:
    """Tests for SystemEditor service."""

    def test_open_calls_subprocess(self, tmp_path):
        """Should call subprocess.run with editor command."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with patch("promptkeep.services.subprocess.run") as mock_run:
            editor = SystemEditor("vim")
            result = editor.open(test_file)

            assert result is True
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert call_args[0] == "vim"
            assert str(test_file) in call_args

    def test_open_handles_editor_with_args(self, tmp_path):
        """Should handle editor commands with arguments."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with patch("promptkeep.services.subprocess.run") as mock_run:
            editor = SystemEditor("code --wait")
            editor.open(test_file)

            call_args = mock_run.call_args[0][0]
            assert call_args[0] == "code"
            assert "--wait" in call_args

    def test_open_raises_not_found_error(self, tmp_path):
        """Should raise EditorNotFoundError when editor not found."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with patch(
            "promptkeep.services.subprocess.run",
            side_effect=FileNotFoundError(),
        ):
            editor = SystemEditor("nonexistent-editor")
            with pytest.raises(EditorNotFoundError) as exc_info:
                editor.open(test_file)
            assert exc_info.value.editor == "nonexistent-editor"

    def test_open_raises_editor_error_on_failure(self, tmp_path):
        """Should raise EditorError when editor exits with error."""
        test_file = tmp_path / "test.txt"
        test_file.touch()

        with patch(
            "promptkeep.services.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "vim"),
        ):
            editor = SystemEditor("vim")
            with pytest.raises(EditorError):
                editor.open(test_file)


class TestFzfPromptSelector:
    """Tests for FzfPromptSelector service."""

    def test_select_returns_path_on_selection(self, tmp_path):
        """Should return selected path."""
        file1 = tmp_path / "prompt1.md"
        file2 = tmp_path / "prompt2.md"
        file1.touch()
        file2.touch()

        with patch("promptkeep.services.subprocess.check_output") as mock_output:
            mock_output.return_value = str(file1).encode()
            selector = FzfPromptSelector("preview script")
            result = selector.select([file1, file2], "Select: ")

            assert result == file1

    def test_select_returns_none_on_cancel(self, tmp_path):
        """Should return None when user cancels."""
        file1 = tmp_path / "prompt1.md"
        file1.touch()

        with patch(
            "promptkeep.services.subprocess.check_output",
            side_effect=subprocess.CalledProcessError(1, "fzf"),
        ):
            selector = FzfPromptSelector("preview script")
            result = selector.select([file1], "Select: ")
            assert result is None

    def test_select_returns_none_for_empty_list(self):
        """Should return None for empty items list."""
        selector = FzfPromptSelector("preview script")
        result = selector.select([], "Select: ")
        assert result is None

    def test_select_raises_not_found_error(self, tmp_path):
        """Should raise SelectorNotFoundError when fzf not installed."""
        file1 = tmp_path / "prompt1.md"
        file1.touch()

        with patch(
            "promptkeep.services.subprocess.check_output",
            side_effect=FileNotFoundError(),
        ):
            selector = FzfPromptSelector("preview script")
            with pytest.raises(SelectorNotFoundError):
                selector.select([file1], "Select: ")

    def test_select_passes_preview_script(self, tmp_path):
        """Should pass preview script to fzf."""
        file1 = tmp_path / "prompt1.md"
        file1.touch()

        with patch("promptkeep.services.subprocess.check_output") as mock_output:
            mock_output.return_value = str(file1).encode()
            selector = FzfPromptSelector("my preview script {}")
            selector.select([file1], "Select: ")

            call_args = mock_output.call_args[0][0]
            assert "--preview" in call_args
            preview_idx = call_args.index("--preview")
            assert call_args[preview_idx + 1] == "my preview script {}"
