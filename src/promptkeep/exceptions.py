"""Custom exception hierarchy for PromptKeep.

This module defines a hierarchy of exceptions that provide clear,
actionable error messages. All exceptions inherit from PromptKeepError,
making it easy to catch all application errors.
"""

from pathlib import Path
from typing import List, Optional


class PromptKeepError(Exception):
    """Base exception for all PromptKeep errors."""

    pass


class VaultNotFoundError(PromptKeepError):
    """Raised when no vault directory can be found."""

    def __init__(self, searched_paths: Optional[List[Path]] = None):
        self.searched_paths = searched_paths or []
        super().__init__("No vault found")


class VaultInvalidError(PromptKeepError):
    """Raised when vault exists but is malformed (missing Prompts dir)."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        super().__init__(f"Invalid vault at {vault_path}: missing Prompts directory")


class EditorError(PromptKeepError):
    """Raised when the editor fails to open or exits with error."""

    pass


class EditorNotFoundError(EditorError):
    """Raised when the configured editor is not found."""

    def __init__(self, editor: str):
        self.editor = editor
        super().__init__(f"Editor not found: {editor}")


class SelectorError(PromptKeepError):
    """Raised when the prompt selector fails."""

    pass


class SelectorNotFoundError(SelectorError):
    """Raised when fzf is not installed."""

    def __init__(self) -> None:
        super().__init__("fzf not found. Please install fzf to use this feature.")
