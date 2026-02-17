"""Character segmentation dialog for TextBaker.

This dialog allows users to segment characters from images by drawing polygons.

Features:
- Browse images with Previous/Next buttons
- Mouse wheel zoom in/out
- Draw polygons by clicking points (double-click to finish)
- Right-click to undo last point
- Show segmented region with black background
- Save segmented characters with labels
- **Invert color before saving** (optional)

Usage:
1. Click "Select Folder" and choose a folder containing images
2. Use Previous/Next to browse images
3. Click "Draw Polygon" to start drawing
4. Click to add points (circles show points)
5. Right-click to undo last point
6. Double-click to finish polygon
7. Click "Show Region" to preview the masked/cropped region
8. (Optional) Check "Invert color before saving"
9. Enter character label and save
"""

from pathlib import Path

import cv2
import numpy as np
from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
)


class SegmentDialog(QDialog):
    character_saved = Signal(str, str)  # character, image_path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Segment a Character")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        self.image_paths = []
        self.current_image = None
        self.current_image_idx = -1
        self.current_polygons = []
        self.masked_regions = []
        self.overlay_points = []
        self.zoom_factor = 1.0
        self.settings = QSettings("TextBaker", "SegmentDialog")

        layout = QVBoxLayout(self)

        folder_btn = QPushButton("Select Folder")
        folder_btn.clicked.connect(self.select_folder)
        layout.addWidget(folder_btn)

        # Info label
        info_label = QLabel(
            "💡 Mouse wheel: Zoom | Click: Add point | "
            "Right-click: Undo | Double-click: Finish polygon | "
            "[ ] Invert color before saving"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(info_label)

        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.prev_image)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_image)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        layout.addLayout(nav_layout)

        # Scrollable image area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        # Enable mouse wheel events
        self.image_label.wheelEvent = self.wheel_event
        scroll_area.setWidget(self.image_label)
        layout.addWidget(scroll_area)

        # --- Button and options layout ---
        action_layout = QHBoxLayout()
        self.draw_btn = QPushButton("Draw Polygon")
        self.draw_btn.clicked.connect(self.start_drawing)
        action_layout.addWidget(self.draw_btn)
        self.show_region_btn = QPushButton("Show Region")
        self.show_region_btn.clicked.connect(self.show_region)
        action_layout.addWidget(self.show_region_btn)
        layout.addLayout(action_layout)

        # Invert color checkbox
        self.invert_checkbox = QCheckBox("Invert color before saving")
        layout.addWidget(self.invert_checkbox)

        # Character input and refresh
        char_layout = QHBoxLayout()
        self.char_input = QLineEdit()
        self.char_input.setPlaceholderText("Enter character label")
        char_layout.addWidget(self.char_input)
        self.refresh_btn = QPushButton("⟳")
        self.refresh_btn.setToolTip("Refresh character list in main window")
        self.refresh_btn.clicked.connect(self.emit_refresh)
        char_layout.addWidget(self.refresh_btn)
        layout.addLayout(char_layout)

        # Save/cancel layout
        save_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save Cropped Region")
        self.save_btn.clicked.connect(self.save_region)
        save_layout.addWidget(self.save_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        save_layout.addWidget(cancel_btn)
        layout.addLayout(save_layout)

        self.drawing = False
        self.temp_polygon = []
        self.original_img = None

    def emit_refresh(self):
        # Just emit a dummy signal to trigger refresh in main window
        self.character_saved.emit("", "")

    def select_folder(self):
        # Load last used folder
        last_folder = self.settings.value("last_folder", "")
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", last_folder)
        if folder:
            # Save the selected folder
            self.settings.setValue("last_folder", folder)
            self.image_paths = (
                list(Path(folder).rglob("*.png"))
                + list(Path(folder).rglob("*.jpg"))
                + list(Path(folder).rglob("*.jpeg"))
                + list(Path(folder).rglob("*.bmp"))
            )
            self.current_image_idx = 0 if self.image_paths else -1
            self.load_image()

    def load_image(self, idx=None):
        if idx is not None:
            self.current_image_idx = idx
        if self.current_image_idx < 0 or self.current_image_idx >= len(self.image_paths):
            self.image_label.setText("No image loaded")
            self.current_image = None
            self.original_img = None
            return
        img_path = self.image_paths[self.current_image_idx]
        img = cv2.imread(str(img_path))
        self.current_image = img
        self.original_img = img.copy()
        self.current_polygons = []
        self.masked_regions = []
        self.overlay_points = []
        self.update_image_label()

    def update_image_label(self):
        if self.current_image is None:
            self.image_label.setText("No image loaded")
            return
        # Draw overlays on a copy
        disp_img = self.original_img.copy()
        # Draw completed polygons in red
        for poly in self.current_polygons:
            pts = np.array(poly, np.int32).reshape((-1, 1, 2))
            cv2.polylines(disp_img, [pts], isClosed=True, color=(0, 0, 255), thickness=2)
            # Draw circles on points
            for pt in poly:
                cv2.circle(disp_img, pt, 5, (0, 0, 255), -1)
        # Draw current polygon in green
        if self.drawing and self.temp_polygon:
            pts = np.array(self.temp_polygon, np.int32).reshape((-1, 1, 2))
            cv2.polylines(disp_img, [pts], isClosed=False, color=(0, 255, 0), thickness=2)
            # Draw circles on points
            for pt in self.temp_polygon:
                cv2.circle(disp_img, pt, 5, (0, 255, 0), -1)
        qimg = QImage(
            disp_img.data,
            disp_img.shape[1],
            disp_img.shape[0],
            disp_img.strides[0],
            QImage.Format_BGR888,
        )
        # Apply zoom
        scaled_width = int(disp_img.shape[1] * self.zoom_factor)
        scaled_height = int(disp_img.shape[0] * self.zoom_factor)
        self.image_label.setPixmap(
            QPixmap.fromImage(qimg).scaled(scaled_width, scaled_height, Qt.KeepAspectRatio)
        )

    def wheel_event(self, event):
        """Handle mouse wheel for zoom."""
        if self.current_image is not None:
            # Get scroll delta
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_factor *= 1.1
            else:
                self.zoom_factor /= 1.1
            # Limit zoom range
            self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))
            self.update_image_label()

    def zoom_in(self):
        self.zoom_factor *= 1.2
        self.update_image_label()

    def zoom_out(self):
        self.zoom_factor /= 1.2
        self.update_image_label()

    def zoom_reset(self):
        self.zoom_factor = 1.0
        self.update_image_label()

    def prev_image(self):
        if self.image_paths and self.current_image_idx > 0:
            self.current_image_idx -= 1
            self.load_image()

    def next_image(self):
        if self.image_paths and self.current_image_idx < len(self.image_paths) - 1:
            self.current_image_idx += 1
            self.load_image()

    def start_drawing(self):
        self.drawing = True
        self.temp_polygon = []
        self.image_label.mousePressEvent = self.mouse_press
        self.image_label.mouseDoubleClickEvent = self.mouse_double_click
        self.image_label.mouseReleaseEvent = self.mouse_release
        self.image_label.setCursor(Qt.CrossCursor)
        self.update_image_label()

    def mouse_press(self, event):
        if self.drawing and self.current_image is not None and event.button() == Qt.LeftButton:
            # Get pixmap and label sizes
            pixmap = self.image_label.pixmap()
            if pixmap is None:
                return
            pixmap_width = pixmap.width()
            pixmap_height = pixmap.height()
            label_width = self.image_label.width()
            label_height = self.image_label.height()
            # Centered pixmap offset
            x_offset = max((label_width - pixmap_width) // 2, 0)
            y_offset = max((label_height - pixmap_height) // 2, 0)
            # Mouse position relative to pixmap
            pos = event.position() if hasattr(event, "position") else event.pos()
            px = pos.x() - x_offset
            py = pos.y() - y_offset
            # Only add point if inside pixmap
            if 0 <= px < pixmap_width and 0 <= py < pixmap_height:
                x = int(px * self.current_image.shape[1] / pixmap_width)
                y = int(py * self.current_image.shape[0] / pixmap_height)
                self.temp_polygon.append((x, y))
                self.update_image_label()

    def mouse_release(self, event):
        """Handle right-click to undo last point."""
        if self.drawing and event.button() == Qt.RightButton and self.temp_polygon:
            self.temp_polygon.pop()
            self.update_image_label()

    def mouse_double_click(self, event):
        if self.drawing and len(self.temp_polygon) > 2:
            self.current_polygons.append(self.temp_polygon.copy())
            self.drawing = False
            self.temp_polygon = []
            self.image_label.setCursor(Qt.ArrowCursor)
            self.update_image_label()
            QMessageBox.information(
                self, "Polygon", "Polygon added. You can draw more or show region."
            )

    def show_region(self):
        if self.current_image is None or not self.current_polygons:
            QMessageBox.warning(self, "No region", "Draw at least one polygon.")
            return
        mask = np.zeros(self.current_image.shape[:2], dtype=np.uint8)
        for poly in self.current_polygons:
            pts = np.array(poly, dtype=np.int32)
            cv2.fillPoly(mask, [pts], 255)
        masked = cv2.bitwise_and(self.current_image, self.current_image, mask=mask)
        ys, xs = np.where(mask)
        if len(xs) == 0 or len(ys) == 0:
            QMessageBox.warning(self, "Empty region", "No region found.")
            return
        min_x, max_x = xs.min(), xs.max()
        min_y, max_y = ys.min(), ys.max()
        cropped = masked[min_y : max_y + 1, min_x : max_x + 1]
        bg = np.zeros_like(cropped)
        bg[mask[min_y : max_y + 1, min_x : max_x + 1] > 0] = cropped[
            mask[min_y : max_y + 1, min_x : max_x + 1] > 0
        ]
        self.masked_regions.append(bg)
        qimg = QImage(bg.data, bg.shape[1], bg.shape[0], bg.strides[0], QImage.Format_BGR888)
        self.image_label.setPixmap(QPixmap.fromImage(qimg).scaled(400, 400, Qt.KeepAspectRatio))

    def save_region(self):
        if not self.masked_regions:
            QMessageBox.warning(self, "No region", "Show region first.")
            return
        char = self.char_input.text().strip()
        if not char:
            QMessageBox.warning(self, "No character", "Enter character label.")
            return
        base_dir = Path.cwd() / ".textbaker" / "custom_characters" / char
        base_dir.mkdir(parents=True, exist_ok=True)
        idx = len(list(base_dir.glob("*.png")))
        fname = f"{char}_{idx}.png"
        save_path = str(base_dir / fname)
        img = self.masked_regions[-1]
        if self.invert_checkbox.isChecked():
            img = cv2.bitwise_not(img)
        cv2.imwrite(save_path, img)
        self.character_saved.emit(char, save_path)
        QMessageBox.information(self, "Saved", f"Saved as {save_path}")
