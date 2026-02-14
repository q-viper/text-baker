# TextBaker

**Synthetic Text Dataset Generator for OCR Training**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/q-viper/text-baker/blob/main/LICENSE)

---

## Example Outputs

| Basic | Transformed | Colored | Background | Texture | Full Pipeline |
|:-----:|:-----------:|:-------:|:----------:|:-------:|:-------------:|
| ![Basic](assets/readme/example_basic.png) | ![Rotated](assets/readme/example_rotated.png) | ![Colored](assets/readme/example_colored.png) | ![Background](assets/readme/example_background.png) | ![Texture](assets/readme/example_texture.png) | ![Full](assets/readme/example_full.png) |

📖 See [Examples](examples.md) for code that generates these images.

---

## Installation

```bash
pip install textbaker
```

**From source:**

```bash
git clone https://github.com/q-viper/text-baker.git
cd text-baker
pip install -e .
```

---

## Quick Start

### GUI Application

```bash
textbaker
```

### CLI Generation

```bash
# Generate specific texts
textbaker generate "hello" "world" -d ./dataset

# Generate random samples with transforms
textbaker generate -n 100 --seed 42 -r "-15,15"
```

### Python Library

```python
from textbaker import TextGenerator, GeneratorConfig

generator = TextGenerator()
result = generator.generate("hello")
generator.save(result)
```

📖 See [Examples](examples.md) for more detailed code samples.

---

## Dataset Structure

Images are scanned **recursively**. Parent folder name = character label:

```
assets/dataset/
├── A/
│   └── sample1.png  → label "A"
├── B/
│   └── sample1.png  → label "B"
└── digits/
    └── 0/
        └── sample1.png  → label "0"
```

---

## Documentation

- **[Examples](examples.md)** - Code samples with visual outputs
- **[Configuration](configuration.md)** - All config options explained
- **[CLI Reference](cli.md)** - Command line usage
- **[API Reference](api.md)** - Python API documentation

---

## Author

**Ramkrishna Acharya** — [GitHub](https://github.com/q-viper)

## License

MIT License — see [LICENSE](https://github.com/q-viper/text-baker/blob/main/LICENSE)
