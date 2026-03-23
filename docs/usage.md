# Usage Guide

## Initialize a Vault

Create a vault to store your prompts:

```bash
promptkeep init
```

This creates `~/PromptVault` with a `Prompts` directory and an example file.

To use a different location:

```bash
promptkeep init ~/Documents/MyPrompts
```

## Add Prompts

### Interactive Mode

```bash
promptkeep add
```

You'll be prompted for a title, description, and tags. Your editor opens to write the prompt content.

### Command Line

```bash
promptkeep add --title "Code Review" --tag coding --tag review
```

### Prompt Format

Prompts are Markdown files with YAML front matter:

```markdown
---
title: "Code Review"
description: "Analyze code for issues and improvements"
tags: ["coding", "review"]
---

Review this code for:
1. Bugs and edge cases
2. Performance issues
3. Security vulnerabilities
4. Readability improvements

[PASTE CODE HERE]
```

## Find and Copy Prompts

```bash
promptkeep pick
```

This opens a fuzzy finder. Type to search, use arrow keys to navigate, press Enter to copy the selected prompt to your clipboard.

### Filter by Tag

```bash
promptkeep pick --tag coding
promptkeep pick --tag coding --tag python  # Must have both tags
```

## Edit Prompts

```bash
promptkeep edit
```

Select a prompt from the fuzzy finder to open it in your editor.

Filter by tag:

```bash
promptkeep edit --tag coding
```

## Use a Different Vault

Override the default vault for any command:

```bash
promptkeep pick --vault ~/Work/Prompts
```

Or set the environment variable:

```bash
export PROMPTKEEP_VAULT=~/Work/Prompts
```

## Tagging Strategies

Consistent tags make prompts easier to find. Consider organizing by:

| Category | Example Tags |
|----------|--------------|
| Task type | `coding`, `writing`, `research` |
| Domain | `python`, `sql`, `marketing` |
| Frequency | `daily`, `reference` |

Combine tags to narrow searches:

```bash
promptkeep pick --tag coding --tag python
```

## Tips

**Use placeholders** — Mark areas to fill in: `[CLIENT NAME]`, `[PASTE CODE]`

**Favorite prompts** — Tag frequently used prompts with `fav` for quick access:
```bash
promptkeep pick --tag fav
```

**Keyboard shortcuts in fzf**:

- `Ctrl+N` / `Ctrl+P` — Navigate up/down
- `Ctrl+C` / `Esc` — Cancel
- `Enter` — Select
