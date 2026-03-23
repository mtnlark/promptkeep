# PromptKeep

A command-line tool for managing reusable AI prompts.

PromptKeep stores prompts as Markdown files with YAML metadata, letting you organize, search, and copy them to your clipboard with a single command.

## Quick Start

```bash
# Install
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

## Why PromptKeep?

- **Fast access**: Fuzzy search finds prompts instantly
- **Organized**: Tag-based filtering keeps prompts manageable
- **Portable**: Plain Markdown files work anywhere
- **Private**: Local storage, no cloud dependencies
- **Compatible**: Works with Obsidian and other Markdown tools

## Next Steps

- [Installation](installation.md) — Prerequisites and setup options
- [Usage Guide](usage.md) — Commands and workflows
- [Reference](reference.md) — Technical details and configuration
