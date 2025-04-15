#!/usr/bin/env python3
"""
Command-line entry point for PromptKeep.

This module provides the main entry point for the PromptKeep CLI application.
When run directly (e.g., `python -m promptkeep`), it initializes and runs the
Typer-based CLI application defined in the cli module.
"""
from promptkeep.cli import app

def main():
    """Execute the PromptKeep CLI application.
    
    This function serves as the main entry point for the application,
    initializing and running the Typer-based CLI interface.
    """
    app()

if __name__ == "__main__":
    main() 