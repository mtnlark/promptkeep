"""Configuration management for PromptKeep.

This module provides centralized configuration with clear precedence:
1. Explicit values passed to constructor or from_environment()
2. Environment variables
3. Default values

The Config class is immutable (frozen dataclass) to prevent accidental
modification after creation.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from promptkeep.constants import (
    DEFAULT_EDITOR,
    DEFAULT_VAULT_PATH,
    ENV_EDITOR,
    ENV_VAULT_PATH,
    PROMPTS_DIR_NAME,
)
from promptkeep.exceptions import VaultInvalidError, VaultNotFoundError


@dataclass(frozen=True)
class Config:
    """Immutable application configuration.

    Attributes:
        vault_path: Absolute path to the vault directory
        editor: Command to open files for editing
        prompts_dir_name: Name of the prompts subdirectory
    """

    vault_path: Path
    editor: str
    prompts_dir_name: str = PROMPTS_DIR_NAME

    @classmethod
    def from_environment(
        cls,
        vault_override: Optional[str] = None,
        editor_override: Optional[str] = None,
    ) -> "Config":
        """Load configuration from environment with optional overrides.

        Args:
            vault_override: Explicit vault path (highest precedence)
            editor_override: Explicit editor command (highest precedence)

        Returns:
            Config instance with resolved values
        """
        # Vault path resolution: override > env var > default
        if vault_override:
            vault_path = Path(vault_override).expanduser().absolute()
        elif env_vault := os.environ.get(ENV_VAULT_PATH):
            vault_path = Path(env_vault).expanduser().absolute()
        else:
            vault_path = Path(DEFAULT_VAULT_PATH).expanduser().absolute()

        # Editor resolution: override > env var > default
        editor = editor_override or os.environ.get(ENV_EDITOR, DEFAULT_EDITOR)

        return cls(vault_path=vault_path, editor=editor)

    @property
    def prompts_dir(self) -> Path:
        """Path to the prompts subdirectory."""
        return self.vault_path / self.prompts_dir_name

    def validate_vault(self) -> None:
        """Validate that the vault exists and is properly structured.

        Raises:
            VaultNotFoundError: If vault_path does not exist
            VaultInvalidError: If vault exists but has no Prompts directory
        """
        if not self.vault_path.exists():
            raise VaultNotFoundError([self.vault_path])
        if not self.prompts_dir.exists() or not self.prompts_dir.is_dir():
            raise VaultInvalidError(self.vault_path)
