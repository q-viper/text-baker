"""
Image processing utilities for TextBaker.

Contains all OpenCV-based image manipulation functions for character processing,
transformations, texturing, and color manipulation.
"""

import os
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from textbaker.utils.random_state import rng

# Suppress OpenCV logging
os.environ["OPENCV_LOG_LEVEL"] = "FATAL"
if hasattr(cv2, "setLogLevel"):
    cv2.setLogLevel(3)


class ImageProcessor:
    """
    Image processing class for character and text manipulation.

    Handles loading, transforming, coloring, and texturing of character images
    for synthetic text generation.
    """

    def __init__(self):
        self.selected_texture_region: Optional[np.ndarray] = None
        self.texture_paths: list[Path] = []

    def load_and_process_image(self, path: Path) -> Optional[np.ndarray]:
        """
        Load an image and process it to grayscale with inverted colors.

        Args:
            path: Path to the image file.

        Returns:
            Processed grayscale image or None if loading fails.
        """
        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if img is None:
            return None

        if len(img.shape) == 3:
            if img.shape[2] == 4:
                # RGBA image
                b, g, r, alpha = cv2.split(img)
                gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
                mask = alpha > 0
                inverted = 255 - gray
                result = np.where(mask, inverted, 0).astype(np.uint8)
            elif img.shape[2] == 3:
                # RGB image
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                result = 255 - gray
        else:
            # Grayscale image
            result = 255 - img

        return result

    def render_character_with_cv2(self, char: str, char_dim: int, font_scale: float) -> np.ndarray:
        """
        Render a character using OpenCV's built-in font.

        Args:
            char: Single character to render.
            char_dim: Dimension of the output square image.
            font_scale: Font scale factor.

        Returns:
            Grayscale image with the rendered character.
        """
        img = np.zeros((char_dim, char_dim), dtype=np.uint8)

        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = max(2, int(font_scale * 2))

        (text_width, text_height), baseline = cv2.getTextSize(char, font, font_scale, thickness)

        x = (char_dim - text_width) // 2
        y = (char_dim + text_height) // 2

        cv2.putText(img, char, (x, y), font, font_scale, 255, thickness, cv2.LINE_AA)

        return img

    def apply_rotation(self, img: np.ndarray, angle: float) -> np.ndarray:
        """
        Apply rotation to an image.

        Args:
            img: Input image.
            angle: Rotation angle in degrees.

        Returns:
            Rotated image with adjusted canvas size.
        """
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int(h * sin + w * cos)
        new_h = int(h * cos + w * sin)
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]

        border_value = 0 if len(img.shape) == 2 else (0, 0, 0)
        return cv2.warpAffine(
            img, M, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=border_value
        )

    def apply_perspective(self, img: np.ndarray, angle: float) -> np.ndarray:
        """
        Apply perspective transformation to an image.

        Args:
            img: Input image.
            angle: Perspective angle in degrees.

        Returns:
            Perspective-transformed image with adjusted canvas to fit content.
        """
        h, w = img.shape[:2]
        shift = int(w * np.tan(np.radians(angle)))
        direction = rng.choice(["left", "right", "top", "bottom"])

        # Define source points (corners of original image)
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])

        # Define destination points based on direction
        if direction == "left":
            dst = np.float32([[shift, 0], [w, 0], [w, h], [0, h]])
        elif direction == "right":
            dst = np.float32([[0, 0], [w - shift, 0], [w, h], [shift, h]])
        elif direction == "top":
            dst = np.float32([[0, shift], [w, 0], [w, h], [0, h - shift]])
        else:
            dst = np.float32([[0, 0], [w, shift], [w, h - shift], [0, h]])

        # Calculate the bounding box of destination points to ensure all content fits
        min_x = int(np.min(dst[:, 0]))
        max_x = int(np.max(dst[:, 0])) + 1
        min_y = int(np.min(dst[:, 1]))
        max_y = int(np.max(dst[:, 1])) + 1

        # Adjust destination points if there are negative coordinates
        offset_x = -min(0, min_x)
        offset_y = -min(0, min_y)

        if offset_x > 0 or offset_y > 0:
            dst[:, 0] += offset_x
            dst[:, 1] += offset_y
            max_x += offset_x
            max_y += offset_y

        output_w = max_x - min_x
        output_h = max_y - min_y

        M = cv2.getPerspectiveTransform(src, dst)
        border_value = 0 if len(img.shape) == 2 else (0, 0, 0)
        return cv2.warpPerspective(
            img, M, (output_w, output_h), borderMode=cv2.BORDER_CONSTANT, borderValue=border_value
        )

    def apply_perspective_to_image(self, img: np.ndarray, angle: float) -> np.ndarray:
        """
        Apply horizontal perspective transformation.

        Args:
            img: Input image.
            angle: Perspective angle in degrees.

        Returns:
            Perspective-transformed image.
        """
        if angle == 0:
            return img

        h, w = img.shape[:2]
        shift = int(w * 0.3 * np.sin(np.radians(abs(angle))))

        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])

        if angle > 0:
            dst = np.float32([[shift, 0], [w, 0], [w - shift, h], [0, h]])
        else:
            dst = np.float32([[0, 0], [w - shift, 0], [w, h], [shift, h]])

        M = cv2.getPerspectiveTransform(src, dst)
        return cv2.warpPerspective(
            img, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0)
        )

    def resize_with_aspect_ratio(
        self, img: np.ndarray, target_size: tuple[int, int], pad_value: int = 0
    ) -> np.ndarray:
        """
        Resize image maintaining aspect ratio and pad to target size.

        Args:
            img: Input image.
            target_size: Target (width, height) tuple.
            pad_value: Value to use for padding.

        Returns:
            Resized and padded image.
        """
        h, w = img.shape[:2]
        target_w, target_h = target_size
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

        if len(img.shape) == 2:
            canvas = np.full((target_h, target_w), pad_value, dtype=np.uint8)
        else:
            canvas = np.full((target_h, target_w, img.shape[2]), pad_value, dtype=np.uint8)

        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        canvas[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = resized
        return canvas

    def apply_texture(
        self, gray_img: np.ndarray, texture: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Apply texture to a grayscale image.

        Args:
            gray_img: Input grayscale image.
            texture: Texture image to apply (optional).

        Returns:
            Textured color image.
        """
        if texture is None:
            if self.selected_texture_region is not None:
                texture = self.selected_texture_region
            elif self.texture_paths:
                texture_path = rng.choice(self.texture_paths)
                texture = cv2.imread(str(texture_path), cv2.IMREAD_COLOR)
                if texture is None:
                    return cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
            else:
                return cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

        h, w = gray_img.shape
        texture_resized = cv2.resize(texture, (w, h), interpolation=cv2.INTER_LINEAR)
        mask = gray_img.astype(np.float32) / 255.0

        textured = np.zeros((h, w, 3), dtype=np.uint8)
        for c in range(3):
            textured[:, :, c] = (texture_resized[:, :, c] * mask).astype(np.uint8)

        return textured

    def apply_random_color(
        self,
        gray_img: np.ndarray,
        color_range: Optional[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = None,
    ) -> np.ndarray:
        """
        Apply random color to a grayscale image.

        Args:
            gray_img: Input grayscale image.
            color_range: Optional ((min_r, max_r), (min_g, max_g), (min_b, max_b)) ranges.

        Returns:
            Colored image.
        """
        if color_range is None:
            return cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

        (min_r, max_r), (min_g, max_g), (min_b, max_b) = color_range
        r = rng.randint(min_r, max_r)
        g = rng.randint(min_g, max_g)
        b = rng.randint(min_b, max_b)

        h, w = gray_img.shape
        colored = np.zeros((h, w, 3), dtype=np.uint8)
        normalized = gray_img.astype(np.float32) / 255.0

        colored[:, :, 2] = (normalized * r).astype(np.uint8)
        colored[:, :, 1] = (normalized * g).astype(np.uint8)
        colored[:, :, 0] = (normalized * b).astype(np.uint8)

        return colored

    def color_to_rgba_transparent(self, color_img: np.ndarray) -> np.ndarray:
        """
        Convert color image to RGBA with transparent background.

        Args:
            color_img: Input BGR color image.

        Returns:
            RGBA image with transparency.
        """
        h, w = color_img.shape[:2]
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[:, :, :3] = color_img
        rgba[:, :, 3] = np.max(color_img, axis=2)
        return rgba

    def crop_resize_pad_char(
        self,
        img: np.ndarray,
        char_dim: int,
        rotation_range: tuple[float, float] = (0, 0),
        perspective_range: tuple[float, float] = (0, 0),
        scale_range: tuple[float, float] = (1.0, 1.0),
        apply_texture: bool = False,
        color_range: Optional[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = None,
    ) -> np.ndarray:
        """
        Crop, augment, and resize a character image.

        Args:
            img: Input character image.
            char_dim: Target dimension for square output.
            rotation_range: (min, max) rotation angles.
            perspective_range: (min, max) perspective angles.
            scale_range: (min, max) scale factors.
            apply_texture: Whether to apply texture.
            color_range: Optional color range for random coloring.

        Returns:
            Processed character image.
        """
        # First, do an initial crop to remove excessive whitespace
        coords = cv2.findNonZero(img)
        if coords is None:
            return np.zeros((char_dim, char_dim, 3), dtype=np.uint8)

        x, y, w, h = cv2.boundingRect(coords)
        cropped = img[y : y + h, x : x + w]

        # Apply rotation
        min_rot, max_rot = rotation_range
        if min_rot != 0 or max_rot != 0:
            angle = rng.uniform(min_rot, max_rot)
            cropped = self.apply_rotation(cropped, angle)

        # Apply perspective
        min_persp, max_persp = perspective_range
        if max_persp > 0:
            angle = rng.uniform(min_persp, max_persp)
            cropped = self.apply_perspective(cropped, angle)

        # Crop again after transformations to remove any padding added by transformations
        # This ensures we crop based on the warped version
        coords = cv2.findNonZero(cropped)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            cropped = cropped[y : y + h, x : x + w]

        # Apply texture or color
        if apply_texture:
            cropped = self.apply_texture(cropped)
        else:
            cropped = self.apply_random_color(cropped, color_range)

        if len(cropped.shape) == 2:
            cropped = cv2.cvtColor(cropped, cv2.COLOR_GRAY2BGR)

        # Apply scale
        min_scale, max_scale = scale_range
        scale = rng.uniform(min_scale, max_scale)
        new_w = max(1, int(cropped.shape[1] * scale))
        new_h = max(1, int(cropped.shape[0] * scale))
        resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)

        return self.resize_with_aspect_ratio(resized, (char_dim, char_dim), pad_value=0)
