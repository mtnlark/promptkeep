"""Protocol definitions for PromptKeep services.

Protocols define the interfaces that services must implement. This enables
dependency injection and makes the code easier to test by allowing mock
implementations.

Uses typing.Protocol for structural subtyping - classes don't need to
explicitly inherit from these protocols, they just need to implement
the required methods.
"""

from pathlib import Path
from typing import List, Optional, Protocol

from promptkeep.models import Prompt


class ClipboardService(Protocol):
    """Interface for clipboard operations."""

    def copy(self, text: str) -> None:
        """Copy text to the system clipboard."""
        ...


class EditorService(Protocol):
    """Interface for opening files in an editor.

    Implementations should raise EditorNotFoundError if the editor binary
    is not found, or EditorError for other failures.
    """

    def open(self, file_path: Path) -> bool:
        """Open a file in the editor. Returns True on success."""
        ...


class PromptSelector(Protocol):
    """Interface for interactive prompt selection.

    Implementations should raise SelectorNotFoundError if the selection
    tool (e.g., fzf) is not installed.
    """

    def select(self, items: List[Path], prompt: str) -> Optional[Path]:
        """Show interactive selection UI. Returns None if user cancels."""
        ...


class PromptRepositoryProtocol(Protocol):
    """Interface for prompt storage operations.

    This is a read-heavy interface reflecting the primary use case of
    browsing and selecting prompts. Write operations (save) are secondary.
    Delete is intentionally omitted - users manage files directly.
    """

    def list_all(self) -> List[Prompt]:
        """Get all prompts from the vault."""
        ...

    def filter_by_tags(self, tags: List[str]) -> List[Prompt]:
        """Get prompts that have all specified tags."""
        ...

    def get_by_path(self, filepath: Path) -> Prompt:
        """Load a prompt from a file path.

        Raises:
            FileNotFoundError: If the file doesn't exist
            OSError: For permission or I/O issues
        """
        ...

    def get_file_paths(self, tags: Optional[List[str]] = None) -> List[Path]:
        """Get file paths, optionally filtered by tags."""
        ...

    def save(self, prompt: Prompt, filename: Optional[str] = None) -> Path:
        """Save a prompt to a file. Returns the path."""
        ...

    def exists_similar(self, title: str) -> List[Path]:
        """Check if prompts with similar titles exist."""
        ...
