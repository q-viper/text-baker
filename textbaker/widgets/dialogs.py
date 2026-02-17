"""
Dialog widgets for TextBaker.
"""

import time
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from loguru import logger
from PySide6.QtCore import QEvent, QPointF, Qt, Signal, QThread
from PySide6.QtGui import QBrush, QColor, QCursor, QImage, QMouseEvent, QPainter, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGraphicsEllipseItem,
    QGraphicsPolygonItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QProgressBar,
    QGroupBox,
    QScrollArea,
    QWidget,
    QComboBox,
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


class SegmentSaveWorker(QThread):
    """Worker thread for saving segmented images without blocking the UI."""

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


class CharacterSegmentationDialog(QDialog):
    """Dialog for segmenting characters from images using polygon drawing."""

    character_saved = Signal(str, str)  # character, image_path
    MAX_CHAR_LABEL_LENGTH = 10  # Maximum length for character label input

    def __init__(self, parent=None, save_dir: Path = None):
        super().__init__(parent)
        if save_dir:
            self.save_dir = save_dir
        else:
            # Default to current working directory
            self.save_dir = Path.cwd() / ".textbaker" / "custom_characters"
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.setWindowTitle("📐 Segment Character")
        self.setModal(True)
        self.resize(1200, 800)

        # State
        self.image_folder: Optional[Path] = None
        self.image_paths: list[Path] = []
        self.current_index = 0
        self.current_image = None
        self.current_image_rgb = None
        self.polygons: list[list[tuple[int, int]]] = []  # List of polygon point lists
        self.current_polygon: list[tuple[int, int]] = []  # Current polygon being drawn
        self.polygon_items: list[QGraphicsPolygonItem] = []
        self.preview_pixmap = None
        self.is_drawing = False
        self.image_item = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QHBoxLayout(self)

        # Left side - image viewer and controls
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Title
        title = QLabel("📐 Segment Character from Images")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #333;")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet("padding: 5px; border: 1px solid #ccc;")
        folder_layout.addWidget(self.folder_label)
        
        select_folder_btn = QPushButton("📁 Select Folder")
        select_folder_btn.clicked.connect(self._select_folder)
        select_folder_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        folder_layout.addWidget(select_folder_btn)
        left_layout.addLayout(folder_layout)

        # Image navigation
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.clicked.connect(self._prev_image)
        self.prev_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_btn)

        self.image_info_label = QLabel("No images loaded")
        self.image_info_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.image_info_label)

        self.next_btn = QPushButton("Next ▶")
        self.next_btn.clicked.connect(self._next_image)
        self.next_btn.setEnabled(False)
        nav_layout.addWidget(self.next_btn)
        left_layout.addLayout(nav_layout)

        # Graphics view for image
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setDragMode(QGraphicsView.NoDrag)
        left_layout.addWidget(self.graphics_view)

        # Install event filter for drawing
        self.graphics_view.viewport().installEventFilter(self)

        # Drawing controls
        controls_layout = QHBoxLayout()
        
        self.draw_polygon_btn = QPushButton("✏️ Draw Polygon")
        self.draw_polygon_btn.setCheckable(True)
        self.draw_polygon_btn.setEnabled(False)
        self.draw_polygon_btn.clicked.connect(self._toggle_drawing)
        self.draw_polygon_btn.setStyleSheet("""
            QPushButton {
                background: #9C27B0;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7B1FA2;
            }
            QPushButton:checked {
                background: #4CAF50;
            }
        """)
        controls_layout.addWidget(self.draw_polygon_btn)

        finish_polygon_btn = QPushButton("✅ Finish Polygon")
        finish_polygon_btn.clicked.connect(self._finish_polygon)
        finish_polygon_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45A049;
            }
        """)
        controls_layout.addWidget(finish_polygon_btn)

        clear_polygons_btn = QPushButton("🗑️ Clear All")
        clear_polygons_btn.clicked.connect(self._clear_polygons)
        clear_polygons_btn.setStyleSheet("""
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
        controls_layout.addWidget(clear_polygons_btn)

        left_layout.addLayout(controls_layout)

        # Instructions
        instructions = QLabel(
            "Instructions: Click 'Draw Polygon', then click points on the image to draw a polygon around the character. "
            "Click 'Finish Polygon' to complete it. You can draw multiple polygons."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 5px; background: #E3F2FD; color: #1565C0;")
        left_layout.addWidget(instructions)

        main_layout.addWidget(left_widget, stretch=2)

        # Right side - preview and save
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Preview title
        preview_title = QLabel("Segmented Preview")
        preview_title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        preview_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(preview_title)

        # Show region button
        show_region_btn = QPushButton("👁️ Show Region")
        show_region_btn.clicked.connect(self._show_region)
        show_region_btn.setStyleSheet("""
            QPushButton {
                background: #FF9800;
                color: white;
                padding: 10px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #F57C00;
            }
        """)
        right_layout.addWidget(show_region_btn)

        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(400, 400)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 3px solid #FF9800;
                background: black;
                border-radius: 5px;
            }
        """)
        self.preview_label.setText("Preview will appear here")
        self.preview_label.setWordWrap(True)
        
        # Wrap in scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.preview_label)
        scroll_area.setWidgetResizable(True)
        right_layout.addWidget(scroll_area)

        # Character input group
        char_group = QGroupBox("📝 Character Label")
        char_layout = QVBoxLayout()
        char_layout.addWidget(QLabel("Enter the character(s) this region represents:"))
        self.char_input = QLineEdit()
        self.char_input.setMaxLength(self.MAX_CHAR_LABEL_LENGTH)
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
        right_layout.addWidget(char_group)

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
        right_layout.addLayout(btn_layout)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        right_layout.addWidget(self.progress_bar)

        main_layout.addWidget(right_widget, stretch=1)

    def _select_folder(self):
        """Open folder selection dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with Images",
            str(Path.home()),
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.image_folder = Path(folder)
            self.folder_label.setText(str(self.image_folder))
            self._load_images()

    def _load_images(self):
        """Load all images from the selected folder using pathlib rglob."""
        if not self.image_folder:
            return

        # Use rglob to find all image files recursively
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
        self.image_paths = []
        
        for ext in image_extensions:
            self.image_paths.extend(self.image_folder.rglob(f'*{ext}'))
            self.image_paths.extend(self.image_folder.rglob(f'*{ext.upper()}'))

        if not self.image_paths:
            QMessageBox.warning(self, "No Images", "No image files found in the selected folder!")
            return

        self.current_index = 0
        self.prev_btn.setEnabled(len(self.image_paths) > 1)
        self.next_btn.setEnabled(len(self.image_paths) > 1)
        self.draw_polygon_btn.setEnabled(True)
        
        self._load_current_image()
        logger.info(f"Loaded {len(self.image_paths)} images from {self.image_folder}")

    def _load_current_image(self):
        """Load and display the current image."""
        if not self.image_paths:
            return

        image_path = self.image_paths[self.current_index]
        self.current_image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

        if self.current_image is None:
            logger.error(f"Failed to load: {image_path}")
            return

        self.current_image_rgb = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
        
        h, w, ch = self.current_image_rgb.shape
        qimg = QImage(self.current_image_rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        self.graphics_scene.clear()
        self.image_item = self.graphics_scene.addPixmap(pixmap)
        self.graphics_view.fitInView(self.image_item, Qt.KeepAspectRatio)

        self.image_info_label.setText(f"{self.current_index + 1} / {len(self.image_paths)}")
        
        # Clear polygons when loading new image
        self._clear_polygons()
        
        logger.info(f"Loaded image: {image_path.name} [{w}x{h}]")

    def _prev_image(self):
        """Navigate to previous image."""
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self._load_current_image()

    def _next_image(self):
        """Navigate to next image."""
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self._load_current_image()

    def _toggle_drawing(self, checked):
        """Toggle polygon drawing mode."""
        self.is_drawing = checked
        if checked:
            self.draw_polygon_btn.setText("✏️ Drawing...")
            self.graphics_view.setCursor(QCursor(Qt.CrossCursor))
        else:
            self.draw_polygon_btn.setText("✏️ Draw Polygon")
            self.graphics_view.setCursor(QCursor(Qt.ArrowCursor))

    def _clear_polygons(self):
        """Clear all drawn polygons."""
        self.polygons = []
        self.current_polygon = []
        for item in self.polygon_items:
            self.graphics_scene.removeItem(item)
        self.polygon_items = []
        self.preview_label.clear()
        self.preview_label.setText("Preview will appear here")
        self.preview_pixmap = None

    def _finish_polygon(self):
        """Finish the current polygon."""
        if len(self.current_polygon) < 3:
            QMessageBox.warning(
                self,
                "Invalid Polygon",
                "A polygon must have at least 3 points!"
            )
            return

        # Add to polygons list
        self.polygons.append(self.current_polygon.copy())
        self.current_polygon = []
        
        # Turn off drawing mode
        if self.draw_polygon_btn.isChecked():
            self.draw_polygon_btn.setChecked(False)
            self._toggle_drawing(False)

        logger.info(f"Finished polygon with {len(self.polygons[-1])} points. Total polygons: {len(self.polygons)}")

    def eventFilter(self, obj, event):
        """Handle mouse events for polygon drawing."""
        if obj == self.graphics_view.viewport() and self.is_drawing:
            if event.type() == QEvent.Type.MouseButtonPress:
                if isinstance(event, QMouseEvent) and event.button() == Qt.LeftButton:
                    scene_pos = self.graphics_view.mapToScene(event.pos())
                    x, y = int(scene_pos.x()), int(scene_pos.y())
                    
                    # Add point to current polygon
                    self.current_polygon.append((x, y))
                    self._draw_current_polygon()
                    
                    logger.debug(f"Added point ({x}, {y}) to polygon")
                    return True

        return super().eventFilter(obj, event)

    def _draw_current_polygon(self):
        """Draw the current polygon on the image."""
        # Remove old polygon visualization for current polygon
        if self.polygon_items:
            # Keep finished polygons, only remove the last one if it's being updated
            if self.current_polygon and len(self.polygon_items) > len(self.polygons):
                last_item = self.polygon_items.pop()
                self.graphics_scene.removeItem(last_item)

        if len(self.current_polygon) < 2:
            # Just draw a point
            if len(self.current_polygon) == 1:
                x, y = self.current_polygon[0]
                point_item = QGraphicsEllipseItem(x - 3, y - 3, 6, 6)
                point_item.setBrush(QBrush(QColor(255, 0, 0)))
                point_item.setPen(QPen(QColor(255, 0, 0), 2))
                self.graphics_scene.addItem(point_item)
                self.polygon_items.append(point_item)
            return

        # Draw the polygon
        polygon = QPolygonF()
        for x, y in self.current_polygon:
            polygon.append(QPointF(x, y))

        polygon_item = QGraphicsPolygonItem(polygon)
        pen = QPen(QColor(0, 255, 0), 2, Qt.SolidLine)
        polygon_item.setPen(pen)
        polygon_item.setBrush(QBrush(QColor(0, 255, 0, 50)))
        self.graphics_scene.addItem(polygon_item)
        self.polygon_items.append(polygon_item)

    def _show_region(self):
        """Show the cropped and masked region."""
        if not self.polygons:
            QMessageBox.warning(
                self,
                "No Polygons",
                "Please draw at least one polygon first!"
            )
            return

        if self.current_image is None:
            return

        # Create a mask from all polygons
        h, w = self.current_image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)

        for polygon in self.polygons:
            pts = np.array(polygon, dtype=np.int32)
            cv2.fillPoly(mask, [pts], 255)

        # Apply mask to image
        masked = cv2.bitwise_and(self.current_image, self.current_image, mask=mask)

        # Find bounding box (extreme points)
        coords = np.column_stack(np.where(mask > 0))
        if coords.size == 0:
            QMessageBox.warning(self, "Empty Region", "The masked region is empty!")
            return

        y_min, x_min = coords.min(axis=0)
        y_max, x_max = coords.max(axis=0)

        # Crop to bounding box
        cropped = masked[y_min:y_max + 1, x_min:x_max + 1]
        cropped_mask = mask[y_min:y_max + 1, x_min:x_max + 1]

        # Set background to black where mask is 0
        cropped[cropped_mask == 0] = 0

        # Store for saving
        self.preview_pixmap = cropped.copy()

        # Display preview
        preview_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
        h_p, w_p, ch_p = preview_rgb.shape
        qimg = QImage(preview_rgb.data, w_p, h_p, ch_p * w_p, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimg)

        # Scale to fit label while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)

        logger.info(f"Segmented region: {w_p}x{h_p}")

    def _save_character(self):
        """Save the segmented character."""
        if self.preview_pixmap is None:
            QMessageBox.warning(
                self,
                "No Preview",
                "Please click 'Show Region' first to generate the preview!"
            )
            return

        character = self.char_input.text().strip()
        if not character:
            QMessageBox.warning(
                self,
                "No Character",
                "Please enter a character label!"
            )
            self.char_input.setFocus()
            return

        # Create character directory
        char_dir = self.save_dir / character
        char_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        timestamp = int(time.time() * 1000)
        filename = f"segmented_{timestamp}.png"
        save_path = char_dir / filename

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        # Save in background thread
        self.save_worker = SegmentSaveWorker(self.preview_pixmap, save_path, character)
        self.save_worker.finished.connect(self._on_save_finished)
        self.save_worker.error.connect(self._on_save_error)
        self.save_worker.start()

    def _on_save_finished(self, success: bool, character: str, path: str):
        """Handle save completion."""
        self.progress_bar.setVisible(False)

        if success:
            QMessageBox.information(
                self,
                "Saved",
                f"Character '{character}' saved successfully to:\n{path}"
            )
            self.character_saved.emit(character, path)
            logger.success(f"Saved character '{character}' to {path}")
            
            # Clear for next segmentation
            self._clear_polygons()
            self.char_input.clear()
        else:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save character '{character}'!"
            )

    def _on_save_error(self, error_msg: str):
        """Handle save error."""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(
            self,
            "Save Error",
            f"Error while saving: {error_msg}"
        )
        logger.error(f"Save error: {error_msg}")
