"""Entry point for the promptkeep package.

This module enables the package to be run directly using `python -m promptkeep`.
It imports and executes the main CLI application from the cli module.
"""
from promptkeep.cli import app

if __name__ == "__main__":
    app() 