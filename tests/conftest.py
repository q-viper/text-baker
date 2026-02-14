"""
Pytest configuration and fixtures for TextBaker tests.
"""

import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_dataset(temp_dir):
    """Create a sample dataset with character images."""
    dataset_dir = temp_dir / "dataset"

    # Create character folders with sample images
    chars = ["A", "B", "C", "0", "1", "2"]
    for char in chars:
        char_dir = dataset_dir / char
        char_dir.mkdir(parents=True)

        # Create a simple white character on transparent background
        img = np.zeros((64, 64, 4), dtype=np.uint8)
        cv2.putText(img, char, (15, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255, 255), 2)

        cv2.imwrite(str(char_dir / "sample.png"), img)

    return dataset_dir


@pytest.fixture
def sample_backgrounds(temp_dir):
    """Create sample background images."""
    bg_dir = temp_dir / "backgrounds"
    bg_dir.mkdir(parents=True)

    # Create simple colored backgrounds
    colors = [(200, 150, 100), (100, 150, 200), (150, 200, 100)]
    for i, color in enumerate(colors):
        img = np.full((256, 256, 3), color, dtype=np.uint8)
        cv2.imwrite(str(bg_dir / f"bg_{i}.png"), img)

    return bg_dir


@pytest.fixture
def sample_textures(temp_dir):
    """Create sample texture images."""
    tex_dir = temp_dir / "textures"
    tex_dir.mkdir(parents=True)

    # Create simple pattern textures
    for i in range(2):
        img = np.zeros((64, 64, 4), dtype=np.uint8)
        # Create a simple checkerboard pattern
        for y in range(64):
            for x in range(64):
                if (x // 8 + y // 8) % 2 == 0:
                    img[y, x] = [200, 200, 200, 255]
                else:
                    img[y, x] = [100, 100, 100, 255]
        cv2.imwrite(str(tex_dir / f"texture_{i}.png"), img)

    return tex_dir


@pytest.fixture
def sample_config_yaml(temp_dir):
    """Create a sample YAML config file."""
    config_content = """
seed: 123
spacing: 5
text_length: [3, 8]

dataset:
  dataset_dir: assets/dataset
  recursive: true

transform:
  rotation_range: [-10, 10]
  scale_range: [0.9, 1.1]

color:
  random_color: false

output:
  output_dir: output
  format: png
"""
    config_path = temp_dir / "config.yaml"
    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def sample_config_json(temp_dir):
    """Create a sample JSON config file."""
    import json

    config_data = {
        "seed": 456,
        "spacing": 3,
        "text_length": [2, 6],
        "transform": {
            "rotation_range": [-5, 5],
        },
    }
    config_path = temp_dir / "config.json"
    config_path.write_text(json.dumps(config_data))
    return config_path
