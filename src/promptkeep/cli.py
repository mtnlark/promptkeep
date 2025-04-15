"""
Main CLI module for PromptKeep
"""
import os
import shutil
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

# Create the app with a callback
app = typer.Typer(help="PromptKeep - A CLI tool for managing and accessing your AI prompts")
console = Console()


def create_prompt_template(prompts_dir: Path) -> None:
    """Create a template prompt file to show users the format"""
    template_content = """---
title: "Example Prompt"
description: "A template showing the prompt format"
tags: ["template", "example"]
---

This is an example prompt. The text above the first '---' is YAML front matter that
contains metadata about your prompt. The text below is the actual prompt content.

You can use this template to create your own prompts. Just copy this file and
modify the YAML front matter and prompt content as needed.
"""
    template_path = prompts_dir / "example_prompt.md"
    template_path.write_text(template_content)


@app.command("init")
def init_command(
    vault_path: str = typer.Argument(
        "~/PromptVault",
        help="Path where your prompt vault will be created",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force creation even if directory exists",
    ),
) -> None:
    """Initialize a new prompt vault"""
    # Expand user directory (~) and make path absolute
    expanded_path = Path(vault_path).expanduser().absolute()
    
    # Check if directory exists
    if expanded_path.exists() and not force:
        console.print(
            Panel.fit(
                f"[red]Error: Directory {expanded_path} already exists.[/]\n"
                "Use --force to overwrite existing directory.",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    # Create the vault directory
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Creating prompt vault...", total=None)
        
        # Remove existing directory if force is True
        if expanded_path.exists() and force:
            shutil.rmtree(expanded_path)
        
        # Create the vault directory and prompts subdirectory
        expanded_path.mkdir(parents=True, exist_ok=True)
        prompts_dir = expanded_path / "Prompts"
        prompts_dir.mkdir(exist_ok=True)
        
        # Create template prompt
        create_prompt_template(prompts_dir)

    # Show success message
    console.print(
        Panel.fit(
            f"✅ Prompt vault created successfully at: [bold blue]{expanded_path}[/]\n\n"
            "Next steps:\n"
            "1. Add your prompts to the 'Prompts' directory\n"
            "2. Use 'promptkeep add' to create new prompts\n"
            "3. Use 'promptkeep pick' to select and copy prompts",
            title="Success",
            border_style="green",
        )
    )


# Add more commands here later
# @app.command("add")
# def add_command():
#     """Add a new prompt"""
#     pass
#
# @app.command("pick")
# def pick_command():
#     """Pick a prompt and copy it to clipboard"""
#     pass


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main() 