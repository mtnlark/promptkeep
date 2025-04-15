"""
Main CLI module for PromptKeep
"""
import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer()
console = Console()

@app.command()
def init(
    vault_path: str = typer.Option(
        "~/PromptVault",
        help="Path where your prompt vault will be created",
    )
):
    """Initialize a new prompt vault"""
    console.print(Panel.fit(
        "Welcome to PromptKeep! 🎉\n\n"
        "This command will help you set up your prompt vault.\n"
        "We'll create a new directory at: [bold blue]{}[/]".format(vault_path),
        title="Initializing Prompt Vault",
        border_style="blue"
    ))

def main():
    """Entry point for the CLI"""
    app()

if __name__ == "__main__":
    main() 