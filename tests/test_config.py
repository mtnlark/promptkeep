"""Tests for configuration management."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from promptkeep.config import Config
from promptkeep.exceptions import VaultInvalidError, VaultNotFoundError


class TestConfigCreation:
    """Tests for Config dataclass."""

    def test_config_is_immutable(self):
        """Config should be frozen (immutable)."""
        config = Config(vault_path=Path("/test"), editor="vim")
        with pytest.raises(AttributeError):
            config.vault_path = Path("/other")

    def test_prompts_dir_property(self):
        """prompts_dir should return vault_path / Prompts."""
        config = Config(vault_path=Path("/test/vault"), editor="vim")
        assert config.prompts_dir == Path("/test/vault/Prompts")

    def test_custom_prompts_dir_name(self):
        """Should support custom prompts directory name."""
        config = Config(
            vault_path=Path("/test"),
            editor="vim",
            prompts_dir_name="MyPrompts",
        )
        assert config.prompts_dir == Path("/test/MyPrompts")


class TestConfigFromEnvironment:
    """Tests for Config.from_environment()."""

    def test_uses_default_vault_path(self):
        """Should use ~/PromptVault when no override or env var."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config.from_environment()
            assert config.vault_path == Path.home() / "PromptVault"

    def test_vault_override_takes_precedence(self):
        """Explicit vault_override should override env var."""
        with patch.dict(os.environ, {"PROMPTKEEP_VAULT": "/env/vault"}):
            config = Config.from_environment(vault_override="/override/vault")
            assert config.vault_path == Path("/override/vault").absolute()

    def test_env_var_used_when_no_override(self):
        """PROMPTKEEP_VAULT env var should be used when no override."""
        with patch.dict(os.environ, {"PROMPTKEEP_VAULT": "/env/vault"}, clear=True):
            config = Config.from_environment()
            assert config.vault_path == Path("/env/vault").absolute()

    def test_expands_user_in_vault_path(self):
        """Should expand ~ in vault path."""
        config = Config.from_environment(vault_override="~/my-vault")
        assert config.vault_path == Path.home() / "my-vault"

    def test_uses_default_editor(self):
        """Should use vim when no EDITOR env var."""
        env_without_editor = {k: v for k, v in os.environ.items() if k != "EDITOR"}
        with patch.dict(os.environ, env_without_editor, clear=True):
            config = Config.from_environment()
            assert config.editor == "vim"

    def test_uses_editor_env_var(self):
        """Should use EDITOR env var when set."""
        with patch.dict(os.environ, {"EDITOR": "nvim"}):
            config = Config.from_environment()
            assert config.editor == "nvim"

    def test_editor_override_takes_precedence(self):
        """Explicit editor_override should override env var."""
        with patch.dict(os.environ, {"EDITOR": "nvim"}):
            config = Config.from_environment(editor_override="code")
            assert config.editor == "code"


class TestConfigValidateVault:
    """Tests for Config.validate_vault()."""

    def test_raises_not_found_when_vault_missing(self, tmp_path):
        """Should raise VaultNotFoundError when vault doesn't exist."""
        config = Config(vault_path=tmp_path / "nonexistent", editor="vim")
        with pytest.raises(VaultNotFoundError) as exc_info:
            config.validate_vault()
        assert config.vault_path in exc_info.value.searched_paths

    def test_raises_invalid_when_prompts_dir_missing(self, tmp_path):
        """Should raise VaultInvalidError when Prompts dir is missing."""
        vault = tmp_path / "vault"
        vault.mkdir()
        config = Config(vault_path=vault, editor="vim")
        with pytest.raises(VaultInvalidError) as exc_info:
            config.validate_vault()
        assert exc_info.value.vault_path == vault

    def test_succeeds_when_vault_valid(self, tmp_path):
        """Should not raise when vault is valid."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)
        config = Config(vault_path=vault, editor="vim")
        config.validate_vault()  # Should not raise
