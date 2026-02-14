"""
Command-line interface for TextBaker.

This module provides the CLI entry point using Typer for a rich command-line experience.
"""

import sys
from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from textbaker import __version__, __description__

app = typer.Typer(
    name="textbaker",
    help=__description__,
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=False,
)
console = Console()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(
            Panel(
                f"[bold blue]TextBaker[/bold blue] v{__version__}\n"
                f"[dim]{__description__}[/dim]\n\n"
                f"[yellow]Author:[/yellow] Ramkrishna Acharya",
                title="About",
                border_style="blue",
            )
        )
        raise typer.Exit()


@app.command()
def main(
    dataset: Optional[Path] = typer.Option(
        None,
        "--dataset", "-d",
        help="Path to dataset folder containing character subfolders",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output", "-o",
        help="Path to output folder for generated images",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    backgrounds: Optional[Path] = typer.Option(
        None,
        "--backgrounds", "-b",
        help="Path to folder containing background images",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    textures: Optional[Path] = typer.Option(
        None,
        "--textures", "-t",
        help="Path to folder containing texture images",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    version: bool = typer.Option(
        False,
        "--version", "-v",
        help="Show version information and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    🍞 TextBaker - Synthetic Text Dataset Generator for OCR Training.
    
    Generate synthetic text images by combining character datasets with backgrounds
    and applying various transformations like rotation, perspective, and texturing.
    
    [bold]Examples:[/bold]
    
        # Launch GUI with default settings
        $ textbaker
        
        # Launch with specific folders
        $ textbaker -d ./dataset -o ./output -b ./backgrounds
        
        # Show help
        $ textbaker --help
    
    [bold]Author:[/bold] Ramkrishna Acharya
    """
    from PySide6.QtWidgets import QApplication
    from textbaker.app.main_window import DatasetMaker
    from textbaker.utils.logging import setup_logger
    
    setup_logger()
    
    console.print(
        Panel(
            f"[bold green]Starting TextBaker v{__version__}[/bold green]\n"
            f"[dim]Synthetic Text Dataset Generator for OCR Training[/dim]",
            border_style="green",
        )
    )
    
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("TextBaker")
    qt_app.setApplicationVersion(__version__)
    
    window = DatasetMaker(
        dataset_root=str(dataset) if dataset else None,
        output_dir=str(output) if output else None,
        background_dir=str(backgrounds) if backgrounds else None,
        texture_dir=str(textures) if textures else None,
    )
    window.show()
    
    sys.exit(qt_app.exec())


def run():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    run()
