# PromptKeep

A CLI tool for managing and accessing AI prompts, built with Python.

PromptKeep helps you organize, access, and reuse your AI prompts through a simple command-line interface. It stores prompts as Markdown files with YAML metadata, making them easy to manage and version control, and lets you quickly find stored prompts and copy them to your clipboard.

## Features

- Store prompts in Markdown files with YAML front matter
- Fuzzy search for quick prompt retrieval
- Copy prompts directly to clipboard
- Local storage (no cloud dependencies)
- Tag-based organization
- Obsidian-compatible format

## Installation

```bash
git clone https://github.com/mtnlark/promptkeep.git
cd promptkeep
pip install .
```

## Usage Basics

1. Initialize a prompt vault:
```bash
promptkeep init ~/PromptVault
```

2. Add a new prompt:
```bash
promptkeep add --title "Code Review Assistance"
```

3. Select and copy a prompt:
```bash
promptkeep pick
```

4. Edit an existing prompt:
```bash
promptkeep edit
```

## Technical Details

Built with:

- Python 3.8+
- Typer for CLI interface
- Rich for terminal output
- Pyperclip for clipboard operations

## License

MIT License
