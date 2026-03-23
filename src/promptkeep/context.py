"""Application context for PromptKeep.

This module provides the composition root where all dependencies are
wired together. The AppContext holds all services and is passed to
commands, enabling dependency injection and easy testing.
"""

from dataclasses import dataclass

from rich.console import Console

from promptkeep.config import Config
from promptkeep.constants import FZF_PREVIEW_SCRIPT
from promptkeep.protocols import (
    ClipboardService,
    EditorService,
    PromptRepositoryProtocol,
    PromptSelector,
)
from promptkeep.repository import PromptRepository
from promptkeep.services import FzfPromptSelector, SystemClipboard, SystemEditor


@dataclass
class AppContext:
    """Container for all application dependencies.

    This is the composition root - the single place where concrete
    implementations are wired together. Commands receive this context
    and use the abstract interfaces, making them easy to test with mocks.
    """

    config: Config
    clipboard: ClipboardService
    editor: EditorService
    selector: PromptSelector
    console: Console
    repository: PromptRepositoryProtocol

    @classmethod
    def create_default(cls, config: Config) -> "AppContext":
        """Create context with default production implementations.

        Args:
            config: Application configuration

        Returns:
            AppContext with all services wired up
        """
        return cls(
            config=config,
            clipboard=SystemClipboard(),
            editor=SystemEditor(config.editor),
            selector=FzfPromptSelector(FZF_PREVIEW_SCRIPT),
            console=Console(),
            repository=PromptRepository(config.vault_path),
        )
