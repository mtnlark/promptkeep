# Reference

Technical details for PromptKeep commands, configuration, and architecture.

## Commands

### init

Create a new prompt vault.

```bash
promptkeep init [PATH]
```

| Argument | Default | Description |
|----------|---------|-------------|
| `PATH` | `~/PromptVault` | Vault location |

!!! warning
    Overwrites existing vault at the specified path.

### add

Add a new prompt.

```bash
promptkeep add [OPTIONS]
```

| Option | Required | Description |
|--------|----------|-------------|
| `--title`, `-t` | Yes | Prompt title |
| `--description`, `-d` | No | Prompt description |
| `--tag` | No | Tag (repeatable) |
| `--vault`, `-v` | No | Vault path |

### pick

Select a prompt and copy to clipboard.

```bash
promptkeep pick [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--tag`, `-t` | Filter by tag (repeatable, AND logic) |
| `--vault`, `-v` | Vault path |

### edit

Edit an existing prompt.

```bash
promptkeep edit [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--tag`, `-t` | Filter by tag (repeatable, AND logic) |
| `--vault`, `-v` | Vault path |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROMPTKEEP_VAULT` | `~/PromptVault` | Default vault location |
| `EDITOR` | `vim` | Editor for prompt editing |

### Precedence

Configuration resolves in this order:

1. Command-line arguments (`--vault`)
2. Environment variables (`PROMPTKEEP_VAULT`)
3. Default values

## File Format

### Prompt Structure

```markdown
---
title: "Prompt Title"
description: "Optional description"
tags: ["tag1", "tag2"]
---

Prompt content goes here.
```

### Filename Format

```
{sanitized-title}-{YYYYMMDD-HHMMSS}.md
```

Example: `code-review-20240315-143022.md`

### Vault Structure

```
VaultPath/
└── Prompts/
    ├── example-prompt.md
    └── code-review-20240315-143022.md
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (vault not found, fzf not installed, etc.) |

## Architecture

PromptKeep uses dependency injection and protocol-based interfaces for testability.

### Modules

| Module | Purpose |
|--------|---------|
| `cli` | Command-line interface |
| `config` | Configuration management |
| `context` | Dependency injection container |
| `exceptions` | Custom exception hierarchy |
| `models` | Data models |
| `protocols` | Service interfaces |
| `repository` | Data access layer |
| `services` | External integrations (clipboard, editor, fzf) |
| `utils` | Utility functions |

### Exception Hierarchy

```
PromptKeepError
├── VaultNotFoundError
├── VaultInvalidError
├── EditorError
│   └── EditorNotFoundError
└── SelectorError
    └── SelectorNotFoundError
```

### Dependencies

| Package | Purpose |
|---------|---------|
| typer | CLI framework |
| rich | Terminal formatting |
| pyperclip | Clipboard access |
| pyyaml | YAML parsing |

External: **fzf** (fuzzy finder)
