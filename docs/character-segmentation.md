# Character Segmentation

The Character Segmentation tool allows you to extract individual characters from images by drawing polygons around them. This is useful for creating custom character datasets from scanned documents, photos, or other sources.

## Accessing the Tool

In the TextBaker GUI, click the **"Segment a Character"** button in the left sidebar.

## Interface Overview

The Segment Character dialog provides:
- **Select Folder**: Choose a folder containing images to segment
- **Previous/Next**: Navigate between images
- **Image Display**: Scrollable, zoomable image viewer
- **Draw Polygon**: Start drawing a polygon around a character
- **Show Region**: Preview the masked and cropped region
- **Invert Color**: Option to invert the color of the cropped region before saving
- **Character Input**: Label for the segmented character
- **Save**: Save the cropped region to disk

## Controls

### Mouse Controls

| Action | Description |
|--------|-------------|
| **Left Click** | Add a point to the current polygon |
| **Right Click** | Undo the last point |
| **Double Click** | Finish the current polygon |
| **Mouse Wheel** | Zoom in/out (scroll up to zoom in, down to zoom out) |
| **[ ] Invert Color** | Toggle to invert the color of the cropped region before saving |

### Keyboard Shortcuts

The dialog remembers your last selected folder for convenience.

## Workflow

### 1. Select a Folder

Click **"Select Folder"** and choose a directory containing images. The tool will recursively scan for:
- `.png`
- `.jpg` / `.jpeg`
- `.bmp`

The dialog remembers your last selected folder, so next time it opens to the same location.

### 2. Navigate Images

Use the **Previous** and **Next** buttons to browse through the images in the selected folder.

### 3. Zoom (Optional)

Use your **mouse wheel** to zoom in and out:
- **Scroll up**: Zoom in
- **Scroll down**: Zoom out

Zooming helps you precisely select character boundaries. The image is displayed in a scrollable area, allowing you to pan when zoomed in.

### 4. Draw Polygon

1. Click the **"Draw Polygon"** button to start drawing
2. **Left-click** on the image to add points to the polygon
   - Green circles appear at each point
   - Green lines connect the points
3. **Right-click** to undo the last point if you make a mistake
4. **Double-click** when you've outlined the entire character
   - The polygon turns red when complete
   - You can draw multiple polygons on the same image if needed

**Tips:**
- Click around the character boundary to create a polygon that follows its shape
- You can have as many points as needed for complex shapes
- Multiple polygons can be drawn to select multiple regions
- Circles on the points help you see exactly where you've clicked

### 5. Show Region

Click **"Show Region"** to preview the result:
- The polygon is used as a mask
- The region is cropped to the extreme points (bounding box of the mask)
- Background is set to **black**
- The preview shows exactly what will be saved

### 6. (Optional) Invert Color

Check the **"Invert color before saving"** box if you want the cropped region to be color-inverted (useful for certain OCR or dataset needs). The preview will not show the inversion, but the saved file will be inverted if this is checked.

### 7. Enter Character Label

In the **"Enter character label"** field, type the character you just segmented. For example:
- Single characters: `A`, `B`, `1`, `2`
- Special characters: `@`, `#`, `$`
- Multi-character labels: `Aa`, `01`

### 8. Save

Click **"Save Cropped Region"**. The file will be saved as:
```
{character}_{index}.png
```

For example:
- `A_0.png`
- `A_1.png`
- `B_0.png`

## Example Use Cases

### Creating Custom Fonts

Extract characters from handwritten text or artistic fonts:
1. Take a photo of handwritten alphabet
2. Use the segmentation tool to extract each letter
3. Save them with appropriate labels
4. Use in TextBaker for synthetic text generation

### Extracting from Scanned Documents

Extract characters from scanned books or documents:
1. Scan document pages
2. Navigate to pages with clear characters
3. Segment individual characters or words
4. Build a custom character dataset

### Processing Multiple Characters

Draw multiple polygons on the same image:
1. Click "Draw Polygon"
2. Outline first character, double-click to finish
3. Click "Draw Polygon" again
4. Outline second character
5. Continue for all characters
6. Click "Show Region" to see all selected regions combined
7. Save the result

## Tips & Best Practices

### Accurate Selection
- **Zoom in** for precise selection of character boundaries
- Include a small margin around the character for better results
- Avoid including neighboring characters in the polygon

### Multiple Characters
- You can draw multiple polygons to select multiple character regions
- All selected regions are combined when you click "Show Region"

### Black Background
- The saved image has a **black background**
- Only pixels inside the polygon are preserved
- This is ideal for OCR training where background should be uniform

### Folder Organization
- Organize your source images in a logical folder structure
- The tool remembers your last folder selection
- Save segmented characters to a separate output folder

### Quality Control
- Always preview with "Show Region" before saving
- Check that the entire character is captured
- Verify no unwanted artifacts are included

## Keyboard Navigation

While the main focus is mouse-based polygon drawing, you can:
- Tab through buttons
- Enter to activate focused button
- Escape to close the dialog

## Technical Details

### File Format
- Output format: PNG (lossless)
- Color mode: BGR (OpenCV format)
- Background: Black (RGB 0,0,0)

### Polygon Processing
1. Points are collected as you click
2. On double-click, polygon is closed
3. Polygon is filled to create a binary mask
4. Bitwise AND combines mask with original image
5. Bounding box of mask is calculated
6. Region is cropped to bounding box
7. Background outside mask is set to black

### Zoom Implementation
- Zoom factor ranges from 0.1x to 10x
- Mouse wheel adjusts by factor of 1.1
- Coordinates are automatically adjusted for zoom level
- Original image coordinates are preserved

## Troubleshooting

### Can't see image
- Make sure the folder contains supported image formats
- Try clicking "Next" if the first image fails to load
- Check file permissions

### Polygon not closing
- Make sure to **double-click** to finish
- Need at least 3 points before double-clicking
- Try right-clicking to undo if you have too many points

### Wrong character selected
- Click "Draw Polygon" again to start over
- Right-click to undo recent points
- Navigate to next image and try again

### Zoom too sensitive
- Use smaller mouse wheel movements
- Reset zoom with the "Reset Zoom" button if available
- Or reload the image

## Integration with TextBaker

Segmented characters can be directly used in TextBaker:

1. Save segmented characters to a folder structure:
   ```
   my_characters/
   ├── A/
   │   ├── A_0.png
   │   └── A_1.png
   ├── B/
   │   └── B_0.png
   └── 1/
       └── 1_0.png
   ```

2. In TextBaker main window, select this folder as your **Dataset Folder**

3. Generate synthetic text using your custom segmented characters!

## See Also

- [Draw Character Tool](../drawing-canvas/) - Create characters from scratch
- [Dataset Structure](../dataset-structure/) - Organizing your character datasets
- [GUI Guide](../gui-guide/) - Complete GUI reference
