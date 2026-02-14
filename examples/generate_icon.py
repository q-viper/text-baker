"""
Generate TextBaker Icon

This example demonstrates how to generate the TextBaker application icon
with handwritten-style text using OpenCV.

Usage:
    python examples/generate_icon.py

Output:
    Icons are saved to assets/ folder at various sizes.
"""

import sys
from pathlib import Path

import cv2
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from textbaker.ui_config import ICON_CONFIG


def generate_textbaker_icon(size: int = 256) -> np.ndarray:
    """Generate a TextBaker icon with handwritten-style text.

    The icon shows a stylized bread slice with handwritten "TB" text,
    representing text being "baked" into images.

    Args:
        size: Icon size in pixels (square)

    Returns:
        BGRA numpy array of the icon
    """
    # Create canvas with transparent background
    img = np.zeros((size, size, 4), dtype=np.uint8)

    padding = max(2, size // 16)

    # Draw bread/toast shape - rounded rectangle
    bread_color = ICON_CONFIG.bread_color
    crust_color = ICON_CONFIG.crust_color

    # Main bread body
    x1, y1 = padding, padding
    x2, y2 = size - padding, size - padding

    # Simple rectangle for small sizes, more detail for larger
    if size <= 32:
        # Simple bread shape for small icons
        cv2.rectangle(img, (x1, y1), (x2, y2), bread_color, -1)
        cv2.rectangle(img, (x1, y1), (x2, y2), crust_color, 1)
    else:
        # Draw rounded bread shape
        cv2.rectangle(img, (x1 + 5, y1), (x2 - 5, y2 - 5), bread_color, -1)
        cv2.rectangle(img, (x1, y1 + 5), (x2, y2 - 10), bread_color, -1)

        # Rounded top (like bread top) - only for larger icons
        if size >= ICON_CONFIG.min_size_for_ellipse:
            ellipse_w = max(1, size // 2 - padding - 5)
            ellipse_h = max(1, size // 8)
            cv2.ellipse(
                img, (size // 2, y1 + 5), (ellipse_w, ellipse_h), 0, 180, 360, bread_color, -1
            )

        # Crust border
        thickness = max(1, size // 50)
        cv2.rectangle(img, (x1 + 5, y1), (x2 - 5, y2 - 5), crust_color, thickness)

        if size >= ICON_CONFIG.min_size_for_ellipse:
            cv2.ellipse(
                img,
                (size // 2, y1 + 5),
                (ellipse_w, ellipse_h),
                0,
                180,
                360,
                crust_color,
                thickness,
            )

        # Inner lighter area (soft bread inside) - only for larger icons
        if size >= ICON_CONFIG.min_size_for_inner:
            inner_color = ICON_CONFIG.bread_light_color
            inner_pad = size // 8
            cv2.rectangle(
                img,
                (x1 + inner_pad, y1 + inner_pad),
                (x2 - inner_pad, y2 - inner_pad - 5),
                inner_color,
                -1,
            )

    # Draw handwritten-style "TB" text
    draw_handwritten_text(img, size)

    # Add some texture dots (like bread texture) - only for larger sizes
    if size >= ICON_CONFIG.min_size_for_texture:
        np.random.seed(42)
        inner_pad = size // 8
        num_dots = max(1, size // 20)
        for _ in range(num_dots):
            dot_x = np.random.randint(x1 + inner_pad + 10, x2 - inner_pad - 10)
            dot_y = np.random.randint(y1 + inner_pad + 10, y2 - inner_pad - 20)
            dot_size = max(1, size // 120)
            cv2.circle(img, (dot_x, dot_y), dot_size, (80, 160, 220, 100), -1)

    return img


def draw_handwritten_text(img: np.ndarray, size: int):
    """Draw handwritten-style 'TB' text on the icon."""
    text_color = ICON_CONFIG.text_color
    shadow_color = ICON_CONFIG.text_shadow_color

    center_x = size // 2
    center_y = size // 2

    # Scale factor based on icon size
    scale = size / 256.0

    if size < 32:
        # Very small - just use simple text
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.3, size / 100)
        thickness = max(1, size // 40)
        (text_w, text_h), _ = cv2.getTextSize("TB", font, font_scale, thickness)
        text_x = (size - text_w) // 2
        text_y = (size + text_h) // 2
        cv2.putText(
            img, "TB", (text_x, text_y), font, font_scale, text_color, thickness, cv2.LINE_AA
        )
        return

    # Handwritten-style strokes for 'T' and 'B'
    stroke_thickness = max(2, int(4 * scale))

    # Calculate positions - T on left, B on right
    t_center_x = int(center_x - 25 * scale)
    b_center_x = int(center_x + 25 * scale)

    # Draw shadow first (only for larger icons)
    if size >= ICON_CONFIG.min_size_for_shadow:
        shadow_offset = max(1, int(3 * scale))
        draw_handwritten_T(
            img,
            t_center_x + shadow_offset,
            center_y + shadow_offset,
            scale,
            shadow_color,
            stroke_thickness,
        )
        draw_handwritten_B(
            img,
            b_center_x + shadow_offset,
            center_y + shadow_offset,
            scale,
            shadow_color,
            stroke_thickness,
        )

    # Draw main text
    draw_handwritten_T(img, t_center_x, center_y, scale, text_color, stroke_thickness)
    draw_handwritten_B(img, b_center_x, center_y, scale, text_color, stroke_thickness)


def draw_handwritten_T(
    img: np.ndarray, cx: int, cy: int, scale: float, color: tuple, thickness: int
):
    """Draw a handwritten-style 'T' letter."""
    h = int(50 * scale)  # height
    w = int(35 * scale)  # width of top bar

    # Top horizontal bar - slightly curved
    pts_top = []
    for i in range(10):
        t = i / 9.0
        x = int(cx - w / 2 + w * t)
        y = int(cy - h / 2 + 3 * scale * np.sin(t * np.pi))
        pts_top.append([x, y])
    pts_top = np.array(pts_top, dtype=np.int32)
    cv2.polylines(img, [pts_top], False, color, thickness, cv2.LINE_AA)

    # Vertical stem - slightly tilted
    pts_stem = []
    for i in range(10):
        t = i / 9.0
        x = int(cx + 2 * scale * np.sin(t * np.pi * 0.5))
        y = int(cy - h / 2 + h * t)
        pts_stem.append([x, y])
    pts_stem = np.array(pts_stem, dtype=np.int32)
    cv2.polylines(img, [pts_stem], False, color, thickness, cv2.LINE_AA)


def draw_handwritten_B(
    img: np.ndarray, cx: int, cy: int, scale: float, color: tuple, thickness: int
):
    """Draw a handwritten-style 'B' letter."""
    h = int(50 * scale)  # height
    w = int(25 * scale)  # width of bumps

    # Vertical stem - slightly curved
    pts_stem = []
    for i in range(10):
        t = i / 9.0
        x = int(cx - w / 2 + 3 * scale * np.sin(t * np.pi * 0.3))
        y = int(cy - h / 2 + h * t)
        pts_stem.append([x, y])
    pts_stem = np.array(pts_stem, dtype=np.int32)
    cv2.polylines(img, [pts_stem], False, color, thickness, cv2.LINE_AA)

    # Top bump
    pts_top_bump = []
    for i in range(15):
        t = i / 14.0
        angle = -np.pi / 2 + np.pi * t
        x = int(cx - w / 2 + w / 2 + (w * 0.6) * np.cos(angle))
        y = int(cy - h / 4 + (h / 4 * 0.8) * np.sin(angle))
        pts_top_bump.append([x, y])
    pts_top_bump = np.array(pts_top_bump, dtype=np.int32)
    cv2.polylines(img, [pts_top_bump], False, color, thickness, cv2.LINE_AA)

    # Bottom bump (slightly larger)
    pts_bot_bump = []
    for i in range(15):
        t = i / 14.0
        angle = -np.pi / 2 + np.pi * t
        x = int(cx - w / 2 + w / 2 + (w * 0.7) * np.cos(angle))
        y = int(cy + h / 4 + (h / 4 * 0.9) * np.sin(angle))
        pts_bot_bump.append([x, y])
    pts_bot_bump = np.array(pts_bot_bump, dtype=np.int32)
    cv2.polylines(img, [pts_bot_bump], False, color, thickness, cv2.LINE_AA)


def main():
    """Generate and save icons at multiple sizes."""
    # Create assets directory if needed
    assets_dir = Path(__file__).parent.parent / "assets"
    assets_dir.mkdir(exist_ok=True)

    # Generate icons in multiple sizes
    sizes = list(ICON_CONFIG.sizes)

    print("Generating TextBaker icons...")
    for size in sizes:
        icon = generate_textbaker_icon(size)
        output_path = assets_dir / f"icon_{size}.png"
        cv2.imwrite(str(output_path), icon)
        print(f"  ✓ {output_path}")

    # Also save the main icon
    main_icon = generate_textbaker_icon(256)
    main_path = assets_dir / "icon.png"
    cv2.imwrite(str(main_path), main_icon)
    print(f"  ✓ {main_path} (main)")

    print("\nDone! Icons saved to assets/ folder.")


if __name__ == "__main__":
    main()
