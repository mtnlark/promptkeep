"""
Main CLI module for PromptKeep.

This module implements the command-line interface for PromptKeep, providing commands
for initializing a prompt vault, adding new prompts, and selecting existing prompts.
It uses Typer for CLI argument parsing and Rich for terminal output formatting.
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
    open_editor,
    sanitize_filename,
    validate_vault_path,
)

# Initialize the Typer app with a help message
app = typer.Typer(help="PromptKeep - A CLI tool for managing and accessing your AI prompts")
console = Console()


def create_prompt_template(prompts_dir: Path) -> None:
    """Create an example prompt file to demonstrate the expected format.
    
    This function creates a template file that shows users:
    - The required YAML front matter structure
    - How to format metadata (title, description, tags)
    - Where to place the actual prompt content
    
    Args:
        prompts_dir: Directory where the template should be created
    """
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
) -> None:
    """Initialize a new prompt vault.
    
    This command creates a directory structure for storing prompts:
    - Creates the main vault directory
    - Creates a 'Prompts' subdirectory
    - Adds an example prompt template
    
    If the directory already exists, it will be overwritten.
    
    Args:
        vault_path: Path where the vault should be created (defaults to ~/PromptVault)
    """
    # Expand user directory (~) and make path absolute
    expanded_path = Path(vault_path).expanduser().absolute()
    
    # Create the vault directory with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task(description="Creating prompt vault...", total=None)
        
        # Remove existing directory if it exists
        if expanded_path.exists():
            shutil.rmtree(expanded_path)
        
        # Create the vault directory and prompts subdirectory
        expanded_path.mkdir(parents=True, exist_ok=True)
        prompts_dir = expanded_path / "Prompts"
        prompts_dir.mkdir(exist_ok=True)
        
        # Create template prompt
        create_prompt_template(prompts_dir)

    # Show success message with next steps
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
    """Add a new prompt to your vault.
    
    This command:
    1. Creates a new markdown file with YAML front matter
    2. Opens your default editor to write the prompt content
    3. Saves the file with a unique name based on title and timestamp
    
    Args:
        title: The title of the prompt
        description: Optional description of the prompt
        tags: Optional list of tags for categorizing the prompt
        vault_path: Optional path to the prompt vault
        
    Raises:
        typer.Exit: If no vault exists or if user cancels the operation
    """
    # Validate vault path
    try:
        expanded_vault = validate_vault_path(vault_path)
    except typer.Exit:
        console.print(
            Panel.fit(
                "[yellow]No vault found. Would you like to create one?[/]\n"
                "Run 'promptkeep init' to create a new vault.",
                title="Warning",
                border_style="yellow",
            )
        )
        raise typer.Exit(1)
        
    prompts_dir = expanded_vault / "Prompts"

    # Process comma-separated tags if provided as a single string
    if len(tags) == 1 and "," in tags[0]:
        tags = [tag.strip() for tag in tags[0].split(",")]

    # Create filename from title and timestamp
    filename = sanitize_filename(title)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{filename}-{timestamp}.md"
    prompt_path = prompts_dir / filename

    # Check for existing similar prompts
    existing_files = list(prompts_dir.glob(f"{sanitize_filename(title)}-*.md"))
    if existing_files:
        console.print(
            Panel.fit(
                f"[yellow]Warning: Similar prompts already exist:[/]\n"
                f"{chr(10).join(f'- {f.name}' for f in existing_files)}",
                title="Warning",
                border_style="yellow",
            )
        )
        if not typer.confirm("Do you want to continue?"):
            raise typer.Exit(0)

    # Create the prompt template with YAML front matter
    yaml_tags = ", ".join([f'"{tag.strip()}"' for tag in tags])
    prompt_content = f"""---
title: "{title}"
description: "{description}"
tags: [{yaml_tags}]
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
    """Select a prompt and copy its content to clipboard.
    
    This command:
    1. Lists all available prompts in the vault
    2. Uses fzf for interactive selection
    3. Copies the selected prompt's content to clipboard
    
    Args:
        vault_path: Optional path to the prompt vault
        
    Raises:
        typer.Exit: If no prompts are found or if selection is cancelled
    """
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
        raise typer.Exit(1)

    # Use fzf to select a file
    try:
        selected_file = subprocess.check_output(
            [
                "fzf",
                "--prompt", "Select a prompt: ",
                "--preview", """awk '
                    BEGIN { in_yaml=0; printed_header=0 }
                    /^---$/ { in_yaml = !in_yaml; next }
                    in_yaml {
                        if ($1 == "title:") title = substr($0, 8)
                        if ($1 == "tags:") { tags=1; next }
                        if (tags && $1 == "-") tag_list = tag_list ", " substr($0, 3)
                    }
                    !in_yaml && !printed_header {
                        gsub(/"/, "", title)
                        sub(/, /, "", tag_list)
                        print "Title: " title
                        if (tag_list) print "Tags:  " tag_list
                        print "----------------------------------------"
                        printed_header=1
                        next
                    }
                    !in_yaml { print }
                ' {}"""
            ],
            input="\n".join(str(f) for f in prompt_files).encode(),
        ).decode().strip()
    except subprocess.CalledProcessError:
        # User cancelled the selection
        raise typer.Exit(0)
    except FileNotFoundError:
        console.print(
            Panel.fit(
                "[red]Error: fzf not found.[/]\n"
                "Please install fzf to use the pick command.",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    # Read and extract the prompt content
    content = Path(selected_file).read_text()
    prompt_content = extract_prompt_content(content)

    # Copy to clipboard
    copy_to_clipboard(prompt_content)
    console.print(
        Panel.fit(
            "✅ Prompt copied to clipboard",
            title="Success",
            border_style="green",
        )
    )


def main():
    """Entry point for the PromptKeep CLI application."""
    app()


if __name__ == "__main__":
    main() 