"""Tests for application context."""

from promptkeep.config import Config
from promptkeep.context import AppContext


class TestAppContext:
    """Tests for AppContext."""

    def test_create_default_returns_context(self, tmp_path):
        """Should create context with all services."""
        vault = tmp_path / "vault"
        prompts = vault / "Prompts"
        prompts.mkdir(parents=True)

        config = Config(vault_path=vault, editor="vim")
        ctx = AppContext.create_default(config)

        assert ctx.config == config
        assert ctx.clipboard is not None
        assert ctx.editor is not None
        assert ctx.selector is not None
        assert ctx.console is not None
        assert ctx.repository is not None

    def test_context_uses_config_editor(self, tmp_path):
        """Editor service should use editor from config."""
        vault = tmp_path / "vault"
        prompts = vault / "Prompts"
        prompts.mkdir(parents=True)

        config = Config(vault_path=vault, editor="nvim")
        ctx = AppContext.create_default(config)

        assert ctx.editor.editor_command == "nvim"

    def test_context_uses_config_vault_path(self, tmp_path):
        """Repository should use vault_path from config."""
        vault = tmp_path / "vault"
        prompts = vault / "Prompts"
        prompts.mkdir(parents=True)

        config = Config(vault_path=vault, editor="vim")
        ctx = AppContext.create_default(config)

        assert ctx.repository.vault_path == vault
