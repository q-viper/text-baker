"""
Command-line interface for TextBaker.

This module provides the CLI entry point using Typer for a rich command-line experience.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from textbaker import __description__, __version__

# Default paths relative to current working directory
DEFAULT_DATASET = Path("assets/dataset")
DEFAULT_OUTPUT = Path("output")
DEFAULT_BACKGROUNDS = Path("assets/backgrounds")
DEFAULT_TEXTURES = Path("assets/textures")

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
                f"[yellow]Author:[/yellow] Ramkrishna Acharya\n"
                f"[yellow]Repository:[/yellow] https://github.com/q-viper/text-baker",
                title="About",
                border_style="blue",
            )
        )
        raise typer.Exit()


def _launch_gui(
    dataset: Optional[Path] = None,
    output: Optional[Path] = None,
    backgrounds: Optional[Path] = None,
    textures: Optional[Path] = None,
    seed: Optional[int] = None,
):
    """Internal function to launch the GUI."""
    from PySide6.QtWidgets import QApplication

    from textbaker.app.main_window import DatasetMaker
    from textbaker.utils import DEFAULT_SEED, rng
    from textbaker.utils.logging import setup_logger

    setup_logger()

    # Set random seed (use provided or default)
    actual_seed = seed if seed is not None else DEFAULT_SEED
    rng.seed(actual_seed)

    # Use default paths if not provided
    dataset_path = dataset if dataset else (DEFAULT_DATASET if DEFAULT_DATASET.exists() else None)
    output_path = output if output else DEFAULT_OUTPUT
    backgrounds_path = (
        backgrounds
        if backgrounds
        else (DEFAULT_BACKGROUNDS if DEFAULT_BACKGROUNDS.exists() else None)
    )
    textures_path = (
        textures if textures else (DEFAULT_TEXTURES if DEFAULT_TEXTURES.exists() else None)
    )

    # Log startup info with paths
    console.print(
        Panel(
            f"[bold green]Starting TextBaker v{__version__}[/bold green]\n"
            f"[dim]Synthetic Text Dataset Generator for OCR Training[/dim]\n\n"
            f"[yellow]Paths:[/yellow]\n"
            f"  Dataset:     {dataset_path or '[not set]'}\n"
            f"  Output:      {output_path}\n"
            f"  Backgrounds: {backgrounds_path or '[not set]'}\n"
            f"  Textures:    {textures_path or '[not set]'}\n\n"
            f"[yellow]Seed:[/yellow] {actual_seed}",
            border_style="green",
        )
    )

    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("TextBaker")
    qt_app.setApplicationVersion(__version__)

    window = DatasetMaker(
        dataset_root=str(dataset_path) if dataset_path else None,
        output_dir=str(output_path) if output_path else None,
        background_dir=str(backgrounds_path) if backgrounds_path else None,
        texture_dir=str(textures_path) if textures_path else None,
    )
    window.show()

    sys.exit(qt_app.exec())


@app.command(name="gui")
def gui_command(
    dataset: Optional[Path] = typer.Option(
        None,
        "--dataset",
        "-d",
        help=f"Path to dataset folder containing character subfolders (default: {DEFAULT_DATASET})",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help=f"Path to output folder for generated images (default: {DEFAULT_OUTPUT})",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    backgrounds: Optional[Path] = typer.Option(
        None,
        "--backgrounds",
        "-b",
        help=f"Path to folder containing background images (default: {DEFAULT_BACKGROUNDS})",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    textures: Optional[Path] = typer.Option(
        None,
        "--textures",
        "-t",
        help=f"Path to folder containing texture images (default: {DEFAULT_TEXTURES})",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    seed: Optional[int] = typer.Option(
        None,
        "--seed",
        "-s",
        help="Random seed for reproducible generation",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file (JSON/YAML)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
):
    """
    🍞 Launch the TextBaker GUI application.

    Generate synthetic text images by combining character datasets with backgrounds
    and applying various transformations like rotation, perspective, and texturing.

    [bold]Examples:[/bold]

        # Launch GUI with default settings
        $ textbaker

        # Launch with specific folders
        $ textbaker -d ./dataset -o ./output -b ./backgrounds

        # Reproducible generation with seed
        $ textbaker --seed 42
    """
    _launch_gui(dataset, output, backgrounds, textures, seed)


# Available CV2 fonts for help text
CV2_FONTS = [
    "FONT_HERSHEY_SIMPLEX",
    "FONT_HERSHEY_PLAIN",
    "FONT_HERSHEY_DUPLEX",
    "FONT_HERSHEY_COMPLEX",
    "FONT_HERSHEY_TRIPLEX",
    "FONT_HERSHEY_COMPLEX_SMALL",
    "FONT_HERSHEY_SCRIPT_SIMPLEX",
    "FONT_HERSHEY_SCRIPT_COMPLEX",
]


@app.command(name="generate")
def generate_command(
    texts: Optional[list[str]] = typer.Argument(
        None,
        help="Text strings to generate images for",
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file (JSON/YAML)",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    dataset: Optional[Path] = typer.Option(
        None,
        "--dataset",
        "-d",
        help=f"Path to dataset folder (default: {DEFAULT_DATASET})",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help=f"Path to output folder (default: {DEFAULT_OUTPUT})",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    seed: int = typer.Option(
        42,
        "--seed",
        "-s",
        help="Random seed for reproducible generation",
    ),
    count: int = typer.Option(
        10,
        "--count",
        "-n",
        help="Number of random samples to generate (if no texts provided)",
    ),
    length: Optional[int] = typer.Option(
        None,
        "--length",
        "-l",
        help="Text length for random generation (default: random 1-10)",
    ),
    spacing: int = typer.Option(
        0,
        "--spacing",
        help="Spacing between characters in pixels",
    ),
    char_width: int = typer.Option(
        64,
        "--char-width",
        help="Character width in pixels for fallback rendering",
    ),
    char_height: int = typer.Option(
        64,
        "--char-height",
        help="Character height in pixels for fallback rendering",
    ),
    font: str = typer.Option(
        "FONT_HERSHEY_SCRIPT_COMPLEX",
        "--font",
        "-f",
        help=f"CV2 font for fallback text. Options: {', '.join(CV2_FONTS)}",
    ),
    # Transform options
    rotation: Optional[str] = typer.Option(
        None,
        "--rotation",
        "-r",
        help="Rotation range in degrees, e.g. '-15,15' for random rotation between -15 and 15",
    ),
    perspective: Optional[str] = typer.Option(
        None,
        "--perspective",
        "-p",
        help="Perspective distortion range, e.g. '0.0,0.1' for subtle perspective",
    ),
    scale: Optional[str] = typer.Option(
        None,
        "--scale",
        help="Scale range, e.g. '0.8,1.2' for 80%%-120%% scaling",
    ),
    shear: Optional[str] = typer.Option(
        None,
        "--shear",
        help="Shear range in degrees, e.g. '-10,10'",
    ),
    # Background options
    backgrounds: Optional[Path] = typer.Option(
        None,
        "--backgrounds",
        "-b",
        help="Path to folder containing background images",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    bg_color: Optional[str] = typer.Option(
        None,
        "--bg-color",
        help="Solid background color as 'R,G,B', e.g. '255,255,255' for white",
    ),
    # Texture options
    textures: Optional[Path] = typer.Option(
        None,
        "--textures",
        "-t",
        help="Path to folder containing texture images",
        exists=False,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    texture_opacity: float = typer.Option(
        1.0,
        "--texture-opacity",
        help="Texture opacity (0.0-1.0)",
        min=0.0,
        max=1.0,
    ),
    texture_per_char: bool = typer.Option(
        False,
        "--texture-per-char",
        help="Apply different texture to each character",
    ),
    # Color options
    random_color: bool = typer.Option(
        False,
        "--random-color",
        help="Apply random colors to characters",
    ),
    color: Optional[str] = typer.Option(
        None,
        "--color",
        help="Fixed color as 'R,G,B', e.g. '0,0,0' for black text",
    ),
    color_range_r: Optional[str] = typer.Option(
        None,
        "--color-r",
        help="Red channel range for random color, e.g. '100,255'",
    ),
    color_range_g: Optional[str] = typer.Option(
        None,
        "--color-g",
        help="Green channel range for random color, e.g. '100,255'",
    ),
    color_range_b: Optional[str] = typer.Option(
        None,
        "--color-b",
        help="Blue channel range for random color, e.g. '100,255'",
    ),
):
    """
    📝 Generate text images from command line (no GUI).

    Generate synthetic text images programmatically for batch processing.
    Characters not found in dataset will be rendered using cv2.putText with the specified font.

    [bold]Examples:[/bold]

        # Generate specific texts
        $ textbaker generate "hello" "world" "test"

        # Generate 100 random samples
        $ textbaker generate -n 100 --seed 42

        # Apply rotation and perspective transforms
        $ textbaker generate "hello" --rotation "-15,15" --perspective "0.0,0.1"

        # Add backgrounds
        $ textbaker generate "hello" -b ./backgrounds
        $ textbaker generate "hello" --bg-color "255,255,255"

        # Apply textures
        $ textbaker generate "hello" -t ./textures --texture-opacity 0.8

        # Random colors or fixed color
        $ textbaker generate "hello" --random-color
        $ textbaker generate "hello" --color "0,0,255"

        # Full pipeline
        $ textbaker generate "hello" -r "-10,10" -p "0,0.05" -b ./bg -t ./tex --random-color
    """
    from textbaker.core.configs import (
        BackgroundConfig,
        CharacterConfig,
        ColorConfig,
        DatasetConfig,
        GeneratorConfig,
        OutputConfig,
        TextureConfig,
        TransformConfig,
    )
    from textbaker.core.generator import TextGenerator
    from textbaker.utils.logging import setup_logger

    setup_logger()

    # Helper to parse range strings like "-15,15"
    def parse_range(value: Optional[str], name: str) -> Optional[tuple]:
        if value is None:
            return None
        try:
            parts = value.split(",")
            if len(parts) != 2:
                raise ValueError("Expected 2 values")
            return (float(parts[0].strip()), float(parts[1].strip()))
        except Exception:
            console.print(
                f"[red]Invalid {name} format: '{value}'. Expected 'min,max' (e.g. '-15,15')[/red]"
            )
            raise typer.Exit(1) from None

    # Helper to parse int range strings like "100,255"
    def parse_int_range(value: Optional[str], name: str) -> Optional[tuple]:
        if value is None:
            return None
        try:
            parts = value.split(",")
            if len(parts) != 2:
                raise ValueError("Expected 2 values")
            return (int(parts[0].strip()), int(parts[1].strip()))
        except Exception:
            console.print(
                f"[red]Invalid {name} format: '{value}'. Expected 'min,max' (e.g. '100,255')[/red]"
            )
            raise typer.Exit(1) from None

    # Helper to parse color strings like "255,255,255"
    def parse_color(value: Optional[str], name: str) -> Optional[tuple]:
        if value is None:
            return None
        try:
            parts = value.split(",")
            if len(parts) != 3:
                raise ValueError("Expected 3 values")
            return (int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip()))
        except Exception:
            console.print(
                f"[red]Invalid {name} format: '{value}'. Expected 'R,G,B' (e.g. '255,255,255')[/red]"
            )
            raise typer.Exit(1) from None

    # Validate font
    if font not in CV2_FONTS:
        console.print(f"[red]Invalid font: {font}[/red]")
        console.print(f"[dim]Available fonts: {', '.join(CV2_FONTS)}[/dim]")
        raise typer.Exit(1)

    # Parse range/color options
    rotation_range = parse_range(rotation, "rotation")
    perspective_range = parse_range(perspective, "perspective")
    scale_range = parse_range(scale, "scale")
    shear_range = parse_range(shear, "shear")
    bg_color_tuple = parse_color(bg_color, "bg-color")
    color_tuple = parse_color(color, "color")
    r_range = parse_int_range(color_range_r, "color-r")
    g_range = parse_int_range(color_range_g, "color-g")
    b_range = parse_int_range(color_range_b, "color-b")

    # Load or create config
    if config:
        generator_config = GeneratorConfig.from_file(config)
        console.print(f"[dim]Loaded config from: {config}[/dim]")
    else:
        # Build transform config
        transform_config = TransformConfig()
        if rotation_range:
            transform_config.rotation_range = rotation_range
        if perspective_range:
            transform_config.perspective_range = perspective_range
        if scale_range:
            transform_config.scale_range = scale_range
        if shear_range:
            transform_config.shear_range = shear_range

        # Build background config
        background_config = BackgroundConfig()
        if backgrounds and backgrounds.exists():
            background_config.enabled = True
            background_config.background_dir = backgrounds
        if bg_color_tuple:
            background_config.enabled = True
            background_config.color = bg_color_tuple

        # Build texture config
        texture_config = TextureConfig()
        if textures and textures.exists():
            texture_config.enabled = True
            texture_config.texture_dir = textures
            texture_config.opacity = texture_opacity
            texture_config.per_character = texture_per_char

        # Build color config
        color_config = ColorConfig()
        if random_color:
            color_config.random_color = True
        if color_tuple:
            color_config.fixed_color = color_tuple
        if r_range:
            color_config.color_range_r = r_range
        if g_range:
            color_config.color_range_g = g_range
        if b_range:
            color_config.color_range_b = b_range

        generator_config = GeneratorConfig(
            seed=seed,
            spacing=spacing,
            dataset=DatasetConfig(dataset_dir=dataset or DEFAULT_DATASET),
            output=OutputConfig(output_dir=output or DEFAULT_OUTPUT),
            character=CharacterConfig(
                width=char_width,
                height=char_height,
                font=font,
            ),
            transform=transform_config,
            background=background_config,
            texture=texture_config,
            color=color_config,
        )

    # Override with CLI options if provided (when using config file)
    if seed != 42:
        generator_config.seed = seed
    if spacing != 0:
        generator_config.spacing = spacing
    if dataset:
        generator_config.dataset.dataset_dir = dataset
    if output:
        generator_config.output.output_dir = output
    if char_width != 64:
        generator_config.character.width = char_width
    if char_height != 64:
        generator_config.character.height = char_height
    if font != "FONT_HERSHEY_SCRIPT_COMPLEX":
        generator_config.character.font = font
    # Override transform if provided
    if rotation_range:
        generator_config.transform.rotation_range = rotation_range
    if perspective_range:
        generator_config.transform.perspective_range = perspective_range
    if scale_range:
        generator_config.transform.scale_range = scale_range
    if shear_range:
        generator_config.transform.shear_range = shear_range
    # Override background if provided
    if backgrounds and backgrounds.exists():
        generator_config.background.enabled = True
        generator_config.background.background_dir = backgrounds
    if bg_color_tuple:
        generator_config.background.enabled = True
        generator_config.background.color = bg_color_tuple
    # Override texture if provided
    if textures and textures.exists():
        generator_config.texture.enabled = True
        generator_config.texture.texture_dir = textures
        generator_config.texture.opacity = texture_opacity
        generator_config.texture.per_character = texture_per_char
    # Override color if provided
    if random_color:
        generator_config.color.random_color = True
    if color_tuple:
        generator_config.color.fixed_color = color_tuple
    if r_range:
        generator_config.color.color_range_r = r_range
    if g_range:
        generator_config.color.color_range_g = g_range
    if b_range:
        generator_config.color.color_range_b = b_range

    # Build display info
    transform_info = []
    if generator_config.transform.rotation_range != (0.0, 0.0):
        transform_info.append(f"Rotation: {generator_config.transform.rotation_range}")
    if generator_config.transform.perspective_range != (0.0, 0.0):
        transform_info.append(f"Perspective: {generator_config.transform.perspective_range}")
    if generator_config.transform.scale_range != (0.9, 1.1):
        transform_info.append(f"Scale: {generator_config.transform.scale_range}")
    if generator_config.transform.shear_range != (0.0, 0.0):
        transform_info.append(f"Shear: {generator_config.transform.shear_range}")

    extras_info = []
    if generator_config.background.enabled:
        if generator_config.background.background_dir:
            extras_info.append(f"Background: {generator_config.background.background_dir}")
        elif generator_config.background.color:
            extras_info.append(f"Background: RGB{generator_config.background.color}")
    if generator_config.texture.enabled:
        extras_info.append(
            f"Texture: {generator_config.texture.texture_dir} (opacity={generator_config.texture.opacity})"
        )
    if generator_config.color.random_color:
        extras_info.append("Color: random")
    elif generator_config.color.fixed_color:
        extras_info.append(f"Color: RGB{generator_config.color.fixed_color}")

    # Log paths and config
    panel_content = (
        f"[bold blue]TextBaker Generator[/bold blue]\n\n"
        f"[yellow]Paths:[/yellow]\n"
        f"  Dataset: {generator_config.dataset.dataset_dir}\n"
        f"  Output:  {generator_config.output.output_dir}\n\n"
        f"[yellow]Config:[/yellow]\n"
        f"  Seed:    {generator_config.seed}\n"
        f"  Spacing: {generator_config.spacing}\n"
        f"  Char size: {generator_config.character.width}x{generator_config.character.height}\n"
        f"  Font:    {generator_config.character.font}"
    )
    if transform_info:
        panel_content += "\n\n[yellow]Transforms:[/yellow]\n  " + "\n  ".join(transform_info)
    if extras_info:
        panel_content += "\n\n[yellow]Effects:[/yellow]\n  " + "\n  ".join(extras_info)

    console.print(Panel(panel_content, border_style="blue"))

    # Create generator
    generator = TextGenerator(generator_config)

    try:
        generator.initialize()
    except Exception as e:
        console.print(f"[red]Error initializing generator: {e}[/red]")
        raise typer.Exit(1) from None

    available = generator.available_characters

    if not available:
        console.print(
            Panel(
                f"[bold red]No character images found![/bold red]\n\n"
                f"[dim]Looked in: {generator_config.dataset.dataset_dir}[/dim]\n\n"
                f"Please provide a dataset folder with character images:\n"
                f'  textbaker generate -d /path/to/dataset "hello"\n\n'
                f"Expected structure:\n"
                f"  dataset/\n"
                f"    ├── A/\n"
                f"    │   └── img001.png\n"
                f"    ├── B/\n"
                f"    │   └── img001.png\n"
                f"    └── ...",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    console.print(f"[green]Loaded {len(available)} character classes[/green]")

    # Generate images
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        if texts:
            # Generate specific texts
            task = progress.add_task(f"Generating {len(texts)} images...", total=len(texts))
            for text in texts:
                try:
                    result = generator.generate(text)
                    generator.save(result)
                    results.append(result)
                    progress.advance(task)
                except ValueError as e:
                    console.print(f"[red]Error generating '{text}': {e}[/red]")
                    progress.advance(task)
        else:
            # Generate random samples
            task = progress.add_task(f"Generating {count} random images...", total=count)
            for _ in range(count):
                try:
                    result = generator.generate_random(length=length)
                    generator.save(result)
                    results.append(result)
                    progress.advance(task)
                except ValueError as e:
                    console.print(f"[red]Error: {e}[/red]")

    # Show result message
    if results:
        console.print(
            Panel(
                f"[bold green]✓ Generated {len(results)} images[/bold green]\n"
                f"[dim]Output: {generator_config.output.output_dir}[/dim]",
                border_style="green",
            )
        )
    else:
        requested = len(texts) if texts else count
        console.print(
            Panel(
                f"[bold red]✗ Failed to generate any images[/bold red]\n"
                f"[dim]Requested: {requested}[/dim]",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command(name="init-config")
def init_config_command(
    output: Path = typer.Option(
        Path("textbaker_config.yaml"),
        "--output",
        "-o",
        help="Output path for config file",
    ),
    format: str = typer.Option(
        "yaml",
        "--format",
        "-f",
        help="Config format (json or yaml)",
    ),
):
    """
    📋 Create a default configuration file.

    Generate a config file with all available options and their default values.

    [bold]Examples:[/bold]

        # Create YAML config (default)
        $ textbaker init-config

        # Create JSON config
        $ textbaker init-config -f json -o config.json

        # Specify output path
        $ textbaker init-config -o my_config.yaml
    """
    from textbaker.core.configs import GeneratorConfig

    config = GeneratorConfig()

    if format.lower() in ("yaml", "yml"):
        output = output.with_suffix(".yaml")
    else:
        output = output.with_suffix(".json")

    config.to_file(output)

    console.print(
        Panel(
            f"[bold green]✓ Created config file[/bold green]\n[dim]Path: {output}[/dim]",
            border_style="green",
        )
    )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version information and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """
    🍞 TextBaker - Synthetic Text Dataset Generator for OCR Training.

    Run without arguments to launch the GUI application.

    [bold]Commands:[/bold]

        (none)     - Launch the GUI application (default)
        gui        - Launch the GUI application
        generate   - Generate images from command line
        init-config - Create a default configuration file

    [bold]Quick Start:[/bold]

        # Launch GUI (default)
        $ textbaker

        # Generate images without GUI
        $ textbaker generate "hello" "world"

        # Show help
        $ textbaker --help

    [bold]Author:[/bold] Ramkrishna Acharya
    """
    # If no command provided, launch GUI with defaults
    if ctx.invoked_subcommand is None:
        _launch_gui()


def run():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    run()
