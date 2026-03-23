"""Test suite for utility functions."""
from promptkeep.utils import extract_prompt_content, sanitize_filename


class TestExtractPromptContent:
    """Tests for extract_prompt_content() function."""

    def test_extracts_content_with_front_matter(self):
        """Test extracting content from file with YAML front matter."""
        content = """---
title: "Test"
tags: ["tag1"]
---

This is the actual prompt content.
It spans multiple lines."""

        result = extract_prompt_content(content)

        assert "This is the actual prompt content." in result
        assert "It spans multiple lines." in result
        assert "title" not in result

    def test_returns_content_without_front_matter(self):
        """Test extracting content from file without front matter."""
        content = "Just plain text without YAML."

        result = extract_prompt_content(content)

        assert result == "Just plain text without YAML."

    def test_handles_empty_content(self):
        """Test extracting from empty content."""
        result = extract_prompt_content("")
        assert result == ""

    def test_handles_content_with_multiple_dashes(self):
        """Test that --- in content doesn't break extraction."""
        content = """---
title: "Test"
---

First line
---
After dashes"""

        result = extract_prompt_content(content)

        # Should include content after the front matter
        assert "First line" in result


class TestSanitizeFilename:
    """Tests for sanitize_filename() function."""

    def test_basic_sanitization(self):
        """Test basic filename sanitization."""
        assert sanitize_filename("Hello World") == "hello-world"

    def test_removes_special_characters(self):
        """Test that special characters are removed."""
        result = sanitize_filename("Test: A/B\\C?*")
        assert "/" not in result
        assert "\\" not in result
        assert "?" not in result
        assert "*" not in result

    def test_truncates_long_names(self):
        """Test that very long names are truncated."""
        long_title = "a" * 200
        result = sanitize_filename(long_title)
        assert len(result) <= 100

    def test_removes_consecutive_hyphens(self):
        """Test that consecutive hyphens are collapsed."""
        result = sanitize_filename("test - - - name")
        assert "---" not in result

    def test_handles_empty_string(self):
        """Test handling of empty string."""
        result = sanitize_filename("")
        assert result == ""

    def test_handles_unicode(self):
        """Test handling of unicode characters."""
        result = sanitize_filename("Café Prompt")
        # Unicode characters should be preserved
        assert "caf" in result.lower()
