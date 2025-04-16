#!/usr/bin/env python
"""Generates Markdown documentation for the PromptKeep CLI commands."""

import subprocess
import sys
from pathlib import Path

# Ensure the script is run from the project root
PROJECT_ROOT = Path(__file__).parent.parent
if Path.cwd() != PROJECT_ROOT:
    print(f"Error: Please run this script from the project root: {PROJECT_ROOT}")
    sys.exit(1)

OUTPUT_FILE = PROJECT_ROOT / "docs" / "reference.md"
COMMAND_BASE = [sys.executable, "-m", "promptkeep.cli"]

# Define the commands to document (add new commands here)
COMMANDS_TO_DOC = ["init", "add", "pick", "edit"]


def run_command(args: list[str]) -> str:
    """Runs a command and returns its stdout."""
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True, cwd=PROJECT_ROOT)
        return result.stdout
    except FileNotFoundError:
        print(f"Error: Command not found. Is Python environment ({sys.executable}) correct?")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(args)}")
        print(f"Stderr:\n{e.stderr}")
        sys.exit(1)


def format_help_text(command_name: str | None, help_text: str) -> str:
    """Formats the raw help text into Markdown."""
    title = f"`promptkeep{f' {command_name}' if command_name else ''}`"
    header = f"## {title}\n\n"
    # Simple formatting: wrap in code block
    return f"{header}```text\n{help_text.strip()}\n```\n\n"


def main():
    """Generates the reference documentation."""
    print(f"Generating reference documentation to {OUTPUT_FILE}...")
    content = ["# Command Reference\n\n"]
    content.append("This page provides the command-line help text for PromptKeep.\n\n")

    # Get help for the main command
    print("Getting help for main command...")
    main_help = run_command(COMMAND_BASE + ["--help"])
    content.append(format_help_text(None, main_help))

    # Get help for subcommands
    for cmd in COMMANDS_TO_DOC:
        print(f"Getting help for subcommand: {cmd}...")
        cmd_help = run_command(COMMAND_BASE + [cmd, "--help"])
        content.append(format_help_text(cmd, cmd_help))

    # Write the content to the output file
    OUTPUT_FILE.write_text("".join(content))
    print("Reference documentation generated successfully.")


if __name__ == "__main__":
    main() 