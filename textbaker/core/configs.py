"""
Pydantic configuration models for TextBaker.

These configs can be used to:
1. Load settings from JSON/YAML files
2. Programmatically configure the text generator
3. Validate configuration parameters
"""

from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field, field_validator


class BaseConfig(BaseModel):
    """Base configuration with common settings."""

    class Config:
        extra = "allow"
        validate_assignment = True


class TransformConfig(BaseConfig):
    """Configuration for image transformations."""

    rotation_range: tuple[float, float] = Field(
        default=(0.0, 0.0), description="Min and max rotation angle in degrees"
    )
    perspective_range: tuple[float, float] = Field(
        default=(0.0, 0.0), description="Min and max perspective distortion"
    )
    scale_range: tuple[float, float] = Field(
        default=(0.9, 1.1), description="Min and max scale factor"
    )
    shear_range: tuple[float, float] = Field(
        default=(0.0, 0.0), description="Min and max shear angle"
    )

    @field_validator(
        "rotation_range", "perspective_range", "scale_range", "shear_range", mode="before"
    )
    @classmethod
    def validate_range(cls, v):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            return tuple(v)
        raise ValueError("Range must be a tuple of (min, max)")


class ColorConfig(BaseConfig):
    """Configuration for color manipulation."""

    random_color: bool = Field(default=False, description="Whether to apply random colors")
    color_range_r: tuple[int, int] = Field(default=(0, 255), description="Red channel range")
    color_range_g: tuple[int, int] = Field(default=(0, 255), description="Green channel range")
    color_range_b: tuple[int, int] = Field(default=(0, 255), description="Blue channel range")
    fixed_color: Optional[tuple[int, int, int]] = Field(
        default=None, description="Fixed RGB color to apply"
    )


class TextureConfig(BaseConfig):
    """Configuration for texture application."""

    enabled: bool = Field(default=False, description="Whether to apply textures")
    texture_dir: Optional[Path] = Field(
        default=None, description="Directory containing texture images"
    )
    per_character: bool = Field(default=False, description="Apply different texture per character")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0, description="Texture opacity (0-1)")


class BackgroundConfig(BaseConfig):
    """Configuration for background handling."""

    enabled: bool = Field(default=False, description="Whether to add background")
    background_dir: Optional[Path] = Field(
        default=None, description="Directory containing background images"
    )
    color: Optional[tuple[int, int, int]] = Field(
        default=None, description="Solid background color RGB"
    )
    random_crop: bool = Field(default=True, description="Randomly crop background to fit")


class OutputConfig(BaseConfig):
    """Configuration for output settings."""

    output_dir: Path = Field(
        default=Path("output"), description="Output directory for generated images"
    )
    format: str = Field(default="png", description="Output image format")
    quality: int = Field(default=95, ge=1, le=100, description="JPEG quality (if format is jpg)")
    create_labels: bool = Field(default=True, description="Create label files alongside images")
    label_format: str = Field(default="txt", description="Label file format (txt, json, csv)")


class DatasetConfig(BaseConfig):
    """Configuration for dataset paths."""

    dataset_dir: Path = Field(
        default=Path("assets/dataset"), description="Directory containing character images"
    )
    recursive: bool = Field(default=True, description="Scan dataset directory recursively")
    extensions: list[str] = Field(
        default=[".png", ".jpg", ".jpeg", ".bmp"], description="Valid image file extensions"
    )


