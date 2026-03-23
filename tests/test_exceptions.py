"""Tests for custom exception hierarchy."""

from pathlib import Path

from promptkeep.exceptions import (
    EditorError,
    EditorNotFoundError,
    PromptKeepError,
    SelectorError,
    SelectorNotFoundError,
    VaultInvalidError,
    VaultNotFoundError,
)


class TestExceptionHierarchy:
    """Test that exceptions inherit correctly."""

    def test_vault_not_found_is_promptkeep_error(self):
        assert issubclass(VaultNotFoundError, PromptKeepError)

    def test_vault_invalid_is_promptkeep_error(self):
        assert issubclass(VaultInvalidError, PromptKeepError)

    def test_editor_error_is_promptkeep_error(self):
        assert issubclass(EditorError, PromptKeepError)

    def test_editor_not_found_is_editor_error(self):
        assert issubclass(EditorNotFoundError, EditorError)

    def test_selector_error_is_promptkeep_error(self):
        assert issubclass(SelectorError, PromptKeepError)

    def test_selector_not_found_is_selector_error(self):
        assert issubclass(SelectorNotFoundError, SelectorError)


class TestVaultNotFoundError:
    def test_stores_searched_paths(self):
        paths = [Path("/path/one"), Path("/path/two")]
        err = VaultNotFoundError(paths)
        assert err.searched_paths == paths

    def test_default_empty_paths(self):
        err = VaultNotFoundError()
        assert err.searched_paths == []

    def test_message(self):
        err = VaultNotFoundError()
        assert "vault" in str(err).lower()


class TestVaultInvalidError:
    def test_stores_vault_path(self):
        path = Path("/invalid/vault")
        err = VaultInvalidError(path)
        assert err.vault_path == path

    def test_message_includes_path(self):
        path = Path("/invalid/vault")
        err = VaultInvalidError(path)
        assert str(path) in str(err)


class TestEditorNotFoundError:
    def test_stores_editor_name(self):
        err = EditorNotFoundError("nvim")
        assert err.editor == "nvim"

    def test_message_includes_editor(self):
        err = EditorNotFoundError("nvim")
        assert "nvim" in str(err)


class TestSelectorNotFoundError:
    def test_message_mentions_fzf(self):
        err = SelectorNotFoundError()
        assert "fzf" in str(err).lower()
