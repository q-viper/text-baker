# CLI Reference

TextBaker provides a command-line interface for generating synthetic text images.

---

## Commands

### `textbaker` (default: GUI)

Launch the GUI application.

```bash
textbaker
# or explicitly
textbaker gui
```

### `textbaker generate`

Generate images from command line (no GUI).

```bash
textbaker generate [TEXTS]... [OPTIONS]
```

### `textbaker init-config`

Create a default configuration file.

```bash
textbaker init-config -o config.yaml
```

---

## GUI Options

```bash
textbaker gui [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--dataset` | `-d` | `assets/dataset` | Character dataset folder |
| `--output` | `-o` | `output` | Output folder |
| `--backgrounds` | `-b` | `assets/backgrounds` | Background images |
| `--textures` | `-t` | `assets/textures` | Texture images |
| `--seed` | `-s` | `42` | Random seed |
| `--config` | `-c` | | Config file (JSON/YAML) |

**Examples:**

```bash
# Launch with defaults
textbaker

# With custom paths
textbaker -d ./my_dataset -o ./output -b ./backgrounds

# With seed for reproducibility
textbaker --seed 123

# Load from config file
textbaker -c config.yaml
```

---

## Generate Options

```bash
textbaker generate [TEXTS]... [OPTIONS]
```

### Basic Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--config` | `-c` | | Config file (JSON/YAML) |
| `--dataset` | `-d` | `assets/dataset` | Dataset folder |
| `--output` | `-o` | `output` | Output folder |
| `--seed` | `-s` | `42` | Random seed |
| `--count` | `-n` | `10` | Number of random samples |
| `--length` | `-l` | random | Text length (single or range) |
| `--spacing` | | `0` | Spacing between characters |

### Transform Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--rotation` | `-r` | `0,0` | Rotation range (min,max degrees) |
| `--perspective` | `-p` | `0,0` | Perspective range (min,max) |
| `--scale` | | `1.0,1.0` | Scale range (min,max) |
| `--shear` | | `0,0` | Shear range (min,max degrees) |

### Color Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--random-color` | | `false` | Enable random coloring |
| `--color` | | | Fixed color as R,G,B (e.g., `255,0,0`) |

### Background & Texture Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--background` | `-b` | | Background images directory |
| `--texture` | `-t` | | Texture images directory |
| `--texture-opacity` | | `0.8` | Texture opacity (0.0-1.0) |

**Examples:**

```bash
# Generate specific texts
textbaker generate "Hello" "World" -d ./dataset -o ./output

# Generate 100 random samples
textbaker generate -n 100 --seed 42 -d ./dataset

# Apply transformations
textbaker generate "Hello" -r "-15,15" -p "0,0.1" --scale "0.9,1.1"

# With backgrounds and textures
textbaker generate "Hello" -b ./backgrounds -t ./textures --texture-opacity 0.8

# Random colors
textbaker generate "Hello" --random-color

# Fixed color (red)
textbaker generate "Hello" --color "255,0,0"

# Full pipeline
textbaker generate "Hello" \
    -r "-10,10" \
    -p "0,0.05" \
    -b ./backgrounds \
    -t ./textures \
    --random-color \
    --seed 42
```

---

## Init-Config Options

```bash
textbaker init-config [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | `config.json` | Output file path |
| `--format` | `-f` | auto | Output format (json/yaml, auto-detected from extension) |

**Examples:**

```bash
# Create JSON config
textbaker init-config -o config.json

# Create YAML config
textbaker init-config -o config.yaml
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `TEXTBAKER_SEED` | Default random seed |
| `TEXTBAKER_DATASET` | Default dataset directory |
| `TEXTBAKER_OUTPUT` | Default output directory |

---

## Exit Codes

| Code | Description |
|------|-------------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |
