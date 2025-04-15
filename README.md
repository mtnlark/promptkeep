# PromptKeep

A CLI tool for managing and accessing your AI prompts. Built with Python and designed to work with Obsidian.

## Features

- 🚀 Simple CLI interface for managing prompts
- 📝 Store prompts in Markdown files with YAML front matter
- 🔍 Quick access to your prompts
- 📋 Copy prompts to clipboard with a single command
- 🔒 Privacy-first: All data stored locally

## Installation

```bash
# Install using pip
pip install promptkeep

# Or install from source
git clone https://github.com/yourusername/promptkeep.git
cd promptkeep
pip install -e .
```

## Quick Start

1. Initialize your prompt vault:
```bash
promptkeep init ~/PromptVault
```

2. Start adding and managing your prompts!

## Development

This project uses:
- Python 3.8+
- Typer for CLI interface
- Rich for beautiful terminal output
- Pyperclip for clipboard operations

## License

MIT License - See LICENSE file for details 