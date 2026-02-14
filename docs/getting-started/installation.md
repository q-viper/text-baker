# Installation

## Requirements

- Python 3.9 or higher
- pip (Python package installer)

## Install from PyPI

The easiest way to install TextBaker is via pip:

```bash
pip install textbaker
```

## Install from Source

For the latest development version:

```bash
git clone https://github.com/rnkrsoft/textbaker.git
cd textbaker
pip install -e .
```

## Development Installation

If you want to contribute or run tests:

```bash
git clone https://github.com/rnkrsoft/textbaker.git
cd textbaker
pip install -e ".[dev,docs]"
```

## Verify Installation

After installation, verify it works:

```bash
textbaker --version
```

You should see output like:

```
╭─────────────────────── About ───────────────────────╮
│ TextBaker v0.1.0                                    │
│ Synthetic Text Dataset Generator for OCR Training  │
│                                                     │
│ Author: Ramkrishna Acharya                          │
╰─────────────────────────────────────────────────────╯
```

## Dependencies

TextBaker depends on the following packages:

| Package | Version | Description |
|---------|---------|-------------|
| numpy | ≥1.21.0 | Numerical computing |
| opencv-python | ≥4.5.0 | Image processing |
| PySide6 | ≥6.4.0 | Qt GUI framework |
| loguru | ≥0.6.0 | Logging |
| typer | ≥0.9.0 | CLI framework |
| rich | ≥13.0.0 | Rich terminal output |
