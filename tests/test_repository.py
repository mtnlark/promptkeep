"""Test suite for the PromptRepository.

This module contains tests for the file-based prompt repository, verifying:
- Listing and filtering prompts
- Loading prompts from files
- Saving prompts to files
- Finding similar prompts
- Error handling for file operations
"""

import pytest

from promptkeep.models import Prompt
from promptkeep.repository import PromptRepository


class TestPromptRepositoryListAll:
    """Tests for PromptRepository.list_all() method."""

    def test_list_all_prompts(self, tmp_path):
        """Test listing all prompts in vault."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        # Create test prompts
        (prompts_dir / "test1.md").write_text('''---
title: "Test 1"
description: "First test"
tags: ["a"]
---
Content 1''')
        (prompts_dir / "test2.md").write_text('''---
title: "Test 2"
description: "Second test"
tags: ["b"]
---
Content 2''')

        repo = PromptRepository(vault)
        prompts = repo.list_all()

        assert len(prompts) == 2
        titles = [p.title for p in prompts]
        assert "Test 1" in titles
        assert "Test 2" in titles

    def test_list_all_empty_vault(self, tmp_path):
        """Test listing prompts in empty vault."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        repo = PromptRepository(vault)
        prompts = repo.list_all()

        assert len(prompts) == 0

    def test_list_all_sets_file_path(self, tmp_path):
        """Test that list_all sets file_path on each prompt."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        test_file = prompts_dir / "test.md"
        test_file.write_text('''---
title: "Test"
tags: []
---
Content''')

        repo = PromptRepository(vault)
        prompts = repo.list_all()

        assert len(prompts) == 1
        assert prompts[0].file_path == test_file


class TestPromptRepositoryFilterByTags:
    """Tests for PromptRepository.filter_by_tags() method."""

    def test_filter_single_tag(self, tmp_path):
        """Test filtering prompts by a single tag."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        (prompts_dir / "python.md").write_text('''---
title: "Python"
tags: ["python", "coding"]
---
Python prompt''')
        (prompts_dir / "java.md").write_text('''---
title: "Java"
tags: ["java", "coding"]
---
Java prompt''')

        repo = PromptRepository(vault)

        python_prompts = repo.filter_by_tags(["python"])
        assert len(python_prompts) == 1
        assert python_prompts[0].title == "Python"

    def test_filter_multiple_tags(self, tmp_path):
        """Test filtering prompts by multiple tags (AND logic)."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        (prompts_dir / "python-ai.md").write_text('''---
title: "Python AI"
tags: ["python", "ai"]
---
Content''')
        (prompts_dir / "python-web.md").write_text('''---
title: "Python Web"
tags: ["python", "web"]
---
Content''')

        repo = PromptRepository(vault)

        # Should only match prompt with BOTH tags
        ai_prompts = repo.filter_by_tags(["python", "ai"])
        assert len(ai_prompts) == 1
        assert ai_prompts[0].title == "Python AI"

    def test_filter_common_tag(self, tmp_path):
        """Test filtering prompts by a tag they share."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        (prompts_dir / "p1.md").write_text('''---
title: "Prompt 1"
tags: ["coding"]
---
Content''')
        (prompts_dir / "p2.md").write_text('''---
title: "Prompt 2"
tags: ["coding"]
---
Content''')

        repo = PromptRepository(vault)

        coding_prompts = repo.filter_by_tags(["coding"])
        assert len(coding_prompts) == 2

    def test_filter_no_matches(self, tmp_path):
        """Test filtering when no prompts match."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        (prompts_dir / "test.md").write_text('''---
title: "Test"
tags: ["python"]
---
Content''')

        repo = PromptRepository(vault)

        results = repo.filter_by_tags(["java"])
        assert len(results) == 0


class TestPromptRepositoryGetByPath:
    """Tests for PromptRepository.get_by_path() method."""

    def test_get_by_path(self, tmp_path):
        """Test retrieving prompt by file path."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        test_file = prompts_dir / "test.md"
        test_file.write_text('''---
title: "Test Prompt"
description: "Test description"
tags: ["test"]
---
Test content here.''')

        repo = PromptRepository(vault)
        prompt = repo.get_by_path(test_file)

        assert prompt.title == "Test Prompt"
        assert prompt.description == "Test description"
        assert prompt.tags == ["test"]
        assert prompt.content == "Test content here."
        assert prompt.file_path == test_file

    def test_get_by_path_nonexistent(self, tmp_path):
        """Test that getting nonexistent file raises FileNotFoundError."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        repo = PromptRepository(vault)

        with pytest.raises(FileNotFoundError):
            repo.get_by_path(prompts_dir / "nonexistent.md")


class TestPromptRepositoryGetFilePaths:
    """Tests for PromptRepository.get_file_paths() method."""

    def test_get_all_file_paths(self, tmp_path):
        """Test getting all file paths."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        (prompts_dir / "test1.md").write_text("---\ntitle: Test1\n---\nContent")
        (prompts_dir / "test2.md").write_text("---\ntitle: Test2\n---\nContent")

        repo = PromptRepository(vault)
        paths = repo.get_file_paths()

        assert len(paths) == 2
        names = [p.name for p in paths]
        assert "test1.md" in names
        assert "test2.md" in names

    def test_get_file_paths_with_tag_filter(self, tmp_path):
        """Test getting file paths filtered by tags."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        (prompts_dir / "python.md").write_text('''---
