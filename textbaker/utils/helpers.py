"""
Helper utilities for TextBaker.
"""

import re


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing special characters.

    Args:
        filename: The original filename string.

    Returns:
        A safe filename with only alphanumeric chars, spaces, underscores, and hyphens.
    """
    # Keep alphanumeric, space, underscore, and hyphen
    safe = "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in filename)
    # Remove consecutive underscores and strip
    safe = re.sub(r"_+", "_", safe).strip("_")
    return safe if safe else "file"
