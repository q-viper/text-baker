"""
Dialog widgets for TextBaker.
"""

from pathlib import Path
from typing import Optional

import cv2
from loguru import logger
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QBrush, QColor, QImage, QMouseEvent, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from textbaker.utils.random_state import rng


class TexturePickerDialog(QDialog):
    """Dialog for selecting texture regions from images."""

    def __init__(self, texture_paths: list[Path], background_paths: list[Path], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Texture Region Selector")
        self.resize(900, 700)

        self.texture_paths = texture_paths if texture_paths else background_paths
        self.using_backgrounds = len(texture_paths) == 0

        if not self.texture_paths:
            QMessageBox.warning(self, "No Images", "No texture or background images available!")
            self.reject()
            return

        self.current_index = 0
        self.current_image = None
        self.selected_region: Optional[tuple[int, int, int, int]] = None
        self.selection_start: Optional[tuple[int, int]] = None
        self.selection_end: Optional[tuple[int, int]] = None
        self.is_selecting = False
        self.selection_rect_item: Optional[QGraphicsRectItem] = None
        self.texture_item = None

        self._init_ui()
        self.load_current_texture()
        self.random_select_region()

    def _init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)

        # Info label
        if self.using_backgrounds:
            info = QLabel("⚠️ Using background images as textures (texture folder is empty)")
            info.setStyleSheet(
                "background: #FF9800; color: white; padding: 8px; font-weight: bold;"
            )
        else:
            info = QLabel("✨ Drag mouse to select a texture region (or use Random Region button)")
            info.setStyleSheet("background: #4CAF50; color: white; padding: 8px;")
        layout.addWidget(info)

        # Graphics view
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setDragMode(QGraphicsView.NoDrag)
        layout.addWidget(self.graphics_view)

        # Navigation
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.clicked.connect(self.prev_texture)
        nav_layout.addWidget(self.prev_btn)

        self.texture_info_label = QLabel(f"1 / {len(self.texture_paths)}")
        self.texture_info_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.texture_info_label)

        self.next_btn = QPushButton("Next ▶")
        self.next_btn.clicked.connect(self.next_texture)
        nav_layout.addWidget(self.next_btn)

        layout.addLayout(nav_layout)

        # Random select button
        random_btn = QPushButton("🎲 Random Region")
        random_btn.clicked.connect(self.random_select_region)
        random_btn.setStyleSheet("""
            QPushButton {
                background: #9C27B0;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7B1FA2;
                color: white;
            }
        """)
        layout.addWidget(random_btn)

        # Action buttons
        action_layout = QHBoxLayout()

        select_btn = QPushButton("✅ Select Texture and Use Everywhere")
        select_btn.clicked.connect(self.accept_selection)
        select_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
                color: white;
            }
        """)
        action_layout.addWidget(select_btn)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #f44336;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #da190b;
                color: white;
            }
        """)
        action_layout.addWidget(cancel_btn)

        layout.addLayout(action_layout)

        # Install event filter for mouse drag selection
        self.graphics_view.viewport().installEventFilter(self)

    def load_current_texture(self):
        """Load and display current texture."""
        texture_path = self.texture_paths[self.current_index]
        texture = cv2.imread(str(texture_path), cv2.IMREAD_COLOR)

        if texture is None:
            logger.error(f"Failed to load: {texture_path.name}")
            return

        self.current_image = texture
        texture_rgb = cv2.cvtColor(texture, cv2.COLOR_BGR2RGB)

        h, w, ch = texture_rgb.shape
        qimg = QImage(texture_rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        self.graphics_scene.clear()
        self.texture_item = self.graphics_scene.addPixmap(pixmap)
        self.selection_rect_item = None
        self.graphics_view.fitInView(self.texture_item, Qt.KeepAspectRatio)

        self.texture_info_label.setText(f"{self.current_index + 1} / {len(self.texture_paths)}")
        logger.info(f"Loaded texture: {texture_path.name} [{w}x{h}]")

    def prev_texture(self):
        """Navigate to previous texture."""
        self.current_index = (self.current_index - 1) % len(self.texture_paths)
        self.load_current_texture()
        self.random_select_region()

    def next_texture(self):
        """Navigate to next texture."""
        self.current_index = (self.current_index + 1) % len(self.texture_paths)
        self.load_current_texture()
        self.random_select_region()

    def random_select_region(self):
        """Randomly select a region from the texture."""
        if self.current_image is None:
            return

        h, w = self.current_image.shape[:2]

        # Random region size (20% to 60% of image)
        region_w = rng.randint(int(w * 0.2), int(w * 0.6))
        region_h = rng.randint(int(h * 0.2), int(h * 0.6))

        # Random position
        x = rng.randint(0, w - region_w)
        y = rng.randint(0, h - region_h)

        self.selected_region = (x, y, region_w, region_h)
        self._draw_selection()

        logger.info(f"Random region: ({x}, {y}) [{region_w}x{region_h}]")

    def _draw_selection(self):
        """Draw the selection rectangle on the image."""
        if self.selection_rect_item:
            self.graphics_scene.removeItem(self.selection_rect_item)
            self.selection_rect_item = None

        if self.selected_region:
            x, y, w, h = self.selected_region
            self.selection_rect_item = QGraphicsRectItem(x, y, w, h)
            pen = QPen(QColor(0, 255, 0), 3, Qt.SolidLine)
            self.selection_rect_item.setPen(pen)
            self.selection_rect_item.setBrush(QBrush(QColor(0, 255, 0, 50)))
            self.graphics_scene.addItem(self.selection_rect_item)

    def eventFilter(self, obj, event):
        """Handle mouse events for drag selection."""
        if obj == self.graphics_view.viewport():
            if event.type() == QEvent.Type.MouseButtonPress:
                if isinstance(event, QMouseEvent) and event.button() == Qt.LeftButton:
                    self.is_selecting = True
                    scene_pos = self.graphics_view.mapToScene(event.pos())
                    self.selection_start = (int(scene_pos.x()), int(scene_pos.y()))
                    return True

            elif event.type() == QEvent.Type.MouseMove:
                if self.is_selecting:
                    scene_pos = self.graphics_view.mapToScene(event.pos())
                    self.selection_end = (int(scene_pos.x()), int(scene_pos.y()))

                    if self.selection_start and self.selection_end:
                        x1, y1 = self.selection_start
                        x2, y2 = self.selection_end

                        x = min(x1, x2)
                        y = min(y1, y2)
                        w = abs(x2 - x1)
                        h = abs(y2 - y1)

                        # Clamp to image bounds
                        if self.current_image is not None:
                            img_h, img_w = self.current_image.shape[:2]
                            x = max(0, min(x, img_w))
                            y = max(0, min(y, img_h))
                            w = min(w, img_w - x)
                            h = min(h, img_h - y)

                        self.selected_region = (x, y, w, h)
                        self._draw_selection()

                    return True

            elif (
                event.type() == QEvent.Type.MouseButtonRelease
                and isinstance(event, QMouseEvent)
                and event.button() == Qt.LeftButton
            ):
                self.is_selecting = False
                if self.selected_region:
                    x, y, w, h = self.selected_region
                    logger.info(f"Selected region: ({x}, {y}) [{w}x{h}]")
                return True

        return super().eventFilter(obj, event)

    def accept_selection(self):
        """Accept the selected region and close dialog."""
        if self.selected_region is None:
            QMessageBox.warning(self, "No Selection", "Please select a region first!")
            return

        x, y, w, h = self.selected_region
        if w < 10 or h < 10:
            QMessageBox.warning(self, "Invalid Selection", "Selected region is too small!")
            return

        logger.success(
            f"Texture region selected: ({x}, {y}) [{w}x{h}] from {self.texture_paths[self.current_index].name}"
        )
        self.accept()

    def get_selected_texture(self):
        """Get the selected texture region as an image."""
        if self.selected_region is None or self.current_image is None:
            return None

        x, y, w, h = self.selected_region
        return self.current_image[y : y + h, x : x + w].copy()


class HintsDialog(QDialog):
    """Dialog to show keyboard shortcuts and hints."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts & Hints")
        self.resize(600, 500)

        layout = QVBoxLayout(self)

        hints_text = QTextEdit()
        hints_text.setReadOnly(True)
        hints_text.setHtml("""
        <h2>Keyboard Shortcuts & Controls</h2>

        <h3>🖱️ Mouse Controls:</h3>
        <ul>
            <li><b>Left Click on Text</b> - Select text item</li>
            <li><b>Left Click + Drag (on text)</b> - Move text</li>
            <li><b>Left Click + Drag (on blue circle)</b> - Rotate text</li>
            <li><b>Left Click + Drag (on corners)</b> - Resize text</li>
            <li><b>Mouse Wheel</b> - Zoom in/out</li>
        </ul>

        <h3>⌨️ Keyboard Shortcuts:</h3>
        <ul>
            <li><b>SPACE + Drag</b> - Pan view</li>
        </ul>

        <h3>🎨 Texture Picker:</h3>
        <ul>
            <li>Click "Pick Texture Region" to open picker</li>
            <li>Use left/right buttons to navigate textures</li>
            <li><b>Drag mouse to select custom region</b></li>
            <li>Click "Random Region" for random selection</li>
            <li>Selected texture applies to all characters</li>
        </ul>

        <h3>🎨 Workflow:</h3>
        <ol>
            <li>Select dataset folder with character subfolders</li>
            <li>Select texture folder for character textures</li>
            <li>Select background folder</li>
            <li>Choose texture mode (No Texture is default)</li>
            <li>Use "Pick Texture Region" to select a specific texture area</li>
            <li>Click <b>"Generate Random Text"</b> to create text</li>
            <li>Click <b>"Select Random Background"</b></li>
        </ol>

        <h3>💡 Tips:</h3>
        <ul>
            <li>Textures apply only to characters, not viewport</li>
            <li>"No Texture" uses original image colors</li>
            <li>Generated text shown at bottom with highlight</li>
            <li>Picked texture region applies to all characters</li>
            <li><b>Drag to draw selection rectangle in texture picker</b></li>
        </ul>
        """)

        layout.addWidget(hints_text)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
