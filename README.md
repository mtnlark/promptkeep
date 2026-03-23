# PromptKeep

A command-line tool for managing reusable AI prompts.

Store prompts as Markdown files, search with fuzzy finding, and copy to clipboard instantly.

**Documentation:** [promptkeep.levcraig.com](https://promptkeep.levcraig.com/)

## Features

- Fuzzy search for instant prompt retrieval
- Tag-based organization and filtering
- Plain Markdown files (Obsidian-compatible)
- Local storage — no cloud dependencies

## Quick Start

```bash
# Install (requires Python 3.8+ and fzf)
git clone https://github.com/mtnlark/promptkeep.git
cd promptkeep
pip install .

# Create a vault
promptkeep init

# Add a prompt
promptkeep add --title "Code Review"

# Find and copy a prompt
promptkeep pick
```

## Commands

| Command | Description |
|---------|-------------|
| `init [path]` | Create a prompt vault |
| `add` | Add a new prompt |
| `pick` | Select and copy a prompt |
| `edit` | Edit an existing prompt |

Use `--tag` with `pick` or `edit` to filter by tags.

## Architecture

```
promptkeep/
├── cli.py          # Command interface
├── config.py       # Configuration management
├── context.py      # Dependency injection
├── exceptions.py   # Error handling
├── models.py       # Data models
├── protocols.py    # Service interfaces
├── repository.py   # Data access
├── services.py     # External integrations
└── utils.py        # Utilities
```

## Development

```bash
pip install -e ".[dev]"
pytest --cov=promptkeep
```

## License

MIT
