# Overview

TextBaker is designed to help machine learning practitioners create synthetic datasets for training OCR (Optical Character Recognition) models.

## Why Synthetic Data?

Training robust OCR models requires large, diverse datasets. However:

- **Real data is expensive** to collect and annotate
- **Privacy concerns** may limit access to real documents
- **Specific scenarios** may be rare in real data
- **Controlled variations** are needed for testing

Synthetic data generation solves these problems by programmatically creating training images with known ground truth labels.

## How TextBaker Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Character  │     │    Text     │     │   Output    │
│   Dataset   │ ──▶ │  Generator  │ ──▶ │   Images    │
└─────────────┘     └─────────────┘     └─────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ Backgrounds │   │  Textures   │   │ Transforms  │
└─────────────┘   └─────────────┘   └─────────────┘
```

### Components

1. **Character Dataset**: Individual character images organized by label
2. **Background Images**: Natural or synthetic backgrounds
3. **Textures**: Optional textures to apply to text
4. **Transformations**: Rotation, perspective, scaling, etc.

## Key Features

### Interactive GUI

The graphical interface allows you to:

- Preview generated text in real-time
- Adjust positioning with drag-and-drop
- Apply transformations interactively
- Fine-tune parameters visually

### Rich CLI

The command-line interface provides:

- Quick launching with preset configurations
- Beautiful terminal output with Rich
- Shell completion support
- Scriptable for automation

### Flexible Image Processing

The core image processor supports:

- Multiple image formats (PNG, JPG, BMP)
- Alpha channel handling
- Color and grayscale images
- Texture blending modes

## Architecture

```
textbaker/
├── app/              # GUI application
│   └── main_window.py
├── core/             # Image processing
│   └── image_processing.py
├── widgets/          # Qt UI components
│   ├── dialogs.py
│   └── graphics.py
├── utils/            # Utilities
│   ├── logging.py
│   └── helpers.py
└── cli.py            # CLI entry point
```

## Author

**Ramkrishna Acharya**

---

Continue to [Dataset Structure](dataset.md) to learn how to organize your character images.