class CharacterConfig(BaseConfig):
    """Configuration for character rendering (fallback when not in dataset).

    Available CV2 fonts:
        - FONT_HERSHEY_SIMPLEX: Normal size sans-serif
        - FONT_HERSHEY_PLAIN: Small size sans-serif
        - FONT_HERSHEY_DUPLEX: Normal size sans-serif (more complex)
        - FONT_HERSHEY_COMPLEX: Normal size serif
        - FONT_HERSHEY_TRIPLEX: Normal size serif (more complex)
        - FONT_HERSHEY_COMPLEX_SMALL: Smaller version of complex
        - FONT_HERSHEY_SCRIPT_SIMPLEX: Handwritten style (default)
        - FONT_HERSHEY_SCRIPT_COMPLEX: Handwritten style (more complex)
    """

    width: int = Field(default=64, ge=16, le=512, description="Character width in pixels")
    height: int = Field(default=64, ge=16, le=512, description="Character height in pixels")
    font: str = Field(
        default="FONT_HERSHEY_SCRIPT_COMPLEX",
        description="CV2 font name for fallback text rendering",
    )
    thickness: int = Field(
        default=2, ge=1, le=10, description="Font thickness for fallback rendering"
    )

    @field_validator("font", mode="before")
    @classmethod
    def validate_font(cls, v):
        valid_fonts = [
            "FONT_HERSHEY_SIMPLEX",
            "FONT_HERSHEY_PLAIN",
            "FONT_HERSHEY_DUPLEX",
            "FONT_HERSHEY_COMPLEX",
            "FONT_HERSHEY_TRIPLEX",
            "FONT_HERSHEY_COMPLEX_SMALL",
            "FONT_HERSHEY_SCRIPT_SIMPLEX",
            "FONT_HERSHEY_SCRIPT_COMPLEX",
        ]
        if v not in valid_fonts:
            raise ValueError(f"Invalid font. Must be one of: {valid_fonts}")
        return v

    def get_cv2_font(self) -> int:
        """Get the cv2 font constant."""
        import cv2

        return getattr(cv2, self.font)


class GeneratorConfig(BaseConfig):
    """Main configuration for text generation.

    This is the primary config class for programmatic usage.

    Example:
        ```python
        from textbaker import GeneratorConfig, TextGenerator

        config = GeneratorConfig(
            seed=42,
            text_length=(3, 8),
            transform=TransformConfig(rotation_range=(-15, 15)),
            output=OutputConfig(output_dir="my_output")
        )

        generator = TextGenerator(config)
        result = generator.generate("hello")
        ```
    """

    seed: int = Field(default=42, description="Random seed for reproducibility")
    text_length: tuple[int, int] = Field(
        default=(1, 10), description="Min and max text length for random generation"
    )
    spacing: int = Field(
        default=0, ge=-50, le=100, description="Spacing between characters in pixels"
    )
    dataset: DatasetConfig = Field(
        default_factory=DatasetConfig, description="Dataset configuration"
    )
    transform: TransformConfig = Field(
        default_factory=TransformConfig, description="Transform configuration"
    )
    color: ColorConfig = Field(default_factory=ColorConfig, description="Color configuration")
    texture: TextureConfig = Field(
        default_factory=TextureConfig, description="Texture configuration"
    )
    background: BackgroundConfig = Field(
        default_factory=BackgroundConfig, description="Background configuration"
    )
    output: OutputConfig = Field(default_factory=OutputConfig, description="Output configuration")
    character: CharacterConfig = Field(
        default_factory=CharacterConfig,
        description="Character rendering configuration (for fallback)",
    )

    @classmethod
    def from_file(cls, path: Union[str, Path]) -> "GeneratorConfig":
        """Load configuration from a JSON or YAML file.

        Args:
            path: Path to config file

        Returns:
            GeneratorConfig instance
        """
        path = Path(path)

        if path.suffix in (".yaml", ".yml"):
            try:
                import yaml

                with open(path) as f:
                    data = yaml.safe_load(f)
            except ImportError as e:
                raise ImportError(
                    "PyYAML is required for YAML config files: pip install pyyaml"
                ) from e
        else:
            import json

            with open(path) as f:
                data = json.load(f)

        return cls(**data)

    def to_file(self, path: Union[str, Path]) -> None:
        """Save configuration to a JSON or YAML file.

        Args:
            path: Path to save config file
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = self.model_dump(mode="json")

        if path.suffix in (".yaml", ".yml"):
            try:
                import yaml

                with open(path, "w") as f:
                    yaml.dump(data, f, default_flow_style=False)
            except ImportError as e:
                raise ImportError(
                    "PyYAML is required for YAML config files: pip install pyyaml"
                ) from e
        else:
            import json

            with open(path, "w") as f:
                json.dump(data, f, indent=2)


# Default config instance
DEFAULT_CONFIG = GeneratorConfig()
