# Configuration

TextBaker provides extensive configuration options through the GUI.

## Generation Parameters

### Character Dimension

Controls the size of each character cell.

| Setting | Range | Default | Description |
|---------|-------|---------|-------------|
| Char Dimension | 32-256 px | 64 px | Size of character bounding box |

### Character Count

Number of characters to generate per image.

| Setting | Range | Default |
|---------|-------|---------|
| Min Count | 1-20 | 4 |
| Max Count | 1-20 | 6 |

### Scale

Random scaling applied to each character.

| Setting | Range | Default |
|---------|-------|---------|
| Min Scale | 0.3-2.0 | 0.9 |
| Max Scale | 0.3-2.0 | 1.2 |

### Rotation

Random rotation angle for each character.

| Setting | Range | Default |
|---------|-------|---------|
| Min Rotation | -45° to 45° | -15° |
| Max Rotation | -45° to 45° | 15° |

### Perspective

Random perspective distortion.

| Setting | Range | Default |
|---------|-------|---------|
| Min Perspective | 0° to 45° | 0° |
| Max Perspective | 0° to 45° | 15° |

### Margins

Spacing between characters and vertical offset.

| Setting | Range | Default | Description |
|---------|-------|---------|-------------|
| H-Margin Min | 0-50 px | 2 px | Min horizontal spacing |
| H-Margin Max | 0-50 px | 10 px | Max horizontal spacing |
| V-Offset | 0-64 px | 20 px | Max vertical offset |
| Canvas Height | 64-256 px | 128 px | Total canvas height |

### Font Scale

For rendering characters not in the dataset.

| Setting | Range | Default |
|---------|-------|---------|
| Font Scale | 0.5-3.0 | 1.5 |

## Texture Modes

### No Texture

Uses original image colors or applies random coloring.

### Per Character

Applies texture independently to each character.

### Whole Text

Applies texture to the entire text composite.

## Color Options

When "Enable Random Colors" is checked:

| Channel | Range | Default Min | Default Max |
|---------|-------|-------------|-------------|
| Red | 0-255 | 100 | 255 |
| Green | 0-255 | 100 | 255 |
| Blue | 0-255 | 100 | 255 |

## Custom Text

### Character Pool

Enter specific characters to use:

```
ABC123
```

### Randomize from Pool

When enabled, generates random combinations from the pool.

| Setting | Range | Default |
|---------|-------|---------|
| Min Length | 1-30 | 5 |
| Max Length | 1-30 | 10 |

## Output Options

### Crop to Text

When enabled, saves only the text bounding box instead of the full canvas with background.

---

Next: Learn about [Transformations](transformations.md).
