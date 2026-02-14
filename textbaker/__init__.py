"""
TextBaker - Synthetic Text Dataset Generator for OCR Training

A Python-based tool for creating/generating images to train OCR detection models.

Usage:
    import textbaker as tb
    
    # Use the image processor
    processor = tb.ImageProcessor()
    
    # Access the main window
    from textbaker.app import DatasetMaker

Author: Ramkrishna Acharya
"""

__version__ = "0.1.0"
__author__ = "Ramkrishna Acharya"
__email__ = ""
__description__ = "Synthetic Text Dataset Generator for OCR Training"

# Lazy imports to avoid circular dependencies and improve import time
def __getattr__(name):
    if name == "DatasetMaker":
        from textbaker.app.main_window import DatasetMaker
        return DatasetMaker
    elif name == "ImageProcessor":
        from textbaker.core.image_processing import ImageProcessor
        return ImageProcessor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["DatasetMaker", "ImageProcessor"]
