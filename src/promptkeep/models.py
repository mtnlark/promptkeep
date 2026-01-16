"""Domain models for PromptKeep.

This module contains the core domain models used throughout the application.
The Prompt class represents a prompt with its metadata and content, providing
methods for parsing from and serializing to markdown with YAML front matter.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml

from promptkeep.constants import YAML_DELIMITER


@dataclass
class Prompt:
    """Represents a prompt with metadata and content.

    A Prompt consists of:
    - title: The name/title of the prompt
    - description: Optional description explaining the prompt's purpose
    - tags: List of tags for categorization and filtering
    - content: The actual prompt text
    - file_path: Optional path to the source file (set when loaded from disk)

    The class provides methods to parse from markdown files with YAML front matter
    and to serialize back to that format.
    """

    title: str
    description: str
    tags: List[str]
    content: str
    file_path: Optional[Path] = field(default=None)

    @classmethod
    def from_markdown(cls, markdown: str, file_path: Optional[Path] = None) -> "Prompt":
        """Parse a prompt from markdown with YAML front matter.

        The expected format is:
        ```
        ---
        title: "Prompt Title"
        description: "Optional description"
        tags: ["tag1", "tag2"]
        ---

        Actual prompt content here...
        ```

        Args:
            markdown: The raw markdown content with optional YAML front matter
            file_path: Optional path to the source file

        Returns:
            A Prompt instance with parsed metadata and content
        """
        parts = markdown.split(YAML_DELIMITER, 2)

        if len(parts) >= 3 and parts[0].strip() == "":
            # Has front matter: parts[0] is empty, parts[1] is YAML, parts[2] is content
            try:
                metadata = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                # If YAML parsing fails, treat as no front matter
                metadata = {}
            content = parts[2].strip()
        else:
            # No front matter - entire content is the prompt
            metadata = {}
            content = markdown.strip()

        return cls(
            title=metadata.get("title", ""),
            description=metadata.get("description", ""),
            tags=metadata.get("tags", []) or [],  # Handle None case
            content=content,
            file_path=file_path,
        )

    def to_markdown(self) -> str:
        """Convert prompt to markdown with YAML front matter.

        Uses yaml.dump() for proper escaping of special characters in
        title and description fields.

        Returns:
            Markdown string with YAML front matter and content
        """
        metadata = {
            "title": self.title,
            "description": self.description,
            "tags": self.tags,
        }

        # yaml.dump handles escaping automatically (quotes, colons, etc.)
        yaml_content = yaml.dump(
            metadata,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )

        return f"{YAML_DELIMITER}\n{yaml_content}{YAML_DELIMITER}\n\n{self.content}"

    def has_tags(self, required_tags: List[str]) -> bool:
        """Check if the prompt has all specified tags.

        Implements AND logic: returns True only if ALL required tags are present.

        Args:
            required_tags: List of tag names to check for

        Returns:
            True if all required tags are present (or if required_tags is empty),
            False otherwise
        """
        if not required_tags:
            return True
        return all(tag in self.tags for tag in required_tags)
