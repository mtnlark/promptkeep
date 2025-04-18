# PromptKeep Reference

This document provides detailed technical reference for PromptKeep's commands, parameters, data structures, file formats, and implementation details. For practical usage examples and workflows, see the [Usage Guide](usage.md).

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

#### Return Value

None. Displays a success panel on completion.

#### Side Effects

- Creates directory structure for the vault
- Removes existing content if the vault directory already exists
- Creates an example prompt file

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

#### Return Value

None. Displays a success panel on completion.

#### Side Effects

- Creates a new markdown file in the vault
- Opens the user's text editor
- May display warnings for similar existing prompts

### pick

Select a prompt and copy it to the clipboard.

```bash
promptkeep pick [OPTIONS]
```

#### Parameters

| Parameter     | Required | Type     | Default       | Description                     |
|---------------|----------|----------|---------------|---------------------------------|
| --vault, -v   | No       | string   | ~/PromptVault | Path to the prompt vault        |
| --tag, -t     | No       | string[] | -             | Filter prompts by tag           |
| --no-copy     | No       | flag     | -             | Don't copy to clipboard         |

#### Return Value

None. Displays a success panel on completion.

#### Side Effects

- Copies prompt content to the system clipboard
- Launches external `fzf` process for selection

### edit

Edit an existing prompt.

```bash
promptkeep edit [OPTIONS]
```

#### Parameters

| Parameter     | Required | Type     | Default       | Description                     |
|---------------|----------|----------|---------------|---------------------------------|
| --vault, -v   | No       | string   | ~/PromptVault | Path to the prompt vault        |
| --tag, -t     | No       | string[] | -             | Filter prompts by tag           |

#### Return Value

None. Displays a success panel on completion.

#### Side Effects

- Launches external `fzf` process for selection
- Opens the user's text editor

## Data Model

### Prompt Structure

Each prompt is represented as a Markdown file with YAML front matter:

```markdown
---
title: "Title of the prompt"
description: "Description of what the prompt does"
tags: ["tag1", "tag2"]
created: "2023-04-16 10:30:00"
---

The actual prompt content goes here.
```

#### YAML Fields

| Field       | Required | Type     | Description                                |
|-------------|----------|-----------|--------------------------------------------|
| title       | Yes      | string    | Title of the prompt                        |
| description | No       | string    | Description of what the prompt does        |
| tags        | No       | string[]  | Array of tags for categorization           |
| created     | Auto     | datetime  | Creation timestamp (added automatically)   |

### File System Structure

The prompt vault follows this structure:

```
VaultPath/
└── Prompts/
    ├── example-prompt.md
    ├── my-prompt-20230416-103000.md
    └── another-prompt-20230416-104500.md
```

### Filename Format

Prompt filenames are automatically generated using this pattern:

```
{sanitized-title}-{timestamp}.md
```

Where:
- `sanitized-title` is the lowercase title with spaces replaced by hyphens and invalid characters removed
- `timestamp` is in the format `YYYYMMDD-HHMMSS`

## Environment Variables

| Variable           | Purpose                              | Default   |
|--------------------|--------------------------------------|-----------|
| PROMPTKEEP_VAULT   | Default location for the prompt vault | ~/PromptVault |
| EDITOR             | Preferred text editor                | vim       |

## Exit Codes

| Code | Meaning                                    |
|------|-------------------------------------------|
| 0    | Command completed successfully           |
| 1    | General error (file not found, etc.)     |
| 2    | User canceled operation                  |

## Dependencies

### Core Dependencies

| Package    | Version | Purpose                        |
|------------|---------|--------------------------------|
| typer      | >=0.7.0 | Command line interface creation |
| rich       | >=13.0.0| Terminal output formatting      |
| pyperclip  | >=1.8.0 | Clipboard operations            |
| pyyaml     | >=6.0   | YAML frontmatter parsing        |

### External Dependencies

| Dependency | Purpose                               | Installation                   |
|------------|---------------------------------------|--------------------------------|
| fzf        | Fuzzy finding for prompt selection    | Varies by platform (see below) |

#### Installing fzf

- **macOS**: `brew install fzf`
- **Linux**: 
    - Ubuntu/Debian: `apt install fzf`
    - Fedora: `dnf install fzf`
- **Windows**: 
    - With Chocolatey: `choco install fzf`
    - With Scoop: `scoop install fzf`

## Error Handling

### Common Error Messages

| Error Message                    | Cause                          | Solution                        |
|----------------------------------|--------------------------------|---------------------------------|
| "Vault not found"                | Invalid vault path             | Check the vault path            |
| "No prompts found"               | Empty prompt vault             | Add some prompts first          |
| "No prompts found for tags: X"   | No matches for tag filter      | Check tag names                 |
| "Editor exited with non-zero code" | Editor failed to save         | Check if file was saved properly |
| "fzf not found"                  | fzf is not installed           | Install fzf (see Dependencies)  |

## Security Considerations

- Prompts are stored as plain text files and are not encrypted
- No network connectivity is required; all operations are local
- Consider vault location security if prompts contain sensitive information

## Limitations

- **Maximum file size:** No explicit limit (limited by system memory)
- **Title length:** No explicit limit
- **Description length:** No explicit limit
- **Tag length:** No explicit limit
- **Number of prompts:** No explicit limit (limited by filesystem)

## API Structure

PromptKeep is primarily a command-line tool, but its core functions are organized in modules:

| Module              | Purpose                                     |
|---------------------|---------------------------------------------|
| promptkeep.cli      | Command-line interface and commands         |
| promptkeep.utils    | Core utilities for file handling and clipboard |

