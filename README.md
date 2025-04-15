# PromptKeep

A CLI tool for managing and accessing AI prompts, built with Python.

PromptKeep helps you organize, access, and reuse AI prompts through a simple command-line interface. It stores prompts as Markdown files with YAML metadata, making them easy to manage and version control.

## Features

- Store prompts in Markdown files with YAML front matter
- Fuzzy search for quick prompt retrieval
- Copy prompts directly to clipboard
- Local storage (no cloud dependencies)
- Tag-based organization
- Obsidian-compatible format

## Installation

```bash
git clone https://github.com/yourusername/promptkeep.git
cd promptkeep
pip install -e .
```

## Usage

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

## Technical Details

Built with:
- Python 3.8+
- Typer for CLI interface
- Rich for terminal output
- Pyperclip for clipboard operations

## License

MIT License - see [LICENSE](LICENSE) for details. 