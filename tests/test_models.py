"""Test suite for the Prompt domain model.

This module contains tests for the Prompt dataclass and its YAML parsing
capabilities. Tests verify:
- Parsing markdown with YAML front matter
- Handling various YAML tag formats (inline and block)
- Converting prompts back to markdown
- Proper YAML escaping for special characters
- Tag filtering functionality
"""
from promptkeep.models import Prompt


class TestPromptFromMarkdown:
    """Tests for Prompt.from_markdown() class method."""

    def test_parse_basic_prompt(self):
        """Test parsing a basic prompt from markdown with YAML front matter."""
        content = '''---
title: "Test Prompt"
description: "A test description"
tags: ["tag1", "tag2"]
---

This is the prompt content.'''

        prompt = Prompt.from_markdown(content)

        assert prompt.title == "Test Prompt"
        assert prompt.description == "A test description"
        assert prompt.tags == ["tag1", "tag2"]
        assert prompt.content == "This is the prompt content."

    def test_parse_block_style_tags(self):
        """Test parsing prompts with block-style YAML tags."""
        content = '''---
title: "Test Prompt"
description: "Description"
tags:
  - tag1
  - tag2
  - tag3
---

Content here.'''

        prompt = Prompt.from_markdown(content)

        assert prompt.tags == ["tag1", "tag2", "tag3"]

    def test_parse_empty_tags(self):
        """Test parsing prompt with empty tags list."""
        content = '''---
title: "No Tags"
description: ""
tags: []
---

Content without tags.'''

        prompt = Prompt.from_markdown(content)

        assert prompt.tags == []
        assert prompt.title == "No Tags"

    def test_parse_no_front_matter(self):
        """Test parsing content without YAML front matter."""
        content = "Just plain content without YAML."

        prompt = Prompt.from_markdown(content)

        assert prompt.title == ""
        assert prompt.description == ""
        assert prompt.tags == []
        assert prompt.content == "Just plain content without YAML."

    def test_parse_empty_front_matter(self):
        """Test parsing content with empty front matter."""
        content = '''---
---

Content after empty front matter.'''

        prompt = Prompt.from_markdown(content)

        assert prompt.title == ""
        assert prompt.tags == []
        assert prompt.content == "Content after empty front matter."

    def test_parse_multiline_content(self):
        """Test parsing prompt with multiline content."""
        content = '''---
title: "Multiline"
tags: []
---

First paragraph.

Second paragraph.

- List item 1
- List item 2'''

        prompt = Prompt.from_markdown(content)

        assert "First paragraph." in prompt.content
        assert "Second paragraph." in prompt.content
        assert "- List item 1" in prompt.content

    def test_parse_content_with_triple_dashes(self):
        """Test that --- in content doesn't break parsing."""
        content = '''---
title: "Has Dashes"
tags: []
---

Before dashes
---
After dashes'''

        prompt = Prompt.from_markdown(content)

        # The content should include everything after the front matter
        assert "Before dashes" in prompt.content
        assert "---" in prompt.content
        assert "After dashes" in prompt.content

    def test_parse_missing_optional_fields(self):
        """Test parsing when optional fields are missing."""
        content = '''---
title: "Only Title"
---

Content'''

        prompt = Prompt.from_markdown(content)

        assert prompt.title == "Only Title"
        assert prompt.description == ""
        assert prompt.tags == []

    def test_parse_special_characters_in_title(self):
        """Test parsing titles with special characters."""
        content = '''---
title: "Title with: colons and 'quotes'"
description: "Desc"
tags: []
---

Content'''

        prompt = Prompt.from_markdown(content)

        assert prompt.title == "Title with: colons and 'quotes'"


class TestPromptToMarkdown:
    """Tests for Prompt.to_markdown() method."""

    def test_basic_to_markdown(self):
        """Test converting prompt to markdown."""
        prompt = Prompt(
            title="Test Title",
            description="Test Description",
            tags=["tag1", "tag2"],
            content="Prompt content here."
        )

        markdown = prompt.to_markdown()

        assert "title:" in markdown
        assert "Test Title" in markdown
        assert "description:" in markdown
        assert "Test Description" in markdown
        assert "tags:" in markdown
        assert "tag1" in markdown
        assert "tag2" in markdown
        assert "Prompt content here." in markdown

    def test_to_markdown_escapes_yaml_special_chars(self):
        """Test that special characters in title/description are properly escaped."""
        prompt = Prompt(
            title='Title with "double quotes"',
            description="Description with: colon",
            tags=[],
            content="Content"
        )

        markdown = prompt.to_markdown()

        # Should be valid YAML - verify by reparsing
        reparsed = Prompt.from_markdown(markdown)
        assert reparsed.title == 'Title with "double quotes"'
        assert reparsed.description == "Description with: colon"

    def test_roundtrip_preserves_data(self):
        """Test that to_markdown -> from_markdown preserves all data."""
        original = Prompt(
            title="Original Title",
            description="Original Description",
            tags=["alpha", "beta", "gamma"],
            content="Original content with\nmultiple lines."
        )

        markdown = original.to_markdown()
        reparsed = Prompt.from_markdown(markdown)

        assert reparsed.title == original.title
        assert reparsed.description == original.description
        assert reparsed.tags == original.tags
        assert reparsed.content == original.content

    def test_empty_prompt_to_markdown(self):
        """Test converting empty prompt to markdown."""
        prompt = Prompt(
            title="",
            description="",
            tags=[],
            content=""
        )

        markdown = prompt.to_markdown()

        # Should still produce valid markdown with front matter
        assert "---" in markdown


class TestPromptHasTags:
    """Tests for Prompt.has_tags() method."""

    def test_has_single_tag(self):
        """Test checking for a single tag."""
        prompt = Prompt(
            title="Test",
            description="",
            tags=["python", "coding", "ai"],
            content=""
        )

        assert prompt.has_tags(["python"]) is True
        assert prompt.has_tags(["java"]) is False

    def test_has_multiple_tags(self):
        """Test checking for multiple tags (AND logic)."""
        prompt = Prompt(
            title="Test",
            description="",
            tags=["python", "coding", "ai"],
            content=""
        )

        assert prompt.has_tags(["python", "coding"]) is True
        assert prompt.has_tags(["python", "ai"]) is True
        assert prompt.has_tags(["python", "java"]) is False  # java not present

    def test_has_empty_tags_list(self):
        """Test that empty tags list returns True (no requirements)."""
        prompt = Prompt(
            title="Test",
            description="",
            tags=["python"],
            content=""
        )

        assert prompt.has_tags([]) is True

    def test_prompt_with_no_tags(self):
        """Test has_tags on prompt with no tags."""
        prompt = Prompt(
            title="Test",
            description="",
            tags=[],
            content=""
        )

        assert prompt.has_tags([]) is True
        assert prompt.has_tags(["any"]) is False


class TestPromptFilePath:
    """Tests for Prompt file_path property."""

    def test_file_path_default_none(self):
        """Test that file_path defaults to None."""
        prompt = Prompt(
            title="Test",
            description="",
            tags=[],
            content=""
        )

        assert prompt.file_path is None

    def test_file_path_preserved(self):
        """Test that file_path is preserved when set."""
        from pathlib import Path

        prompt = Prompt(
            title="Test",
            description="",
            tags=[],
            content="",
            file_path=Path("/some/path/prompt.md")
        )

        assert prompt.file_path == Path("/some/path/prompt.md")
