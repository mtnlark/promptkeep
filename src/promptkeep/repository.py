"""Repository pattern for prompt storage.

This module provides a file-based repository for storing and retrieving prompts.
The repository handles all file I/O operations, keeping the CLI layer clean and
making it easy to test business logic in isolation.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from promptkeep.constants import PROMPT_FILE_EXTENSION, PROMPTS_DIR_NAME
from promptkeep.models import Prompt
from promptkeep.utils import sanitize_filename


class PromptRepository:
    """File-based repository for prompts.

    This class provides an abstraction layer over the file system for prompt
    storage. All prompt files are stored in the Prompts subdirectory of the
    vault path.

    Attributes:
        vault_path: Path to the root vault directory
        prompts_dir: Path to the Prompts subdirectory where prompts are stored
    """

    def __init__(self, vault_path: Path) -> None:
        """Initialize the repository.

        Args:
            vault_path: Path to the root vault directory
        """
        self.vault_path = vault_path
        self.prompts_dir = vault_path / PROMPTS_DIR_NAME

    def list_all(self) -> List[Prompt]:
        """Get all prompts from the vault.

        Returns:
            List of Prompt objects for all markdown files in the prompts directory.
            Unreadable files are silently skipped.
        """
        prompts = []
        for filepath in self.get_file_paths():
            try:
                prompts.append(self.get_by_path(filepath))
            except OSError:
                # Skip unreadable files
                continue
        return prompts

    def filter_by_tags(self, tags: List[str]) -> List[Prompt]:
        """Get prompts that have all specified tags.

        Implements AND logic: only prompts with ALL specified tags are returned.

        Args:
            tags: List of tag names to filter by

        Returns:
            List of Prompt objects that have all the specified tags
        """
        return [p for p in self.list_all() if p.has_tags(tags)]

    def get_by_path(self, filepath: Path) -> Prompt:
        """Load a prompt from a file path.

        Args:
            filepath: Path to the markdown file

        Returns:
            Prompt object with content loaded from the file

        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If the file can't be read
        """
        content = filepath.read_text(encoding="utf-8")
        return Prompt.from_markdown(content, file_path=filepath)

    def get_file_paths(self, tags: Optional[List[str]] = None) -> List[Path]:
        """Get file paths, optionally filtered by tags.

        Args:
            tags: Optional list of tags to filter by. If None, returns all paths.

        Returns:
            List of Path objects for matching prompt files
        """
        paths = list(self.prompts_dir.glob(f"*{PROMPT_FILE_EXTENSION}"))

        if tags:
            filtered = []
            for path in paths:
                try:
                    prompt = self.get_by_path(path)
                    if prompt.has_tags(tags):
                        filtered.append(path)
                except OSError:
                    continue
            return filtered

        return paths

    def save(self, prompt: Prompt, filename: Optional[str] = None) -> Path:
        """Save a prompt to a file.

        If no filename is provided, generates one from the prompt title and
        current timestamp.

        Args:
            prompt: The Prompt object to save
            filename: Optional explicit filename. If not provided, generates
                      a filename from the title and timestamp.

        Returns:
            Path to the saved file
        """
        if filename is None:
            base_name = sanitize_filename(prompt.title)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{base_name}-{timestamp}{PROMPT_FILE_EXTENSION}"

        filepath = self.prompts_dir / filename
        filepath.write_text(prompt.to_markdown(), encoding="utf-8")
        return filepath

    def exists_similar(self, title: str) -> List[Path]:
        """Check if prompts with similar titles exist.

        Searches for existing files that start with the sanitized version
        of the given title.

        Args:
            title: The title to check for

        Returns:
            List of Path objects for files with similar names
        """
        base_name = sanitize_filename(title)
        return list(self.prompts_dir.glob(f"{base_name}-*{PROMPT_FILE_EXTENSION}"))
