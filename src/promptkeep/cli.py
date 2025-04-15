"""
Main CLI module for PromptKeep
"""
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

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


def get_default_vault_path() -> Path:
    """Get the default vault path"""
    return Path("~/PromptVault").expanduser().absolute()


def find_vault_path() -> Optional[Path]:
    """Find the vault path by checking common locations"""
    # First, check environment variable
    env_path = os.environ.get("PROMPTKEEP_VAULT")
    if env_path:
        path = Path(env_path).expanduser().absolute()
        if path.exists() and (path / "Prompts").exists():
            return path

    # Check default location
    default_path = get_default_vault_path()
    if default_path.exists() and (default_path / "Prompts").exists():
        return default_path

    # No vault found
    return None


def open_editor(file_path: Path) -> None:
    """Open the user's preferred editor to edit the file"""
    editor = os.environ.get("EDITOR", "vim")
    try:
        subprocess.run([editor, str(file_path)], check=True)
    except subprocess.CalledProcessError:
        console.print(
            Panel.fit(
                f"[red]Error: Failed to open editor '{editor}'[/]\n"
                "Set the EDITOR environment variable to your preferred editor.",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)


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
    # Find the vault path
    if vault_path:
        expanded_vault = Path(vault_path).expanduser().absolute()
    else:
        expanded_vault = find_vault_path()

    if not expanded_vault:
        console.print(
            Panel.fit(
                "[red]Error: No vault found.[/]\n"
                "Use 'promptkeep init' to create a vault or specify a vault path with --vault.",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    prompts_dir = expanded_vault / "Prompts"
    if not prompts_dir.exists() or not prompts_dir.is_dir():
        console.print(
            Panel.fit(
                f"[red]Error: Prompts directory not found in {expanded_vault}.[/]\n"
                "Make sure this is a valid prompt vault.",
                title="Error",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    # Process comma-separated tags if provided as a single string
    if len(tags) == 1 and "," in tags[0]:
        tags = [tag.strip() for tag in tags[0].split(",")]

    # Create filename from title
    filename = title.lower().replace(" ", "-")
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
    open_editor(prompt_path)

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