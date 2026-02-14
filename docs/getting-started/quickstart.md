# Quick Start

This guide will help you get started with TextBaker in just a few minutes.

## Launch the Application

After [installation](installation.md), simply run:

```bash
textbaker
```

This opens the TextBaker GUI application.

## Basic Workflow

### 1. Set Up Folders

Click the folder buttons on the left panel to set:

- **Dataset Folder**: Contains subfolders with character images
- **Output Folder**: Where generated images will be saved
- **Background Folder**: Contains background images
- **Texture Folder**: Contains texture images (optional)

### 2. Configure Generation Parameters

On the right panel, adjust:

- **Character Dimension**: Size of each character (32-256 px)
- **Character Count**: Number of characters per image
- **Scale Range**: Random scaling factor
- **Rotation Range**: Random rotation angle
- **Perspective Range**: Random perspective distortion

### 3. Generate Text

Click **"🎲 Generate Random Text"** to create a synthetic text image.

### 4. Add Background

Click **"🖼️ Select Random Background"** to add a random background.

### 5. Adjust and Save

- Drag the text to position it
- Use the rotation handle to rotate
- Drag corners to resize
- Click **"💾 Save Image"** to export

## Using Custom Text

1. Enter characters in the "Character Pool" field
2. Check "Randomize from pool" to generate random combinations
3. Set the desired length range
4. Click Generate

## Example

```bash
# Launch with preset folders
textbaker \
    --dataset ./my_dataset \
    --output ./generated \
    --backgrounds ./backgrounds \
    --textures ./textures
```

## Next Steps

- Learn about [CLI Usage](cli.md)
- Understand [Dataset Structure](../guide/dataset.md)
- Explore [Transformations](../guide/transformations.md)
