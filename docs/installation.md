# Installation

## Prerequisites

- **Python 3.8+**
- **fzf** — fuzzy finder for prompt selection

### Installing fzf

=== "macOS"
    ```bash
    brew install fzf
    ```

=== "Ubuntu/Debian"
    ```bash
    sudo apt install fzf
    ```

=== "Fedora"
    ```bash
    sudo dnf install fzf
    ```

=== "Windows"
    ```bash
    # With Chocolatey
    choco install fzf

    # With Scoop
    scoop install fzf
    ```

## Install PromptKeep

```bash
git clone https://github.com/mtnlark/promptkeep.git
cd promptkeep
pip install .
```

### Using a Virtual Environment (Recommended)

```bash
git clone https://github.com/mtnlark/promptkeep.git
cd promptkeep
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install .
```

## Verify Installation

```bash
promptkeep --help
```

You should see the available commands listed.

## Configuration

PromptKeep uses two environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `PROMPTKEEP_VAULT` | Vault location | `~/PromptVault` |
| `EDITOR` | Text editor for editing prompts | `vim` |

Set these in your shell profile (`.bashrc`, `.zshrc`, etc.):

```bash
export PROMPTKEEP_VAULT=~/Documents/Prompts
export EDITOR=code  # or vim, nano, etc.
```

## Troubleshooting

**"fzf not found"**
: Install fzf using the instructions above, then ensure it's in your PATH.

**"command not found: promptkeep"**
: If using a virtual environment, make sure it's activated. Otherwise, check that your Python scripts directory is in your PATH.

**Editor doesn't open**
: Set the `EDITOR` environment variable to your preferred editor.
