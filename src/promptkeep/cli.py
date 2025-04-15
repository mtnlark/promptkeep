"""
Main CLI module for PromptKeep
"""
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from promptkeep.utils import (
    copy_to_clipboard,
    extract_prompt_content,
    get_default_vault_path,
    open_editor,
    sanitize_filename,
    validate_vault_path,
)

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


@app.command("add")
def add_command(
    title: str = typer.Option(
        ...,
        "--title", "-t",
        help="Title of the prompt",
        prompt="Enter a title for your prompt",
    ),
    description: str = typer.Option(
        "",
        "--description", "-d",
        help="Description of the prompt",
        prompt="Enter a description (optional)",
    ),
    tags: List[str] = typer.Option(
        [],
        "--tag",
        help="Tags for the prompt (can be specified multiple times)",
        prompt="Enter tags separated by commas (optional)",
    ),
    vault_path: Optional[str] = typer.Option(
        None,
        "--vault", "-v",
        help="Path to the prompt vault (defaults to ~/PromptVault or PROMPTKEEP_VAULT env var)",
    ),
) -> None:
    """Add a new prompt to your vault"""
    # Validate vault path
    expanded_vault = validate_vault_path(vault_path)
    prompts_dir = expanded_vault / "Prompts"

    # Process comma-separated tags if provided as a single string
    if len(tags) == 1 and "," in tags[0]:
        tags = [tag.strip() for tag in tags[0].split(",")]

    # Create filename from title
    filename = sanitize_filename(title.lower().replace(" ", "-"))
    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{filename}-{timestamp}.md"
    prompt_path = prompts_dir / filename

    # Create the prompt template
    yaml_tags = ", ".join([f'"{tag}"' for tag in tags])
    prompt_content = f"""---
title: "{title}"
description: "{description}"
tags: [{yaml_tags}]
created: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
---

"""

    # Write the template to the file
    prompt_path.write_text(prompt_content)

    # Open the editor for the user to edit the content
    console.print(
        Panel.fit(
            f"Opening editor for you to write your prompt content.\n"
            f"File will be saved at: [bold blue]{prompt_path}[/]",
            title="Creating Prompt",
            border_style="blue",
        )
    )
    
    if not open_editor(prompt_path):
        # If editor failed to open, remove the file
        prompt_path.unlink()
        raise typer.Exit(1)

    # Check if file still exists (user might have deleted it)
    if prompt_path.exists():
        console.print(
            Panel.fit(
                f"✅ Prompt created successfully at: [bold blue]{prompt_path}[/]",
                title="Success",
                border_style="green",
            )
        )
    else:
        console.print(
            Panel.fit(
                "[yellow]Note: Prompt file was not saved.[/]",
                title="Warning",
                border_style="yellow",
            )
        )


@app.command("pick")
def pick_command(
    vault_path: Optional[str] = typer.Option(
        None,
        "--vault", "-v",
        help="Path to the prompt vault (defaults to ~/PromptVault or PROMPTKEEP_VAULT env var)",
    ),
) -> None:
    """Pick a prompt and copy its content to clipboard"""
    # Validate vault path
    expanded_vault = validate_vault_path(vault_path)
    prompts_dir = expanded_vault / "Prompts"

    # Get all markdown files
    prompt_files = list(prompts_dir.glob("*.md"))
    if not prompt_files:
        console.print(
            Panel.fit(
                "[yellow]No prompts found in the vault.[/]\n"
                "Use 'promptkeep add' to create a new prompt.",
                title="Warning",
                border_style="yellow",
            )
        )
        raise typer.Exit(0)

    # Use fzf to let user select a file
    try:
        selected_file = subprocess.check_output(
            ["fzf", "--prompt", "Select a prompt: "],
            input="\n".join(str(f) for f in prompt_files).encode(),
        ).decode().strip()
    except subprocess.CalledProcessError:
        # User pressed Ctrl+C or Esc
        raise typer.Exit(0)
    except FileNotFoundError:
        console.print(
            Panel.fit(
                "[red]Error: fzf not found.[/]\n"
                "Please install fzf to use the pick command:\n"
                "  - macOS: brew install fzf\n"
                "  - Linux: use your package manager",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    if not selected_file:
        # User didn't select anything
        raise typer.Exit(0)

    # Read and process the selected file
    try:
        content = Path(selected_file).read_text()
        prompt_content = extract_prompt_content(content)
        copy_to_clipboard(prompt_content)
        console.print(
            Panel.fit(
                "✅ Prompt copied to clipboard!",
                title="Success",
                border_style="green",
            )
        )
    except Exception as e:
        console.print(
            Panel.fit(
                f"[red]Error: Failed to process prompt: {str(e)}[/]",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


def main():
    """Entry point for the CLI"""
    app()


if __name__ == "__main__":
    main() 