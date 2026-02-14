"""
Logging utilities for TextBaker.
"""

import sys
from loguru import logger
from PySide6.QtCore import Signal, QObject


def setup_logger():
    """Configure loguru logger with custom format."""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout, 
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
    )
    return logger


class LogHandler(QObject):
    """Handler to capture loguru logs and emit them as Qt signals."""
    log_signal = Signal(str)
    
    def write(self, message):
        if message.strip():
            self.log_signal.emit(message.strip())


# Initialize logger on module import
setup_logger()
