"""
Main CLI module for PromptKeep.

This module implements the command-line interface for PromptKeep, providing commands
for initializing a prompt vault, adding new prompts, and selecting existing prompts.
It uses Typer for CLI argument parsing and Rich for terminal output formatting.
"""

import shutil
from functools import wraps
from pathlib import Path
from typing import Any, Callable, List, Optional, TypeVar

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from promptkeep.config import Config
from promptkeep.constants import DEFAULT_VAULT_PATH, PROMPTS_DIR_NAME
from promptkeep.context import AppContext
from promptkeep.exceptions import (
    EditorError,
    EditorNotFoundError,
    PromptKeepError,
    SelectorNotFoundError,
    VaultInvalidError,
    VaultNotFoundError,
)
from promptkeep.models import Prompt
from promptkeep.utils import extract_prompt_content

# Initialize the Typer app with a help message
app = typer.Typer(
    help="PromptKeep - A CLI tool for managing and accessing your AI prompts"
)
console = Console()

F = TypeVar("F", bound=Callable[..., None])


def handle_errors(func: F) -> F:
    """Decorator to convert PromptKeepError to user-friendly CLI output."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        try:
            return func(*args, **kwargs)
        except VaultNotFoundError:
            console.print(
                Panel.fit(
                    "[red]Error: No vault found.[/]\n"
                    "Use 'promptkeep init' to create a vault or specify --vault.",
                    title="Error",
                    border_style="red",
                )
            )
            raise typer.Exit(1) from None
        except VaultInvalidError as e:
            console.print(
                Panel.fit(
                    f"[red]Error: Invalid vault at {e.vault_path}[/]\n"
                    "Make sure this is a valid prompt vault with a Prompts directory.",
                    title="Error",
                    border_style="red",
                )
            )
            raise typer.Exit(1) from None
        except EditorNotFoundError as e:
            console.print(
                Panel.fit(
                    f"[red]Error: Editor '{e.editor}' not found.[/]\n"
                    "Please set the EDITOR environment variable to your preferred editor.",
                    title="Error",
                    border_style="red",
                )
            )
            raise typer.Exit(1) from None
        except EditorError as e:
            console.print(
                Panel.fit(
                    f"[red]Error: {e}[/]",
                    title="Error",
                    border_style="red",
                )
            )
            raise typer.Exit(1) from None
        except SelectorNotFoundError:
            console.print(
                Panel.fit(
                    "[red]Error: fzf not found.[/]\n"
                    "Please install fzf to use this command.",
                    title="Error",
                    border_style="red",
                )
            )
            raise typer.Exit(1) from None

    return wrapper  # type: ignore[return-value]


def get_context(vault_path: Optional[str] = None, *, validate: bool = True) -> AppContext:
    """Get or create AppContext with optional vault override.

    Args:
        vault_path: Optional path to vault directory
        validate: If True, validates that the vault exists and is properly structured.
                  Raises VaultNotFoundError or VaultInvalidError if invalid.
    """
    config = Config.from_environment(vault_override=vault_path)
    if validate:
        config.validate_vault()
    return AppContext.create_default(config)


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
        DEFAULT_VAULT_PATH,
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
        prompts_dir = expanded_path / PROMPTS_DIR_NAME
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
            "3. Use 'promptkeep pick' to select and copy prompts\n"
            "4. Use 'promptkeep edit' to modify existing prompts\n"
            "5. Use the --tag option with pick/edit to filter by tags",
            title="Success",
            border_style="green",
        )
    )


@app.command("add")
@handle_errors
def add_command(
    title: str = typer.Option(
        ...,
        "--title",
        "-t",
        help="Title of the prompt",
        prompt="Enter a title for your prompt",
    ),
    description: str = typer.Option(
        "",
        "--description",
        "-d",
        help="Description of the prompt",
        prompt="Enter a description (optional)",
    ),
    tags: List[str] = typer.Option(
        [],
        "--tag",
        help="Tags for the prompt (can be specified multiple times)",
    ),
    tags_prompt_str: Optional[str] = typer.Option(
        "",
        prompt="Enter tags separated by commas (optional)",
        help="Internal use for prompt input",
        hidden=True,
        show_default=False,
    ),
    vault_path: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Path to the prompt vault (defaults to ~/PromptVault or PROMPTKEEP_VAULT env var)",
    ),
) -> None:
    """Add a new prompt to your vault."""
    ctx = get_context(vault_path)

    # Combine tags from --tag flags and the prompt string
    processed_tags = tags[:]
    if tags_prompt_str and isinstance(tags_prompt_str, str):
        prompt_tags = [tag.strip() for tag in tags_prompt_str.split(",") if tag.strip()]
        processed_tags.extend(prompt_tags)
    processed_tags = sorted(list(set(processed_tags)))

    # Check for existing similar prompts using repository
    existing_files = ctx.repository.exists_similar(title)
    if existing_files:
        ctx.console.print(
            Panel.fit(
                f"[yellow]Warning: Similar prompts already exist:[/]\n"
                f"{chr(10).join(f'- {f.name}' for f in existing_files)}",
                title="Warning",
                border_style="yellow",
            )
        )
        if not typer.confirm("Do you want to continue?"):
            raise typer.Exit(0)

    # Create the prompt using repository.save()
    prompt = Prompt(
        title=title, description=description, tags=processed_tags, content=""
    )
    prompt_path = ctx.repository.save(prompt)

    ctx.console.print(
        Panel.fit(
            f"Opening editor for you to write your prompt content.\n"
            f"File will be saved at: [bold blue]{prompt_path}[/]",
            title="Creating Prompt",
            border_style="blue",
        )
    )

    try:
        ctx.editor.open(prompt_path)
    except PromptKeepError:
        prompt_path.unlink()
        raise

    if prompt_path.exists():
        ctx.console.print(
            Panel.fit(
                f"Prompt created successfully at: [bold blue]{prompt_path}[/]",
                title="Success",
                border_style="green",
            )
        )
    else:
        ctx.console.print(
            Panel.fit(
                "[yellow]Note: Prompt file was not saved.[/]",
                title="Warning",
                border_style="yellow",
            )
        )


@app.command("pick")
@handle_errors
def pick_command(
    vault_path: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Path to the prompt vault (defaults to ~/PromptVault or PROMPTKEEP_VAULT env var)",
    ),
    tags: Optional[List[str]] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Filter prompts by tag (can be specified multiple times)",
    ),
) -> None:
    """Select a prompt and copy its content to clipboard."""
    ctx = get_context(vault_path)

    prompt_files = ctx.repository.get_file_paths(tags=list(tags) if tags else None)

    if not prompt_files:
        if tags:
            tag_list = ", ".join(f"'{tag}'" for tag in tags)
            ctx.console.print(
                Panel.fit(
                    f"[yellow]No prompts found with tags: {tag_list}[/]",
                    title="Warning",
                    border_style="yellow",
                )
            )
        else:
            ctx.console.print(
                Panel.fit(
                    "[yellow]No prompts found in the vault.[/]\n"
                    "Use 'promptkeep add' to create a new prompt.",
                    title="Warning",
                    border_style="yellow",
                )
            )
        raise typer.Exit(1)

    selected_file = ctx.selector.select(prompt_files, "Select a prompt: ")
    if not selected_file:
        raise typer.Exit(0)

    content = selected_file.read_text()
    prompt_content = extract_prompt_content(content)
    ctx.clipboard.copy(prompt_content)

    ctx.console.print(
        Panel.fit(
            "Prompt copied to clipboard",
            title="Success",
            border_style="green",
        )
    )


@app.command("edit")
@handle_errors
def edit_command(
    vault_path: Optional[str] = typer.Option(
        None,
        "--vault",
        "-v",
        help="Path to the prompt vault (defaults to ~/PromptVault or PROMPTKEEP_VAULT env var)",
    ),
    tags: Optional[List[str]] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Filter prompts by tag (can be specified multiple times)",
    ),
) -> None:
    """Edit an existing prompt in your vault."""
    ctx = get_context(vault_path)

    prompt_files = ctx.repository.get_file_paths(tags=list(tags) if tags else None)

    if not prompt_files:
        if tags:
            tag_list = ", ".join(f"'{tag}'" for tag in tags)
            ctx.console.print(
                Panel.fit(
                    f"[yellow]No prompts found with tags: {tag_list}[/]",
                    title="Warning",
                    border_style="yellow",
                )
            )
        else:
            ctx.console.print(
                Panel.fit(
                    "[yellow]No prompts found in the vault.[/]\n"
                    "Use 'promptkeep add' to create a new prompt.",
                    title="Warning",
                    border_style="yellow",
                )
            )
        raise typer.Exit(1)

    selected_file = ctx.selector.select(prompt_files, "Select a prompt to edit: ")
    if not selected_file:
        raise typer.Exit(0)

    ctx.console.print(
        Panel.fit(
            f"Opening editor for you to edit the prompt.\n"
            f"File: [bold blue]{selected_file}[/]",
            title="Editing Prompt",
            border_style="blue",
        )
    )

    ctx.editor.open(selected_file)

    ctx.console.print(
        Panel.fit(
            "Prompt updated successfully",
            title="Success",
            border_style="green",
        )
    )


def main() -> None:
    """Entry point for the PromptKeep CLI application."""
    app()


if __name__ == "__main__":
    main()
