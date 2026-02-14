# Dataset Structure

TextBaker expects your character images to be organized in a specific folder structure.

## Required Structure

```
dataset/
├── A/
│   ├── img001.png
│   ├── img002.png
│   └── ...
├── B/
│   ├── img001.png
│   └── ...
├── 0/
│   ├── img001.png
│   └── ...
├── 1/
│   └── ...
└── ...
```

Each subfolder name represents a character/label, and contains image samples of that character.

## Folder Naming

The folder name is used as the character label:

| Folder Name | Character |
|-------------|-----------|
| `A` | Letter A |
| `a` | Lowercase a |
| `0` | Digit 0 |
| `exclamation` | ! (custom name) |

!!! tip "Case Sensitivity"
    Folder names are case-sensitive. `A` and `a` are treated as different characters.

## Image Requirements

### Supported Formats

- PNG (recommended, supports transparency)
- JPG/JPEG
- BMP

### Recommended Specifications

| Property | Recommendation |
|----------|----------------|
| Size | 64x64 to 256x256 pixels |
| Background | Transparent (PNG) or white |
| Color | Grayscale or colored |
| Format | PNG with alpha channel |

### Image Processing

TextBaker automatically processes images:

1. **Loads** the image with alpha channel support
2. **Converts** to grayscale for masking
3. **Inverts** colors (assumes dark-on-light)
4. **Crops** to content bounding box
5. **Applies** transformations

## Example Dataset

Here's an example structure for digits:

```
handwritten_digits/
├── 0/
│   ├── sample_001.png
│   ├── sample_002.png
│   └── sample_003.png
├── 1/
│   ├── sample_001.png
│   └── sample_002.png
├── 2/
│   └── ...
...
└── 9/
    └── ...
```

## Multiple Styles

You can include multiple handwriting styles:

```
dataset/
├── A/
│   ├── style1_001.png
│   ├── style1_002.png
│   ├── style2_001.png
│   └── style2_002.png
└── ...
```

The more variations you include, the more diverse your generated dataset will be.

## Background Images

Background images should be placed in a separate folder:

```
backgrounds/
├── paper_texture_01.jpg
├── paper_texture_02.jpg
├── document_scan_01.png
└── ...
```

## Texture Images

Texture images for character styling:

```
textures/
├── ink_texture_01.png
├── pen_stroke_01.jpg
└── ...
```

---

Next: Learn about [Configuration](configuration.md) options.
