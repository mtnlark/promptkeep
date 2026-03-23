"""
Utility functions for PromptKeep.

This module provides core utility functions used throughout the application.
"""
import re

from promptkeep.constants import MAX_FILENAME_LENGTH, YAML_DELIMITER


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
    if len(sanitized) > MAX_FILENAME_LENGTH:
        sanitized = sanitized[:MAX_FILENAME_LENGTH]
    
    return sanitized


def extract_prompt_content(content: str) -> str:
    """Extract the prompt content from a markdown file, excluding YAML front matter.
    
    Args:
        content: The full content of the markdown file
        
    Returns:
        The prompt content without the YAML front matter
    """
    # Split the content into YAML and prompt text
    parts = content.split(YAML_DELIMITER, 2)
    if len(parts) == 3:
        return parts[2].strip()
    return content.strip()


