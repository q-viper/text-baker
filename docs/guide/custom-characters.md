# Custom Character Drawing

TextBaker includes a built-in drawing canvas that allows you to create custom characters directly in the application without needing external image editing software.

## Overview

The drawing canvas provides a simple yet powerful interface for creating character images that can be immediately used in your text generation pipeline.

## Opening the Drawing Canvas

1. Launch the TextBaker GUI application
2. Click the **"✏️ Draw Character"** button (located above the Custom Text field)
3. The drawing canvas dialog will open

## Drawing Tools

### 🖊️ Pen Tool
- **Purpose**: Draw characters with customizable pen width and color
- **Cursor**: Crosshair (for precise drawing)
- **Controls**: 
  - Adjust pen width using the spin box (1-50px)
  - Use mouse wheel to increase/decrease pen width (±2px per scroll)
  - Click "🎨 Pick Color" to choose drawing color

### 🧹 Eraser Tool
- **Purpose**: Erase parts of your drawing
- **Cursor**: Pointing hand
- **Note**: Eraser width is 2x the pen width

### 🎨 Fill Background
- Opens a color picker to fill the entire canvas background
- Useful for creating characters on colored backgrounds

### 🗑️ Clear Canvas
- Clears the entire canvas (asks for confirmation)
- Resets to the current background color

## Keyboard Shortcuts

- **Delete Key**: Clears the canvas (with confirmation dialog)
  - Useful for quickly starting over without reaching for the mouse

## Saving Characters

1. Draw your character on the canvas
2. Enter a label in the "Character Label" field (e.g., "A", "5", "@", "abc")
   - Can be single or multiple characters (max 10)
3. Click **"💾 Save Character"**
4. The character is saved to `.textbaker/custom_characters/` in your current working directory
5. The application will automatically rescan the dataset and your character becomes available for use
6. The dialog stays open so you can draw more characters

## File Organization

Custom characters are saved in this structure:

```
.textbaker/
└── custom_characters/
    ├── A/
    │   ├── drawn_0001.png
    │   └── drawn_0002.png
    ├── B/
    │   └── drawn_0001.png
    └── @/
        └── drawn_0001.png
```

- Each character label gets its own folder
- Files are automatically numbered (drawn_0001.png, drawn_0002.png, etc.)
- Images are saved at 512×512 pixels in PNG format

## Tips & Best Practices

1. **Canvas is Empty Check**: The application validates that you've drawn something before saving
2. **Continuous Drawing**: Keep the dialog open to draw multiple characters in one session
3. **Mouse Wheel**: Use scroll wheel for quick pen size adjustments while drawing
4. **Color Switching**: Picking a new color automatically switches back to Pen mode
5. **Clean Slate**: Use Delete key for quick canvas clearing when making mistakes

## Performance & Feedback

- **Non-blocking Save**: Character saves are completely async using background thread (< 50ms perceived time)
- **Progress Bar**: Animated progress indicator shows during save operation
- **Success Confirmation**: Green status message appears for 3 seconds showing filename
- **Incremental Dataset Updates**: Only the new character is added to the list (no full rescan)
- **Visual Feedback**: 
  - Success messages appear in green banner on the drawing window
  - Missing character label: red border on input field
  - Empty canvas: warning in window title
  - All indicators reset automatically on successful save
- **Zero Freezing**: Dialog remains fully responsive during all operations
- **Real-time Updates**: Character appears in main app list within 50ms

## Example Workflow

1. Click "✏️ Draw Character"
2. Adjust pen width to 15px using mouse wheel
3. Draw the letter "X"
4. Enter "X" in the Character Label field
5. Click "💾 Save Character"
6. **Progress bar appears** with "Saving..." message
7. **Green success banner shows**: "✅ Saved 'X' as drawn_0001.png"
8. Banner auto-hides after 3 seconds
9. Character "X" appears in the main app's character list
10. Draw the letter "Y" on the same canvas
11. Enter "Y" and save again
12. Process repeats instantly with no freezing
13. Close dialog when finished

Your custom characters are now available in the character selection list and can be used like any other character in the dataset!
