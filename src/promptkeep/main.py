#!/usr/bin/env python3
"""
Command-line entry point for PromptKeep
"""
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from promptkeep.cli import init_command, add_command

app = typer.Typer(
    help="PromptKeep - A CLI tool for managing and accessing your AI prompts",
    no_args_is_help=True,  # Show help when no arguments are provided
)
console = Console()


@app.callback()
def callback():
    """PromptKeep - A CLI tool for managing and accessing your AI prompts"""
    pass


# Add commands
app.command(name="init")(init_command)
app.command(name="add")(add_command)

# Add more commands here as they are implemented
# app.command(name="pick")(pick_command)


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main() 