title: Python
tags: ["python"]
---
Content''')
        (prompts_dir / "java.md").write_text('''---
title: Java
tags: ["java"]
---
Content''')

        repo = PromptRepository(vault)
        paths = repo.get_file_paths(tags=["python"])

        assert len(paths) == 1
        assert paths[0].name == "python.md"

    def test_get_file_paths_empty_dir(self, tmp_path):
        """Test getting file paths from empty directory."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        repo = PromptRepository(vault)
        paths = repo.get_file_paths()

        assert len(paths) == 0


class TestPromptRepositorySave:
    """Tests for PromptRepository.save() method."""

    def test_save_new_prompt(self, tmp_path):
        """Test saving a new prompt."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        repo = PromptRepository(vault)
        prompt = Prompt(
            title="New Prompt",
            description="A new prompt",
            tags=["new", "test"],
            content="This is the content."
        )

        filepath = repo.save(prompt)

        assert filepath.exists()
        assert "new-prompt" in filepath.name
        assert filepath.suffix == ".md"

        # Verify content
        saved = repo.get_by_path(filepath)
        assert saved.title == "New Prompt"
        assert saved.description == "A new prompt"
        assert saved.tags == ["new", "test"]
        assert saved.content == "This is the content."

    def test_save_with_explicit_filename(self, tmp_path):
        """Test saving with explicit filename."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        repo = PromptRepository(vault)
        prompt = Prompt(
            title="Test",
            description="",
            tags=[],
            content="Content"
        )

        filepath = repo.save(prompt, filename="custom-name.md")

        assert filepath.name == "custom-name.md"
        assert filepath.exists()

    def test_save_generates_timestamped_filename(self, tmp_path):
        """Test that save generates filename with timestamp."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        repo = PromptRepository(vault)
        prompt = Prompt(
            title="Test Title",
            description="",
            tags=[],
            content="Content"
        )

        filepath = repo.save(prompt)

        # Should contain sanitized title and timestamp pattern
        assert "test-title" in filepath.name
        # Timestamp pattern: YYYYMMDD-HHMMSS
        import re
        assert re.search(r"\d{8}-\d{6}", filepath.name)


class TestPromptRepositoryExistsSimilar:
    """Tests for PromptRepository.exists_similar() method."""

    def test_exists_similar_found(self, tmp_path):
        """Test finding similar prompts."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        # Create existing prompt with similar name
        (prompts_dir / "my-prompt-20260101-120000.md").write_text(
            "---\ntitle: My Prompt\n---\nContent"
        )

        repo = PromptRepository(vault)
        similar = repo.exists_similar("My Prompt")

        assert len(similar) == 1
        assert "my-prompt" in similar[0].name

    def test_exists_similar_not_found(self, tmp_path):
        """Test when no similar prompts exist."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        (prompts_dir / "other-prompt-20260101-120000.md").write_text(
            "---\ntitle: Other\n---\nContent"
        )

        repo = PromptRepository(vault)
        similar = repo.exists_similar("My Unique Title")

        assert len(similar) == 0

    def test_exists_similar_multiple(self, tmp_path):
        """Test finding multiple similar prompts."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        (prompts_dir / "my-prompt-20260101-120000.md").write_text("Content")
        (prompts_dir / "my-prompt-20260102-120000.md").write_text("Content")
        (prompts_dir / "my-prompt-20260103-120000.md").write_text("Content")

        repo = PromptRepository(vault)
        similar = repo.exists_similar("My Prompt")

        assert len(similar) == 3


class TestPromptRepositoryErrorHandling:
    """Tests for repository error handling."""

    def test_list_all_skips_unreadable_files(self, tmp_path):
        """Test that list_all skips files that can't be read."""
        vault = tmp_path / "vault"
        prompts_dir = vault / "Prompts"
        prompts_dir.mkdir(parents=True)

        # Create one valid file
        (prompts_dir / "valid.md").write_text("---\ntitle: Valid\n---\nContent")

        # Create one file with invalid YAML
        (prompts_dir / "invalid.md").write_text("---\n[invalid yaml\n---\nContent")

        repo = PromptRepository(vault)
        prompts = repo.list_all()

        # Should get at least the valid one (invalid YAML is handled
        # gracefully by Prompt.from_markdown)
        assert len(prompts) >= 1
        titles = [p.title for p in prompts]
        assert "Valid" in titles
