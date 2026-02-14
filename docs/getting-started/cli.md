# CLI Usage

TextBaker provides a rich command-line interface powered by [Typer](https://typer.tiangolo.com/).

## Basic Commands

### Launch GUI

```bash
textbaker
```

### Show Version

```bash
textbaker --version
# or
textbaker -v
```

### Show Help

```bash
textbaker --help
```

Output:

```
 Usage: textbaker [OPTIONS]

 🍞 TextBaker - Synthetic Text Dataset Generator for OCR Training.

 Generate synthetic text images by combining character datasets with backgrounds
 and applying various transformations like rotation, perspective, and texturing.

 Examples:

     # Launch GUI with default settings
     $ textbaker

     # Launch with specific folders
     $ textbaker -d ./dataset -o ./output -b ./backgrounds

     # Show help
     $ textbaker --help

 Author: Ramkrishna Acharya

╭─ Options ─────────────────────────────────────────────────────────────────────╮
│ --dataset      -d  PATH  Path to dataset folder containing character          │
│                          subfolders                                           │
│ --output       -o  PATH  Path to output folder for generated images           │
│ --backgrounds  -b  PATH  Path to folder containing background images          │
│ --textures     -t  PATH  Path to folder containing texture images             │
│ --version      -v        Show version information and exit                    │
│ --help                   Show this message and exit.                          │
╰───────────────────────────────────────────────────────────────────────────────╯
```

## Options

| Option | Short | Description |
|--------|-------|-------------|
| `--dataset` | `-d` | Path to dataset folder containing character subfolders |
| `--output` | `-o` | Path to output folder for generated images |
| `--backgrounds` | `-b` | Path to folder containing background images |
| `--textures` | `-t` | Path to folder containing texture images |
| `--version` | `-v` | Show version information and exit |
| `--help` | | Show help message and exit |

## Examples

### Launch with All Options

```bash
textbaker \
    --dataset /path/to/characters \
    --output /path/to/output \
    --backgrounds /path/to/backgrounds \
    --textures /path/to/textures
```

### Using Short Options

```bash
textbaker -d ./dataset -o ./output -b ./backgrounds -t ./textures
```

### Run as Python Module

```bash
python -m textbaker
python -m textbaker --help
python -m textbaker -d ./dataset -o ./output
```

## Shell Completion

TextBaker supports shell completion for bash, zsh, fish, and PowerShell.

### Install Completion

```bash
# For bash
textbaker --install-completion bash

# For zsh
textbaker --install-completion zsh

# For fish
textbaker --install-completion fish

# For PowerShell
textbaker --install-completion powershell
```

After installation, restart your shell or source the completion file.
