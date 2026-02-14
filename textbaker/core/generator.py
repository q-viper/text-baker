"""
TextGenerator - Programmatic text image generation.

This module provides a class for generating text images without using the GUI.
It can be used as a library for batch processing or integration into other applications.
"""

import hashlib
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from ..utils.logging import get_logger
from ..utils.random_state import rng
from .configs import DEFAULT_CONFIG, GeneratorConfig
from .defs import CharacterImage, GenerationResult

logger = get_logger(__name__)


class TextGenerator:
    """Programmatic text image generator.

    This class provides an API for generating text images without using the GUI.
    It's designed for library usage, batch processing, and integration.

    Example:
        ```python
        from textbaker import TextGenerator, GeneratorConfig

        # Simple usage with defaults
        generator = TextGenerator()
        result = generator.generate("hello")
        cv2.imwrite("hello.png", result.image)

        # With custom config
        config = GeneratorConfig(
            seed=42,
            spacing=5,
        )
        generator = TextGenerator(config)

        # Generate multiple samples
        for i in range(10):
            result = generator.generate_random()
            generator.save(result, f"sample_{i}.png")
        ```
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """Initialize the text generator.

        Args:
            config: Generator configuration. Uses defaults if not provided.
        """
        self.config = config or DEFAULT_CONFIG
        self._char_images: dict[str, list[CharacterImage]] = {}
        self._backgrounds: list[Path] = []
        self._textures: list[Path] = []
        self._initialized = False

        # Set seed
        rng.seed(self.config.seed)
        logger.info(f"TextGenerator initialized with seed {self.config.seed}")

    def initialize(self) -> None:
        """Load dataset, backgrounds, and textures.

        Call this method before generating images, or let it be called
        automatically on first generation.
        """
        if self._initialized:
            return

        self._load_dataset()
        self._load_backgrounds()
        self._load_textures()
        self._initialized = True
        logger.info(f"Loaded {len(self._char_images)} character classes")

    def _load_dataset(self) -> None:
        """Load character images from dataset directory."""
        dataset_dir = Path(self.config.dataset.dataset_dir)
        if not dataset_dir.exists():
            logger.warning(f"Dataset directory not found: {dataset_dir}")
            return

        extensions = set(self.config.dataset.extensions)

        if self.config.dataset.recursive:
            # Recursive scan - parent folder is label
            for label_dir in dataset_dir.iterdir():
                if label_dir.is_dir():
                    label = label_dir.name
                    self._char_images[label] = []
                    for img_path in label_dir.rglob("*"):
                        if img_path.suffix.lower() in extensions:
                            self._char_images[label].append(
                                CharacterImage(path=img_path, label=label)
                            )
        else:
            # Flat scan - filename is label
            for img_path in dataset_dir.iterdir():
                if img_path.suffix.lower() in extensions:
                    label = img_path.stem
                    if label not in self._char_images:
                        self._char_images[label] = []
                    self._char_images[label].append(CharacterImage(path=img_path, label=label))

    def _load_backgrounds(self) -> None:
        """Load background image paths."""
        if not self.config.background.enabled:
            return

        bg_dir = self.config.background.background_dir
        if bg_dir and bg_dir.exists():
            extensions = {".png", ".jpg", ".jpeg", ".bmp"}
            self._backgrounds = [p for p in bg_dir.iterdir() if p.suffix.lower() in extensions]

    def _load_textures(self) -> None:
        """Load texture image paths."""
        if not self.config.texture.enabled:
            return

        tex_dir = self.config.texture.texture_dir
        if tex_dir and tex_dir.exists():
            extensions = {".png", ".jpg", ".jpeg", ".bmp"}
            self._textures = [p for p in tex_dir.iterdir() if p.suffix.lower() in extensions]

    @property
    def available_characters(self) -> list[str]:
        """Get list of available character labels."""
        if not self._initialized:
            self.initialize()
        return list(self._char_images.keys())

    def _render_char_fallback(self, char: str) -> np.ndarray:
        """Render a character using cv2.putText as fallback when not in dataset.

        Uses character config for width, height, font, and thickness.

        Args:
            char: Character to render

        Returns:
            BGRA image with the rendered character
        """
        char_config = self.config.character
        width = char_config.width
        height = char_config.height

        # Create transparent image
        img = np.zeros((height, width, 4), dtype=np.uint8)

        # Get font settings from config
        font = char_config.get_cv2_font()
        thickness = char_config.thickness

        # Calculate font scale to fit in the given size
        # Start with a base scale and adjust
        font_scale = min(width, height) / 40

        # Get text size and adjust scale if needed
        (text_w, text_h), baseline = cv2.getTextSize(char, font, font_scale, thickness)

        # Scale down if text is too big
        if text_w > width * 0.9 or text_h > height * 0.9:
            scale_factor = min(width * 0.9 / text_w, height * 0.9 / text_h)
            font_scale *= scale_factor
            (text_w, text_h), baseline = cv2.getTextSize(char, font, font_scale, thickness)

        # Calculate position to center text
        x = (width - text_w) // 2
        y = (height + text_h) // 2 - baseline // 2

        # Draw white text with full alpha
        cv2.putText(
            img, char, (x, y), font, font_scale, (255, 255, 255, 255), thickness, cv2.LINE_AA
        )

        return img

    def generate(self, text: str) -> GenerationResult:
        """Generate an image for the given text.

        Args:
            text: Text to generate image for

        Returns:
            GenerationResult with image, text, and labels
        """
        if not self._initialized:
            self.initialize()

        if not text:
            raise ValueError("Text cannot be empty")

        # Check for missing characters and warn
        missing = {c for c in text if c not in self._char_images}
        if missing:
            logger.warning(f"Characters not in dataset (will use fallback): {sorted(missing)}")

        # Generate character images
        char_imgs = []
        labels = []

        for char in text:
            if char in self._char_images and self._char_images[char]:
                # Use image from dataset
                char_img = rng.choice(self._char_images[char])
                img = cv2.imread(str(char_img.path), cv2.IMREAD_UNCHANGED)

                if img is None:
                    logger.warning(f"Failed to load image: {char_img.path}, using fallback")
                    img = self._render_char_fallback(char)
            else:
                # Use cv2 fallback for missing characters
                img = self._render_char_fallback(char)

            # Apply transforms
            img = self._apply_transforms(img)

            # Apply color
            if self.config.color.random_color:
                img = self._apply_random_color(img)
            elif self.config.color.fixed_color:
                img = self._apply_fixed_color(img, self.config.color.fixed_color)

            char_imgs.append(img)
            labels.append(char)

        # Combine images horizontally
        composite = self._combine_images(char_imgs)

        # Apply perspective to composite
        composite = self._apply_perspective(composite)

        # Apply texture
        if self.config.texture.enabled and self._textures:
            composite = self._apply_texture(composite)

        # Apply background
        if self.config.background.enabled:
            composite = self._apply_background(composite)

        return GenerationResult(
            image=composite,
            text=text,
            labels=labels,
            seed=rng.current_seed,
            params={
                "spacing": self.config.spacing,
                "transform": self.config.transform.model_dump(),
            },
        )

    def generate_random(self, length: Optional[int] = None) -> GenerationResult:
        """Generate a random text image.

        Args:
            length: Text length. If None, randomly chosen from config range.

        Returns:
            GenerationResult with generated image
        """
        if not self._initialized:
            self.initialize()

        if not self._char_images:
            raise ValueError("No characters loaded from dataset")

        if length is None:
            length = rng.randint(*self.config.text_length)

        available = list(self._char_images.keys())
        text = "".join(rng.choices(available, k=length))

        return self.generate(text)

    def _apply_transforms(self, img: np.ndarray) -> np.ndarray:
        """Apply random transformations to image."""
        h, w = img.shape[:2]

        # Rotation
        if self.config.transform.rotation_range != (0.0, 0.0):
            angle = rng.uniform(*self.config.transform.rotation_range)
            center = (w // 2, h // 2)
            matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
            img = cv2.warpAffine(
                img,
                matrix,
                (w, h),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0, 0),
            )

        # Scale
        if self.config.transform.scale_range != (1.0, 1.0):
            scale = rng.uniform(*self.config.transform.scale_range)
            new_w, new_h = int(w * scale), int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        # Shear
        if self.config.transform.shear_range != (0.0, 0.0):
            shear = rng.uniform(*self.config.transform.shear_range)
            shear_rad = np.deg2rad(shear)
            shear_matrix = np.array([[1, np.tan(shear_rad), 0], [0, 1, 0]], dtype=np.float32)
            img = cv2.warpAffine(
                img,
                shear_matrix,
                (w, h),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_CONSTANT,
                borderValue=(0, 0, 0, 0),
            )

        return img

    def _apply_perspective(self, img: np.ndarray) -> np.ndarray:
        """Apply perspective transformation to the composite image."""
        if self.config.transform.perspective_range == (0.0, 0.0):
            return img

        h, w = img.shape[:2]
        perspective = rng.uniform(*self.config.transform.perspective_range)

        if perspective == 0:
            return img

        # Calculate perspective transformation
        # Perspective factor determines how much the top/bottom edges shrink
        factor = perspective * 0.1  # Scale down the effect

        # Source points (corners of original image)
        src_pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]])

        # Destination points with perspective effect
        offset = int(w * factor)
        if rng.uniform() > 0.5:
            # Top narrower (text tilted back)
            dst_pts = np.float32([[offset, 0], [w - offset, 0], [w, h], [0, h]])
        else:
            # Bottom narrower (text tilted forward)
            dst_pts = np.float32([[0, 0], [w, 0], [w - offset, h], [offset, h]])

        matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
        img = cv2.warpPerspective(
            img,
            matrix,
            (w, h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0, 0),
        )

        return img

    def _apply_random_color(self, img: np.ndarray) -> np.ndarray:
        """Apply random color to image."""
        if len(img.shape) < 3:
            return img

        r = rng.randint(*self.config.color.color_range_r)
        g = rng.randint(*self.config.color.color_range_g)
        b = rng.randint(*self.config.color.color_range_b)

        colored = img.copy()
        if img.shape[2] == 4:
            # RGBA - preserve alpha
            mask = img[:, :, 3] > 0
            colored[mask, 0] = b
            colored[mask, 1] = g
            colored[mask, 2] = r
        else:
            # RGB
            mask = np.any(img > 0, axis=2)
            colored[mask] = [b, g, r]

        return colored

    def _apply_fixed_color(self, img: np.ndarray, color: tuple[int, int, int]) -> np.ndarray:
        """Apply fixed color to image."""
        if len(img.shape) < 3:
            return img

        r, g, b = color
        colored = img.copy()

        if img.shape[2] == 4:
            mask = img[:, :, 3] > 0
            colored[mask, 0] = b
            colored[mask, 1] = g
            colored[mask, 2] = r
        else:
            mask = np.any(img > 0, axis=2)
            colored[mask] = [b, g, r]

        return colored

    def _combine_images(self, images: list[np.ndarray]) -> np.ndarray:
        """Combine character images horizontally."""
        if not images:
            return np.zeros((100, 100, 4), dtype=np.uint8)

        # Ensure all images have alpha channel
        processed = []
        max_h = max(img.shape[0] for img in images)

        for img in images:
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
            elif img.shape[2] == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

            # Pad to max height
            if img.shape[0] < max_h:
                pad = max_h - img.shape[0]
                img = cv2.copyMakeBorder(
                    img, pad // 2, pad - pad // 2, 0, 0, cv2.BORDER_CONSTANT, value=(0, 0, 0, 0)
                )

            processed.append(img)

        # Add spacing
        spacing = self.config.spacing
        if spacing > 0:
            spacer = np.zeros((max_h, spacing, 4), dtype=np.uint8)
            with_spacing = []
            for i, img in enumerate(processed):
                with_spacing.append(img)
                if i < len(processed) - 1:
                    with_spacing.append(spacer)
            processed = with_spacing

        return np.hstack(processed)

    def _apply_texture(self, img: np.ndarray) -> np.ndarray:
        """Apply texture to image."""
        if not self._textures:
            return img

        texture_path = rng.choice(self._textures)
        texture = cv2.imread(str(texture_path), cv2.IMREAD_UNCHANGED)

        if texture is None:
            return img

        # Resize texture to match image
        texture = cv2.resize(texture, (img.shape[1], img.shape[0]))

        # Blend based on alpha
        if img.shape[2] == 4 and texture.shape[2] >= 3:
            alpha = img[:, :, 3:4] / 255.0
            opacity = self.config.texture.opacity

            texture_rgb = texture[:, :, :3] if texture.shape[2] == 4 else texture

            img[:, :, :3] = (
                img[:, :, :3] * (1 - opacity * alpha) + texture_rgb * opacity * alpha
            ).astype(np.uint8)

        return img

    def _apply_background(self, img: np.ndarray) -> np.ndarray:
        """Apply background to image."""
        h, w = img.shape[:2]

        if self.config.background.color:
            # Solid color background
            r, g, b = self.config.background.color
            bg = np.full((h, w, 3), [b, g, r], dtype=np.uint8)
        elif self._backgrounds:
            # Random background image
            bg_path = rng.choice(self._backgrounds)
            bg = cv2.imread(str(bg_path))

            if bg is None:
                bg = np.full((h, w, 3), [255, 255, 255], dtype=np.uint8)
            else:
                # Crop/resize to fit
                if self.config.background.random_crop and bg.shape[0] >= h and bg.shape[1] >= w:
                    y = rng.randint(0, bg.shape[0] - h)
                    x = rng.randint(0, bg.shape[1] - w)
                    bg = bg[y : y + h, x : x + w]
                else:
                    bg = cv2.resize(bg, (w, h))
        else:
            # White background
            bg = np.full((h, w, 3), [255, 255, 255], dtype=np.uint8)

        # Composite image onto background
        if img.shape[2] == 4:
            alpha = img[:, :, 3:4] / 255.0
            result = bg * (1 - alpha) + img[:, :, :3] * alpha
            return result.astype(np.uint8)
        else:
            return img[:, :, :3]

    def save(
        self,
        result: GenerationResult,
        filename: Optional[str] = None,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """Save generation result to file.

        Args:
            result: GenerationResult to save
            filename: Output filename. Auto-generated if not provided.
            output_dir: Output directory. Uses config if not provided.

        Returns:
            Path to saved file
        """
        output_dir = output_dir or self.config.output.output_dir
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            # Generate safe filename
            text_hash = hashlib.md5(result.text.encode()).hexdigest()[:8]
            safe_text = "".join(c if c.isalnum() else "_" for c in result.text)[:20]
            filename = f"{safe_text}_{text_hash}.{self.config.output.format}"

        filepath = output_dir / filename

        # Save image
        if self.config.output.format.lower() in ("jpg", "jpeg"):
            cv2.imwrite(
                str(filepath), result.image, [cv2.IMWRITE_JPEG_QUALITY, self.config.output.quality]
            )
        else:
            cv2.imwrite(str(filepath), result.image)

        # Save label
        if self.config.output.create_labels:
            label_path = filepath.with_suffix(f".{self.config.output.label_format}")
            if self.config.output.label_format == "json":
                import json

                with open(label_path, "w") as f:
                    json.dump(
                        {"text": result.text, "labels": result.labels, "seed": result.seed}, f
                    )
            else:
                with open(label_path, "w") as f:
                    f.write(result.text)

        logger.info(f"Saved: {filepath}")
        return filepath

    def batch_generate(
        self, texts: list[str], save: bool = True, output_dir: Optional[Path] = None
    ) -> list[GenerationResult]:
        """Generate images for multiple texts.

        Args:
            texts: List of texts to generate
            save: Whether to save results to disk
            output_dir: Output directory for saved files

        Returns:
            List of GenerationResult objects
        """
        results = []

        for text in texts:
            try:
                result = self.generate(text)
                if save:
                    self.save(result, output_dir=output_dir)
                results.append(result)
            except ValueError as e:
                logger.warning(f"Failed to generate '{text}': {e}")

        return results

    def reset_seed(self, seed: Optional[int] = None) -> None:
        """Reset the random seed.

        Args:
            seed: New seed. Uses config seed if not provided.
        """
        seed = seed if seed is not None else self.config.seed
        rng.seed(seed)
        logger.info(f"Reset seed to {seed}")
