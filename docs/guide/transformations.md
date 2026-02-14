# Transformations

TextBaker applies various transformations to create realistic synthetic text images.

## Character-Level Transformations

These are applied to individual characters during generation.

### Rotation

Rotates each character by a random angle within the specified range.

```
Original:  A    →    Rotated:  ∠A
```

**Parameters:**

- Min Rotation: -45° to 45°
- Max Rotation: -45° to 45°

**Use Cases:**

- Simulate handwriting variation
- Add natural inconsistency
- Test rotation-invariant OCR models

### Perspective

Applies perspective distortion to simulate 3D viewing angles.

```
Original:  A    →    Perspective:  /A\
```

**Parameters:**

- Min Perspective: 0° to 45°
- Max Perspective: 0° to 45°

**Directions:** Randomly chosen from left, right, top, bottom.

### Scaling

Resizes characters by a random factor.

```
Original:  A    →    Scaled:  A (larger/smaller)
```

**Parameters:**

- Min Scale: 0.3x to 2.0x
- Max Scale: 0.3x to 2.0x

## Text-Level Transformations

Applied to the entire text composite after character assembly.

### Text Perspective Slider

Interactive slider to apply horizontal perspective to the whole text.

```
Range: -45° to +45°
```

**Positive angle:** Text appears to recede on the right
**Negative angle:** Text appears to recede on the left

### Interactive Transform

In the GUI, you can manually:

1. **Move** - Drag the text anywhere on the canvas
2. **Rotate** - Drag the blue rotation handle
3. **Resize** - Drag corner handles

### Reset Transform

Click "Reset Transform" to restore the text to its original state.

## Texture Application

### No Texture Mode

Characters retain their original grayscale values or receive random RGB coloring.

### Per-Character Texture

Each character is independently textured:

1. Character mask extracted
2. Texture region selected
3. Texture applied through mask
4. Result composited

### Whole-Text Texture

The entire text composite is textured:

1. All characters assembled
2. Combined mask created
3. Single texture applied
4. Uniform appearance achieved

## Color Transformations

When random colors are enabled:

```python
# For each pixel with intensity I (0-255):
R_out = I * (random in [min_r, max_r]) / 255
G_out = I * (random in [min_g, max_g]) / 255
B_out = I * (random in [min_b, max_b]) / 255
```

## Spacing Transformations

### Horizontal Margin

Random spacing between adjacent characters.

```
A[margin]B[margin]C
```

### Vertical Offset

Random vertical displacement for each character.

```
    A
  B
      C
```

Creates a "bouncy" handwritten effect.

## Best Practices

### For Printed Text OCR

- Low rotation (±5°)
- No perspective
- Consistent scale (0.95-1.05)
- Small margins (2-5 px)
- No vertical offset

### For Handwritten Text OCR

- Higher rotation (±15°)
- Moderate perspective (0-10°)
- Variable scale (0.8-1.3)
- Variable margins (2-15 px)
- Vertical offset (10-20 px)

### For Document Scanning OCR

- Low rotation (±3°)
- Perspective for page curl
- Consistent scale
- Use document backgrounds
- Apply paper textures

---

## API Reference

For programmatic access to transformations, see the [ImageProcessor API](../reference/textbaker/core/image_processing.md).
