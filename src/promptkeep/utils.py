"""
Utility functions for PromptKeep.

This module provides core utility functions used throughout the PromptKeep application,
including file path management, clipboard operations, and text processing.
"""
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional

import pyperclip
import typer
from rich.console import Console
from rich.panel import Panel

console = Console()


def sanitize_filename(title: str) -> str:
    """Convert a title into a valid filename.
    
    This function handles several aspects of filename sanitization:
    - Converts to lowercase
    - Replaces invalid characters with hyphens
    - Removes consecutive hyphens
    - Trims leading/trailing hyphens
    - Enforces a maximum length of 100 characters
    
    Args:
        title: The original title to be converted into a filename
        
    Returns:
        A sanitized string suitable for use as a filename
        
    Example:
        >>> sanitize_filename("My Prompt: A Test?")
        'my-prompt-a-test'
    """
    # Convert to lowercase for consistency
    title = title.lower()
    
    # Replace invalid filesystem characters with hyphens
    # This includes: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '-', title)
    
    # Replace spaces with hyphens for better readability
    sanitized = sanitized.replace(' ', '-')
    
    # Remove consecutive hyphens to avoid messy filenames
    sanitized = re.sub(r'-+', '-', sanitized)
    
    # Remove leading/trailing hyphens that might cause issues
    sanitized = sanitized.strip('-')
    
    # Enforce maximum filename length to prevent filesystem issues
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized


def find_vault_path() -> Optional[Path]:
    """Locate the prompt vault by checking common locations.
    
    This function searches for the vault in the following order:
    1. Path specified in PROMPTKEEP_VAULT environment variable
    2. Default location (~/PromptVault)
    
    Returns:
        Path to the vault if found, None otherwise
    """
    # First, check environment variable for custom vault location
    env_path = os.environ.get("PROMPTKEEP_VAULT")
    if env_path:
        path = Path(env_path).expanduser().absolute()
        if path.exists() and (path / "Prompts").exists():
            return path

    # Check default location if environment variable not set or invalid
    default_path = Path("~/PromptVault").expanduser().absolute()
    if default_path.exists() and (default_path / "Prompts").exists():
        return default_path

    # No valid vault found
    return None


def validate_vault_path(vault_path: Optional[str]) -> Path:
    """Validate the existence and structure of a prompt vault.
    
    This function ensures that:
    1. The vault directory exists
    2. It contains a 'Prompts' subdirectory
    3. The path is absolute and expanded
    
    Args:
        vault_path: Optional path to the vault. If None, attempts to find it.
        
    Returns:
        Validated absolute Path to the vault
        
    Raises:
        typer.Exit: If the vault is not found or is invalid
    """
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

    return expanded_vault


def copy_to_clipboard(text: str) -> None:
    """Copy text to the system clipboard.
    
    Args:
        text: The text to copy to the clipboard
    """
    pyperclip.copy(text)


def extract_prompt_content(content: str) -> str:
    """Extract the prompt content from a markdown file, excluding YAML front matter.
    
    Args:
        content: The full content of the markdown file
        
    Returns:
        The prompt content without the YAML front matter
    """
    # Split the content into YAML and prompt text
    parts = content.split("---", 2)
    if len(parts) == 3:
        return parts[2].strip()
    return content.strip()


def open_editor(file_path: Path) -> bool:
    """Open the user's default editor to edit a file.
    
    Args:
        file_path: Path to the file to edit
        
    Returns:
        True if the editor was opened successfully, False otherwise
    """
    editor = os.environ.get("EDITOR", "vim")
    try:
        subprocess.run([editor, str(file_path)], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        console.print(
            Panel.fit(
                f"[red]Error: Editor '{editor}' not found.[/]\n"
                "Please set the EDITOR environment variable to your preferred editor.",
                title="Error",
                border_style="red",
            )
        )
        return False 