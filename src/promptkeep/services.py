"""Concrete service implementations for PromptKeep.

This module provides production implementations of the service protocols.
Each service wraps an external dependency (pyperclip, subprocess, fzf)
and converts errors to PromptKeep exceptions.
"""

import shlex
import subprocess
from pathlib import Path
from typing import List, Optional

import pyperclip

from promptkeep.exceptions import (
    EditorError,
    EditorNotFoundError,
    SelectorNotFoundError,
)


class SystemClipboard:
    """Clipboard implementation using pyperclip."""

    def copy(self, text: str) -> None:
        """Copy text to the system clipboard."""
        pyperclip.copy(text)


class SystemEditor:
    """Editor implementation using subprocess."""

    def __init__(self, editor_command: str) -> None:
        """Initialize with the editor command."""
        self.editor_command = editor_command

    def open(self, file_path: Path) -> bool:
        """Open a file in the editor."""
        try:
            editor_parts = shlex.split(self.editor_command)
            editor_parts.append(str(file_path))
            subprocess.run(editor_parts, check=True)
            return True
        except FileNotFoundError as e:
            raise EditorNotFoundError(self.editor_command) from e
        except subprocess.CalledProcessError as e:
            raise EditorError(f"Editor exited with code {e.returncode}") from e
        except ValueError as e:
            raise EditorError(f"Invalid editor command: {e}") from e


class FzfPromptSelector:
    """Prompt selector using fzf."""

    def __init__(self, preview_script: str) -> None:
        """Initialize with the preview script."""
        self.preview_script = preview_script

    def select(self, items: List[Path], prompt: str) -> Optional[Path]:
        """Show interactive selection UI."""
        if not items:
            return None

        try:
            result = subprocess.check_output(
                ["fzf", "--prompt", prompt, "--preview", self.preview_script],
                input="\n".join(str(f) for f in items).encode(),
            )
            return Path(result.decode().strip())
        except subprocess.CalledProcessError:
            return None
        except FileNotFoundError as e:
            raise SelectorNotFoundError() from e
