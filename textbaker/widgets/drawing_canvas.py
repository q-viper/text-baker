"""
Drawing canvas widget for creating custom characters.
"""

from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import QPoint, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QColor, QCursor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)


class SaveWorker(QThread):
    """Worker thread for saving images without blocking the UI."""

    finished = Signal(bool, str, str)  # success, character, path
    error = Signal(str)  # error message

    def __init__(self, img_bgr, save_path: Path, character: str):
        super().__init__()
        self.img_bgr = img_bgr
        self.save_path = save_path
        self.character = character

    def run(self):
        """Save the image in a separate thread."""
        try:
            success = cv2.imwrite(str(self.save_path), self.img_bgr)
            self.finished.emit(success, self.character, str(self.save_path))
        except Exception as e:
            self.error.emit(str(e))


class DrawingCanvas(QDialog):
    """Dialog for drawing custom characters."""

    character_saved = Signal(str, str)  # character, image_path

    def __init__(self, parent=None, save_dir: Path = None):
        super().__init__(parent)
        if save_dir:
            self.save_dir = save_dir
        else:
            # Default to current working directory
            self.save_dir = Path.cwd() / ".textbaker" / "custom_characters"
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.setWindowTitle("✏️ Draw Character")
        self.setModal(True)
        self.resize(700, 850)

        # Drawing state
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 10
        self.eraser_mode = False
        self.bg_color = QColor(255, 255, 255)  # White background

        # Canvas size
        self.canvas_size = 512
        self.canvas = QPixmap(self.canvas_size, self.canvas_size)
        self.canvas.fill(self.bg_color)

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Draw Your Character")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Canvas label
        self.canvas_label = QLabel()
        self.canvas_label.setPixmap(self.canvas)
        self.canvas_label.setStyleSheet("""
            QLabel {
                border: 3px solid #2196F3;
                background: white;
                border-radius: 5px;
            }
        """)
        self.canvas_label.mousePressEvent = self.mouse_press_event
        self.canvas_label.mouseMoveEvent = self.mouse_move_event
        self.canvas_label.mouseReleaseEvent = self.mouse_release_event
        self.canvas_label.wheelEvent = self.wheel_event
        # Set crosshair cursor for precise drawing
        self.canvas_label.setCursor(QCursor(Qt.CrossCursor))
        layout.addWidget(self.canvas_label, alignment=Qt.AlignCenter)

        # Drawing controls group
        controls_group = QGroupBox("🎨 Drawing Controls")
        controls_layout = QVBoxLayout()

        # Pen width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Pen Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 50)
        self.width_spin.setValue(self.pen_width)
        self.width_spin.valueChanged.connect(self._on_width_changed)
        width_layout.addWidget(self.width_spin)
        width_layout.addStretch()
        controls_layout.addLayout(width_layout)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Tool palette group
        tool_group = QGroupBox("🛠️ Tools & Colors")
        tool_layout = QVBoxLayout()

        # Drawing tools row
        tools_row = QHBoxLayout()

        # Pen/Draw button
        self.pen_btn = QPushButton("✏️ Pen")
        self.pen_btn.setCheckable(True)
        self.pen_btn.setChecked(True)
        self.pen_btn.clicked.connect(self._set_pen_mode)
        self.pen_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:checked {
                background: #1976D2;
                border: 2px solid #0D47A1;
            }
        """)
        tools_row.addWidget(self.pen_btn)

        # Eraser button
        self.eraser_btn = QPushButton("🧹 Eraser")
        self.eraser_btn.setCheckable(True)
        self.eraser_btn.clicked.connect(self._set_eraser_mode)
        self.eraser_btn.setStyleSheet("""
            QPushButton {
                background: #9E9E9E;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:checked {
                background: #616161;
                border: 2px solid #424242;
            }
        """)
        tools_row.addWidget(self.eraser_btn)

        # Fill background button
        fill_bg_btn = QPushButton("🎨 Fill BG")
        fill_bg_btn.clicked.connect(self._fill_background)
        fill_bg_btn.setStyleSheet("""
            QPushButton {
                background: #673AB7;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5E35B1;
            }
        """)
        tools_row.addWidget(fill_bg_btn)

        # Clear canvas button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.clicked.connect(self._clear_canvas)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #F44336;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #D32F2F;
            }
        """)
        tools_row.addWidget(clear_btn)

        tool_layout.addLayout(tools_row)

        # Color picker section
        color_picker_layout = QHBoxLayout()
        color_picker_layout.addWidget(QLabel("Drawing Color:"))

        # Custom color picker button
        self.custom_color_btn = QPushButton("🎨 Pick Color")
        self.custom_color_btn.clicked.connect(self._choose_color)
        self.custom_color_btn.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                color: white;
                padding: 8px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #F57C00;
            }
        """)
        color_picker_layout.addWidget(self.custom_color_btn)

        # Current color display
        self.current_color_display = QLabel()
        self.current_color_display.setFixedSize(60, 30)
        self.current_color_display.setStyleSheet(f"""
            QLabel {{
                background: {self.pen_color.name()};
                border: 2px solid #333;
                border-radius: 3px;
            }}
        """)
        color_picker_layout.addWidget(self.current_color_display)
        color_picker_layout.addStretch()

        tool_layout.addLayout(color_picker_layout)
        tool_group.setLayout(tool_layout)
        layout.addWidget(tool_group)

        # Character input group
        char_group = QGroupBox("📝 Character Label")
        char_layout = QVBoxLayout()
        char_layout.addWidget(QLabel("Enter the character(s) this drawing represents:"))
        self.char_input = QLineEdit()
        self.char_input.setMaxLength(10)
        self.char_input.setPlaceholderText("e.g., A, 5, @, abc, etc.")
        self.char_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14pt;
                border: 2px solid #2196F3;
                border-radius: 3px;
            }
        """)
        char_layout.addWidget(self.char_input)
        char_group.setLayout(char_layout)
        layout.addWidget(char_group)

        # Action buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("💾 Save Character")
        save_btn.clicked.connect(self._save_character)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                padding: 10px;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #45A049;
            }
        """)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #9E9E9E;
                color: white;
                padding: 10px;
                font-size: 12pt;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #757575;
            }
        """)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Saving...")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2196F3;
                border-radius: 3px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label for confirmation messages (hidden by default)
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-size: 14pt;
                font-weight: bold;
            }
        """)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

    def _on_width_changed(self, value: int):
        """Handle pen width change."""
        self.pen_width = value

    def _set_pen_mode(self):
        """Set to pen drawing mode."""
        self.eraser_mode = False
        self.pen_btn.setChecked(True)
        self.eraser_btn.setChecked(False)
        # Set crosshair cursor for pen mode
        self.canvas_label.setCursor(QCursor(Qt.CrossCursor))

    def _set_eraser_mode(self):
        """Set to eraser mode."""
        self.eraser_mode = True
        self.eraser_btn.setChecked(True)
        self.pen_btn.setChecked(False)
        # Set pointing hand cursor for eraser mode
        self.canvas_label.setCursor(QCursor(Qt.PointingHandCursor))

    def _fill_background(self):
        """Fill background with chosen color."""
        color = QColorDialog.getColor(self.bg_color, self, "Choose Background Color")
        if color.isValid():
            self.bg_color = color
            self.canvas.fill(self.bg_color)
            self.canvas_label.setPixmap(self.canvas)

    def _choose_color(self):
        """Open color picker dialog."""
        color = QColorDialog.getColor(self.pen_color, self, "Choose Pen Color")
        if color.isValid():
            self.pen_color = color
            # Update the color display
            self.current_color_display.setStyleSheet(f"""
                QLabel {{
                    background: {color.name()};
                    border: 2px solid #333;
                    border-radius: 3px;
                }}
            """)
            self.eraser_mode = False
            self.pen_btn.setChecked(True)
            self.eraser_btn.setChecked(False)
            # Set crosshair cursor when choosing color
            self.canvas_label.setCursor(QCursor(Qt.CrossCursor))

    def _clear_canvas(self):
        """Clear the drawing canvas."""
        reply = QMessageBox.question(
            self,
            "Clear Canvas",
            "Are you sure you want to clear the canvas?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.canvas.fill(self.bg_color)
            self.canvas_label.setPixmap(self.canvas)

    def mouse_press_event(self, event):
        """Handle mouse press on canvas."""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouse_move_event(self, event):
        """Handle mouse move on canvas."""
        if self.drawing and event.buttons() & Qt.LeftButton:
            painter = QPainter(self.canvas)

            if self.eraser_mode:
                # Use background color for erasing
                pen = QPen(
                    self.bg_color,
                    self.pen_width * 2,  # Eraser is wider
                    Qt.SolidLine,
                    Qt.RoundCap,
                    Qt.RoundJoin,
                )
            else:
                # Use selected pen color for drawing
                pen = QPen(
                    self.pen_color,
                    self.pen_width,
                    Qt.SolidLine,
                    Qt.RoundCap,
                    Qt.RoundJoin,
                )

            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            painter.end()

            self.last_point = event.pos()
            self.canvas_label.setPixmap(self.canvas)

    def mouse_release_event(self, event):
        """Handle mouse release on canvas."""
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Delete:
            # Clear canvas on Delete key
            reply = QMessageBox.question(
                self,
                "Clear Canvas",
                "Are you sure you want to clear the canvas?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.canvas.fill(self.bg_color)
                self.canvas_label.setPixmap(self.canvas)
        else:
            super().keyPressEvent(event)

    def wheel_event(self, event):
        """Handle mouse wheel event to change pen width."""
        # Get wheel delta (positive = scroll up, negative = scroll down)
        delta = event.angleDelta().y()

        # Change pen width based on scroll direction
        new_width = min(self.pen_width + 2, 50) if delta > 0 else max(self.pen_width - 2, 1)

        # Update pen width
        if new_width != self.pen_width:
            self.pen_width = new_width
            self.width_spin.setValue(new_width)

    def _save_character(self):
        """Save the drawn character."""
        character = self.char_input.text().strip()
        if not character:
            self.char_input.setFocus()
            self.char_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14pt;
                    border: 2px solid #F44336;
                    border-radius: 3px;
                }
            """)
            return

        # Validate that something was drawn
        qimage = self.canvas.toImage()
        if self._is_canvas_empty(qimage):
            self.setWindowTitle("✏️ Draw Character - Please draw something first!")
            return

        # Convert QPixmap to numpy array
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()

        # Convert to numpy array (RGBA format)
        arr = np.frombuffer(ptr, dtype=np.uint8).reshape((height, width, 4))

        # Convert RGBA to BGR for OpenCV
        img_bgr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)

        # Create character directory
        char_dir = self.save_dir / character
        char_dir.mkdir(exist_ok=True)

        # Generate unique filename
        existing_files = list(char_dir.glob("drawn_*.png"))
        filename = f"drawn_{len(existing_files) + 1:04d}.png"
        save_path = char_dir / filename

        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setFormat("Saving...")

        # Create and start worker thread for async saving
        self.save_worker = SaveWorker(img_bgr, save_path, character)
        self.save_worker.finished.connect(self._on_save_finished)
        self.save_worker.error.connect(self._on_save_error)
        self.save_worker.start()

    def _on_save_finished(self, success: bool, character: str, save_path: str):
        """Handle save completion."""
        # Hide progress bar
        self.progress_bar.setVisible(False)

        if success:
            # Reset title and input styling
            self.setWindowTitle("✏️ Draw Character")
            self.char_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    font-size: 14pt;
                    border: 2px solid #2196F3;
                    border-radius: 3px;
                }
            """)

            # Show success message
            from pathlib import Path

            filename = Path(save_path).name
            self.status_label.setText(f"✅ Saved '{character}' as {filename}")
            self.status_label.setVisible(True)

            # Auto-hide after 3 seconds
            QTimer.singleShot(3000, lambda: self.status_label.setVisible(False))

            # Emit signal to notify parent (non-blocking)
            self.character_saved.emit(character, save_path)
        else:
            QMessageBox.critical(self, "Error", f"Failed to save character to {save_path}")

    def _on_save_error(self, error_msg: str):
        """Handle save error."""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"Error saving character: {error_msg}")

    def _is_canvas_empty(self, qimage: QImage) -> bool:
        """Check if canvas has any content different from background."""
        width = qimage.width()
        height = qimage.height()

        bg_r = self.bg_color.red()
        bg_g = self.bg_color.green()
        bg_b = self.bg_color.blue()

        # Check multiple points across the canvas
        # Sample in a grid pattern to detect any drawing
        step = 16  # Check every 16 pixels (more thorough)

        for y in range(0, height, step):
            for x in range(0, width, step):
                pixel = qimage.pixelColor(x, y)
                # Check if pixel is different from background
                r_diff = abs(pixel.red() - bg_r)
                g_diff = abs(pixel.green() - bg_g)
                b_diff = abs(pixel.blue() - bg_b)
                color_diff = r_diff + g_diff + b_diff

                # If any pixel is different enough, not empty
                if color_diff > 10:  # Lower threshold for better detection
                    return False

        # If we didn't find any different pixels, canvas is empty
        return True
