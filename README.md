# PromptKeep

A CLI tool for managing and accessing AI prompts, built with Python.

PromptKeep helps you organize, access, and reuse AI prompts through a simple command-line interface. It stores prompts as Markdown files with YAML metadata, making them easy to manage and version control.

Detailed docs: [promptkeep.levcraig.com](https://promptkeep.levcraig.com/)

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

## Architecture

PromptKeep follows clean architecture principles with clear separation of concerns:

```
promptkeep/
├── cli.py          # Command-line interface
├── config.py       # Configuration management
├── context.py      # Dependency injection container
├── exceptions.py   # Custom exception hierarchy
├── models.py       # Data models (Prompt)
├── protocols.py    # Service interfaces
├── repository.py   # Data access layer
├── services.py     # External service integrations
└── utils.py        # Pure utility functions
```

**Key patterns:**
- **Dependency Injection** via `AppContext` composition root
- **Protocol-based interfaces** for testability
- **Repository pattern** for data access
- **Custom exception hierarchy** for clear error handling

## Technical Details

Built with:
- Python 3.8+
- Typer for CLI interface
- Rich for terminal output
- Pyperclip for clipboard operations

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=promptkeep
```

## License

MIT License - see [LICENSE](LICENSE) for details. 
