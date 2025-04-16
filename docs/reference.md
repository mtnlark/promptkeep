# PromptKeep Reference

This document provides detailed technical reference for all PromptKeep commands, parameters, data structures, and file formats.

## Command Reference

### Global Options

These options are available for all commands:

```
--help          Show help message and exit
--vault PATH    Path to the prompt vault (defaults to ~/PromptVault or PROMPTKEEP_VAULT env var)
```

### init

Initializes a new prompt vault.

```bash
promptkeep init [PATH]
```

#### Parameters

| Parameter | Required | Type   | Default        | Description                    |
|-----------|----------|--------|----------------|--------------------------------|
| path      | No       | string | ~/PromptVault  | Location for the prompt vault  |

#### Example

```bash
promptkeep init ~/my_prompts
```

### add

Adds a new prompt to your vault.

```bash
promptkeep add [OPTIONS]
```

#### Parameters

| Parameter          | Required | Type     | Default | Description                       |
|--------------------|----------|----------|---------|-----------------------------------|
| --title, -t        | Yes      | string   | -       | Title of the prompt               |
| --description, -d  | No       | string   | -       | Description of the prompt         |
| --tag              | No       | string[] | -       | Tags for the prompt (can specify multiple) |
| --vault, -v        | No       | string   | ~/PromptVault | Path to the prompt vault   |

#### Example

```bash
promptkeep add --title "Code Review" --tag "programming" --tag "review"
```

### pick

Select a prompt and copy it to the clipboard.

```bash
promptkeep pick [OPTIONS]
```

#### Parameters

| Parameter     | Required | Type    | Default       | Description                     |
|---------------|----------|---------|---------------|---------------------------------|
| --vault, -v   | No       | string  | ~/PromptVault | Path to the prompt vault        |
| --no-copy     | No       | flag    | -             | Don't copy to clipboard         |

#### Example

```bash
promptkeep pick
```

### edit

Edit an existing prompt.

```bash
promptkeep edit [OPTIONS]
```

#### Parameters

| Parameter     | Required | Type     | Default       | Description                     |
|---------------|----------|----------|---------------|---------------------------------|
| --vault, -v   | No       | string   | ~/PromptVault | Path to the prompt vault        |
| --tags        | No       | string[] | -             | Filter by tags                  |

#### Example

```bash
promptkeep edit --tags "programming"
```

## Data Storage

### Prompt File Format

Prompts are stored as Markdown files with YAML front matter using the following format:

```markdown
---
title: Code Review Assistance
description: Prompt for getting help with code reviews
date: 2023-04-16
tags:
  - programming
  - review
---

Please review the following code and provide feedback on:
1. Code quality
2. Potential bugs
3. Performance issues
4. Security concerns

[code]
```

### File Locations

| File        | Location        | Purpose              |
|-------------|-----------------|----------------------|
| *.md        | Prompt vault    | Individual prompts   |
| .vault-id   | Prompt vault    | Vault identification |

## Error Handling

### Common Error Messages

| Error Message                    | Cause                          | Solution                        |
|----------------------------------|--------------------------------|---------------------------------|
| "Vault not found"                | Invalid vault path             | Check the vault path            |
| "No prompts found"               | Empty prompt vault             | Add some prompts first          |
| "No prompts found for tags: X"   | No matches for tag filter      | Check tag names                 |
| "Editor exited with non-zero code" | Editor failed to save         | Check if file was saved properly |

## Dependencies

* `typer`: Command line interface creation
* `rich`: Terminal output formatting
* `pyperclip`: Clipboard operations
* `pyyaml`: YAML frontmatter parsing
* `fzf`: Fuzzy searching (external dependency)

## Environment Variables

| Variable           | Purpose                              |
|--------------------|--------------------------------------|
| PROMPTKEEP_VAULT   | Default location for the prompt vault |
| EDITOR             | Preferred text editor                |

## Limitations

* Maximum file size: No explicit limit (limited by system memory)
* Title length: No explicit limit
* Description length: No explicit limit
* Tag length: No explicit limit
* Number of prompts: No explicit limit

