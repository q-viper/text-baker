import sys
import os
import random
import argparse
import string
import numpy as np
import cv2
from pathlib import Path
from loguru import logger
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QCheckBox,
                               QGridLayout, QSpinBox, QDoubleSpinBox, QFileDialog,
                               QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                               QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsItem,
                               QDialog, QTextEdit, QFrame, QSlider, QGroupBox, QTextBrowser,
                               QLineEdit, QDockWidget, QScrollArea, QRadioButton, QButtonGroup,
                               QMessageBox)
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer, Signal, QObject, QSize, QEvent
from PySide6.QtGui import QPixmap, QImage, QWheelEvent, QPainter, QPen, QColor, QBrush, QTransform, QCursor, QPainterPath, QFont, QMouseEvent

os.environ["OPENCV_LOG_LEVEL"] = "FATAL"
cv2.setLogLevel(3)

np.random.seed(100)
random.seed(100)

# Configure loguru
logger.remove()  # Remove default handler
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


class LogHandler(QObject):
    """Handler to capture loguru logs and emit them as Qt signals"""
    log_signal = Signal(str)
    
    def write(self, message):
        if message.strip():
            self.log_signal.emit(message.strip())


class TexturePickerDialog(QDialog):
    """Dialog for selecting texture regions"""
    def __init__(self, texture_paths, background_paths, parent=None):
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
        self.selected_region = None
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        self.selection_rect_item = None
        
        self.init_ui()
        self.load_current_texture()
        self.random_select_region()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Info label
        if self.using_backgrounds:
            info = QLabel("⚠️ Using background images as textures (texture folder is empty)")
            info.setStyleSheet("background: #FF9800; color: white; padding: 8px; font-weight: bold;")
            layout.addWidget(info)
        else:
            info = QLabel("✨ Drag mouse to select a texture region (or use Random Region button)")
            info.setStyleSheet("background: #4CAF50; color: white; padding: 8px;")
            layout.addWidget(info)
        
        # Graphics view for texture display
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setDragMode(QGraphicsView.NoDrag)
        layout.addWidget(self.graphics_view)
        
        # Navigation buttons
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
        """Load and display current texture"""
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
        
        # Update info
        self.texture_info_label.setText(f"{self.current_index + 1} / {len(self.texture_paths)}")
        
        logger.info(f"Loaded texture: {texture_path.name} [{w}x{h}]")
    
    def prev_texture(self):
        """Navigate to previous texture"""
        self.current_index = (self.current_index - 1) % len(self.texture_paths)
        self.load_current_texture()
        self.random_select_region()
    
    def next_texture(self):
        """Navigate to next texture"""
        self.current_index = (self.current_index + 1) % len(self.texture_paths)
        self.load_current_texture()
        self.random_select_region()
    
    def random_select_region(self):
        """Randomly select a region from the texture"""
        if self.current_image is None:
            return
        
        h, w = self.current_image.shape[:2]
        
        # Random region size (20% to 60% of image)
        region_w = random.randint(int(w * 0.2), int(w * 0.6))
        region_h = random.randint(int(h * 0.2), int(h * 0.6))
        
        # Random position
        x = random.randint(0, w - region_w)
        y = random.randint(0, h - region_h)
        
        self.selected_region = (x, y, region_w, region_h)
        self.draw_selection()
        
        logger.info(f"Random region: ({x}, {y}) [{region_w}x{region_h}]")
    
    def draw_selection(self):
        """Draw the selection rectangle on the image"""
        # Remove old selection rectangle if exists
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
        """Handle mouse events for drag selection"""
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
                        self.draw_selection()
                    
                    return True
            
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if isinstance(event, QMouseEvent) and event.button() == Qt.LeftButton:
                    self.is_selecting = False
                    if self.selected_region:
                        x, y, w, h = self.selected_region
                        logger.info(f"Selected region: ({x}, {y}) [{w}x{h}]")
                    return True
        
        return super().eventFilter(obj, event)
    
    def accept_selection(self):
        """Accept the selected region and close dialog"""
        if self.selected_region is None:
            QMessageBox.warning(self, "No Selection", "Please select a region first!")
            return
        
        x, y, w, h = self.selected_region
        if w < 10 or h < 10:
            QMessageBox.warning(self, "Invalid Selection", "Selected region is too small!")
            return
        
        logger.success(f"Texture region selected: ({x}, {y}) [{w}x{h}] from {self.texture_paths[self.current_index].name}")
        self.accept()
    
    def get_selected_texture(self):
        """Get the selected texture region as an image"""
        if self.selected_region is None or self.current_image is None:
            return None
        
        x, y, w, h = self.selected_region
        return self.current_image[y:y+h, x:x+w].copy()


class HintsDialog(QDialog):
    """Dialog to show keyboard shortcuts and hints"""
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


class ResizableRotatableTextItem(QGraphicsPixmapItem):
    """Text overlay with rotation handle, resize handles, and dotted border"""
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsPixmapItem.ItemSendsGeometryChanges, True)
        self.setZValue(1)
        self.setCursor(QCursor(Qt.OpenHandCursor))
        self.setAcceptHoverEvents(True)
        
        self.setShapeMode(QGraphicsPixmapItem.BoundingRectShape)
        
        center = self.boundingRect().center()
        self.setTransformOriginPoint(center)
        
        # Border
        self.border = QGraphicsRectItem(self.boundingRect(), self)
        pen = QPen(QColor(0, 150, 255), 2, Qt.DashLine)
        self.border.setPen(pen)
        self.border.setBrush(QBrush(Qt.NoBrush))
        self.border.setVisible(False)
        
        # Rotation handle
        handle_size = 25
        rect = self.boundingRect()
        self.rotation_handle = QGraphicsEllipseItem(
            center.x() - handle_size/2, 
            center.y() - handle_size/2, 
            handle_size, 
            handle_size, 
            self
        )
        self.rotation_handle.setBrush(QBrush(QColor(0, 150, 255, 180)))
        self.rotation_handle.setPen(QPen(QColor(255, 255, 255), 2))
        self.rotation_handle.setVisible(False)
        self.rotation_handle.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Resize handles
        self.resize_handle_size = 12
        self.resize_handles = []
        positions = [
            (rect.left(), rect.top()),
            (rect.right(), rect.top()),
            (rect.right(), rect.bottom()),
            (rect.left(), rect.bottom()),
        ]
        
        cursors = [
            Qt.SizeFDiagCursor,
            Qt.SizeBDiagCursor,
            Qt.SizeFDiagCursor,
            Qt.SizeBDiagCursor,
        ]
        
        for i, (x, y) in enumerate(positions):
            handle = QGraphicsRectItem(
                x - self.resize_handle_size/2,
                y - self.resize_handle_size/2,
                self.resize_handle_size,
                self.resize_handle_size,
                self
            )
            handle.setBrush(QBrush(QColor(255, 150, 0, 200)))
            handle.setPen(QPen(QColor(255, 255, 255), 2))
            handle.setVisible(False)
            handle.setCursor(QCursor(cursors[i]))
            self.resize_handles.append(handle)
        
        self.dragging_handle = False
        self.dragging_resize = False
        self.resize_handle_index = -1
        self.initial_angle = 0
        self.initial_rotation = 0
        self.initial_pixmap = None
        
        # Resize tracking variables
        self.initial_rect = None
        self.initial_pos = None
        self.resize_start_item_pos = None
    
    def shape(self):
        path = QPainterPath()
        path.addRect(self.boundingRect())
        return path
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            selected = value
            self.border.setVisible(selected)
            self.rotation_handle.setVisible(selected)
            for handle in self.resize_handles:
                handle.setVisible(selected)
        return super().itemChange(change, value)
    
    def get_handle_at_pos(self, pos):
        for i, handle in enumerate(self.resize_handles):
            if handle.rect().contains(pos):
                return i
        return -1
    
    def hoverMoveEvent(self, event):
        if self.isSelected():
            pos = event.pos()
            handle_idx = self.get_handle_at_pos(pos)
            if handle_idx >= 0:
                self.setCursor(self.resize_handles[handle_idx].cursor())
                return
            if self.rotation_handle.rect().contains(pos):
                self.setCursor(QCursor(Qt.PointingHandCursor))
                return
            self.setCursor(QCursor(Qt.OpenHandCursor))
        super().hoverMoveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            return
            
        if not self.isSelected():
            self.setSelected(True)
            event.accept()
            return
        
        click_pos = event.pos()
        
        handle_idx = self.get_handle_at_pos(click_pos)
        if handle_idx >= 0:
            self.dragging_resize = True
            self.resize_handle_index = handle_idx
            self.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
            
            self.initial_pixmap = self.pixmap()
            self.initial_rect = self.boundingRect()
            self.initial_pos = self.pos()
            self.resize_start_item_pos = event.pos()
            
            logger.info(f"Resize started from corner {handle_idx}")
            event.accept()
            return
        
        if self.rotation_handle.rect().contains(click_pos):
            self.dragging_handle = True
            self.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
            
            self.rotation_handle.setBrush(QBrush(QColor(76, 175, 80, 200)))
            self.border.setPen(QPen(QColor(76, 175, 80), 2, Qt.DashLine))
            
            center_scene = self.mapToScene(self.boundingRect().center())
            click_scene = event.scenePos()
            
            dx = click_scene.x() - center_scene.x()
            dy = click_scene.y() - center_scene.y()
            self.initial_angle = np.arctan2(dy, dx)
            self.initial_rotation = self.rotation()
            
            logger.info(f"Rotation started: {self.initial_rotation:.1f}°")
            event.accept()
            return
        
        self.setCursor(QCursor(Qt.ClosedHandCursor))
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.dragging_resize:
            current_item_pos = event.pos()
            delta_x = current_item_pos.x() - self.resize_start_item_pos.x()
            delta_y = current_item_pos.y() - self.resize_start_item_pos.y()
            
            initial_width = self.initial_rect.width()
            initial_height = self.initial_rect.height()
            
            new_width = initial_width
            new_height = initial_height
            offset_x = 0
            offset_y = 0
            
            if self.resize_handle_index == 0:  # Top-left
                new_width = initial_width - delta_x
                new_height = initial_height - delta_y
                offset_x = delta_x
                offset_y = delta_y
            elif self.resize_handle_index == 1:  # Top-right
                new_width = initial_width + delta_x
                new_height = initial_height - delta_y
                offset_y = delta_y
            elif self.resize_handle_index == 2:  # Bottom-right
                new_width = initial_width + delta_x
                new_height = initial_height + delta_y
            elif self.resize_handle_index == 3:  # Bottom-left
                new_width = initial_width - delta_x
                new_height = initial_height + delta_y
                offset_x = delta_x
            
            if new_width > 20 and new_height > 20:
                scaled_pixmap = self.initial_pixmap.scaled(
                    int(new_width), 
                    int(new_height),
                    Qt.IgnoreAspectRatio,
                    Qt.SmoothTransformation
                )
                self.setPixmap(scaled_pixmap)
                
                angle_rad = np.radians(self.rotation())
                cos_a = np.cos(angle_rad)
                sin_a = np.sin(angle_rad)
                
                offset_x_rotated = offset_x * cos_a - offset_y * sin_a
                offset_y_rotated = offset_x * sin_a + offset_y * cos_a
                
                new_pos = QPointF(
                    self.initial_pos.x() + offset_x_rotated,
                    self.initial_pos.y() + offset_y_rotated
                )
                self.setPos(new_pos)
                
                new_center = self.boundingRect().center()
                self.setTransformOriginPoint(new_center)
                
                self.update_handles()
            
            event.accept()
            
        elif self.dragging_handle:
            center_scene = self.mapToScene(self.boundingRect().center())
            mouse_scene = event.scenePos()
            
            dx = mouse_scene.x() - center_scene.x()
            dy = mouse_scene.y() - center_scene.y()
            current_angle = np.arctan2(dy, dx)
            
            angle_diff = np.degrees(current_angle - self.initial_angle)
            new_rotation = self.initial_rotation + angle_diff
            self.setRotation(new_rotation)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() != Qt.LeftButton:
            event.ignore()
            return
            
        if self.dragging_resize:
            self.dragging_resize = False
            self.resize_handle_index = -1
            self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
            logger.info(f"Resize finished: {self.boundingRect().width():.0f}x{self.boundingRect().height():.0f}")
            event.accept()
            
        elif self.dragging_handle:
            self.dragging_handle = False
            self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
            self.setCursor(QCursor(Qt.OpenHandCursor))
            
            self.rotation_handle.setBrush(QBrush(QColor(0, 150, 255, 180)))
            self.border.setPen(QPen(QColor(0, 150, 255), 2, Qt.DashLine))
            
            logger.info(f"Rotation finished: {self.rotation():.1f}°")
            event.accept()
        else:
            self.setCursor(QCursor(Qt.OpenHandCursor))
            super().mouseReleaseEvent(event)
    
    def update_handles(self):
        rect = self.boundingRect()
        center = rect.center()
        
        self.border.setRect(rect)
        
        handle_size = 25
        self.rotation_handle.setRect(
            center.x() - handle_size/2,
            center.y() - handle_size/2,
            handle_size,
            handle_size
        )
        
        positions = [
            (rect.left(), rect.top()),
            (rect.right(), rect.top()),
            (rect.right(), rect.bottom()),
            (rect.left(), rect.bottom()),
        ]
        
        for handle, (x, y) in zip(self.resize_handles, positions):
            handle.setRect(
                x - self.resize_handle_size/2,
                y - self.resize_handle_size/2,
                self.resize_handle_size,
                self.resize_handle_size
            )


class InteractiveGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setInteractive(True)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)
        
        self.zoom_factor = 1.0
        self.panning = False
        self.pan_start = QPointF()
        
    def wheelEvent(self, event: QWheelEvent):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self.zoom_factor *= zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
            self.zoom_factor *= zoom_out_factor
        
        self.scale(zoom_factor, zoom_factor)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space and not self.panning:
            self.panning = True
            self.viewport().setCursor(QCursor(Qt.OpenHandCursor))
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.panning = False
            self.viewport().setCursor(QCursor(Qt.ArrowCursor))
        super().keyReleaseEvent(event)
    
    def mousePressEvent(self, event):
        if self.panning and event.button() == Qt.LeftButton:
            self.pan_start = event.pos()
            self.viewport().setCursor(QCursor(Qt.ClosedHandCursor))
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.panning:
            delta = event.pos() - self.pan_start
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.pan_start = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if self.panning:
            self.viewport().setCursor(QCursor(Qt.OpenHandCursor))
            event.accept()
        else:
            super().mouseReleaseEvent(event)


class DatasetMaker(QMainWindow):
    def __init__(self, dataset_root=None, output_dir=None, background_dir=None, texture_dir=None):
        super().__init__()
        self.setWindowTitle("Synthetic Text Dataset Generator")
        self.resize(1600, 900)
        
        self.dataset_root = Path(dataset_root or "")
        self.output_dir = Path(output_dir or "")
        self.background_dir = Path(background_dir or "")
        self.texture_dir = Path(texture_dir or r"C:\Users\Z0064JH3\Pictures\Screenshots")
        
        self.character_paths = {}
        self.background_paths = []
        self.texture_paths = []
        
        self.current_composite = None
        self.current_background = None
        self.text_item = None
        self.background_item = None
        self.last_text_position = None
        self.last_text_rotation = 0
        self.current_perspective_angle = 0
        self.current_number = ""
        
        self.original_pixmap = None
        self.original_position = None
        
        # Texture picker
        self.selected_texture_region = None
        
        # Setup log handler
        self.log_handler = LogHandler()
        logger.add(self.log_handler.write, format="{time:HH:mm:ss} | {level} | {message}")
        
        self.init_ui()
        
        if self.dataset_root.exists():
            self.scan_dataset()
        if self.background_dir.exists():
            self.scan_backgrounds()
        if self.texture_dir.exists():
            self.scan_textures()
        
        QTimer.singleShot(100, self.auto_start)
    
    def auto_start(self):
        if self.background_paths and len([cb for cb in self.character_checkboxes.values() if cb.isChecked()]) > 0:
            logger.info("Auto-starting...")
            self.load_random_background()
            QTimer.singleShot(50, self.generate_text)
    
    def show_hints(self):
        dialog = HintsDialog(self)
        dialog.exec()
    
    def append_log(self, message):
        self.log_display.append(message)
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def create_scroll_widget(self, widget):
        """Wrap a widget in a scroll area"""
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        return scroll
    
    def open_texture_picker(self):
        """Open texture picker dialog"""
        if not self.texture_paths and not self.background_paths:
            QMessageBox.warning(self, "No Images", "No texture or background images available!")
            return
        
        dialog = TexturePickerDialog(self.texture_paths, self.background_paths, self)
        if dialog.exec() == QDialog.Accepted:
            self.selected_texture_region = dialog.get_selected_texture()
            if self.selected_texture_region is not None:
                logger.success(f"Texture region selected: {self.selected_texture_region.shape}")
            else:
                logger.warning("No texture region selected")
    
    def init_ui(self):
        # Central widget - Graphics View
        self.graphics_view = InteractiveGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.setCentralWidget(self.graphics_view)
        
        # === LEFT DOCK: Folders & Characters ===
        left_dock = QDockWidget("Input Settings", self)
        left_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Folders
        folder_group = QGroupBox("📁 Folders")
        folder_layout = QVBoxLayout()
        
        dataset_btn = QPushButton("Dataset Folder")
        dataset_btn.clicked.connect(self.select_dataset)
        folder_layout.addWidget(dataset_btn)
        self.dataset_label = QLabel(f"{self.dataset_root.name if self.dataset_root.exists() else 'None'}")
        self.dataset_label.setWordWrap(True)
        folder_layout.addWidget(self.dataset_label)
        
        output_btn = QPushButton("Output Folder")
        output_btn.clicked.connect(self.select_output)
        folder_layout.addWidget(output_btn)
        self.output_label = QLabel(f"{self.output_dir.name if self.output_dir.exists() else 'None'}")
        self.output_label.setWordWrap(True)
        folder_layout.addWidget(self.output_label)
        
        bg_btn = QPushButton("Background Folder")
        bg_btn.clicked.connect(self.select_backgrounds)
        folder_layout.addWidget(bg_btn)
        self.bg_label = QLabel(f"0 backgrounds")
        folder_layout.addWidget(self.bg_label)
        
        texture_btn = QPushButton("Texture Folder")
        texture_btn.clicked.connect(self.select_textures)
        folder_layout.addWidget(texture_btn)
        self.texture_label = QLabel(f"{self.texture_dir.name if self.texture_dir.exists() else 'None'}")
        self.texture_label.setWordWrap(True)
        folder_layout.addWidget(self.texture_label)
        
        folder_group.setLayout(folder_layout)
        left_layout.addWidget(folder_group)
        
        # Texture Mode
        texture_mode_group = QGroupBox("🎨 Texture Application")
        texture_mode_layout = QVBoxLayout()
        
        self.texture_button_group = QButtonGroup()
        
        self.no_texture_radio = QRadioButton("No Texture (use original colors)")
        self.no_texture_radio.setChecked(True)  # Default
        self.texture_per_char_radio = QRadioButton("Per Character")
        self.texture_whole_text_radio = QRadioButton("Whole Text")
        
        self.texture_button_group.addButton(self.no_texture_radio)
        self.texture_button_group.addButton(self.texture_per_char_radio)
        self.texture_button_group.addButton(self.texture_whole_text_radio)
        
        texture_mode_layout.addWidget(self.no_texture_radio)
        texture_mode_layout.addWidget(self.texture_per_char_radio)
        texture_mode_layout.addWidget(self.texture_whole_text_radio)
        
        # Texture picker button
        pick_texture_btn = QPushButton("🎨 Pick Texture Region")
        pick_texture_btn.clicked.connect(self.open_texture_picker)
        pick_texture_btn.setStyleSheet("""
            QPushButton {
                background: #673AB7; 
                color: white; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5E35B1;
                color: white;
            }
        """)
        texture_mode_layout.addWidget(pick_texture_btn)
        
        texture_mode_group.setLayout(texture_mode_layout)
        left_layout.addWidget(texture_mode_group)
        
        # Custom Text
        text_group = QGroupBox("📝 Custom Text")
        text_layout = QVBoxLayout()
        
        text_layout.addWidget(QLabel("Character Pool:"))
        self.custom_text_input = QLineEdit()
        self.custom_text_input.setPlaceholderText("e.g., ABC123 (chars to use)")
        self.custom_text_input.textChanged.connect(self.on_custom_text_changed)
        text_layout.addWidget(self.custom_text_input)
        
        self.randomize_text_checkbox = QCheckBox("Randomize from pool")
        self.randomize_text_checkbox.setChecked(False)
        self.randomize_text_checkbox.toggled.connect(self.toggle_randomize_controls)
        text_layout.addWidget(self.randomize_text_checkbox)
        
        random_len_layout = QHBoxLayout()
        random_len_layout.addWidget(QLabel("Length:"))
        self.min_random_chars = QSpinBox()
        self.min_random_chars.setRange(1, 30)
        self.min_random_chars.setValue(5)
        self.min_random_chars.setEnabled(False)
        random_len_layout.addWidget(self.min_random_chars)
        random_len_layout.addWidget(QLabel("-"))
        self.max_random_chars = QSpinBox()
        self.max_random_chars.setRange(1, 30)
        self.max_random_chars.setValue(10)
        self.max_random_chars.setEnabled(False)
        random_len_layout.addWidget(self.max_random_chars)
        text_layout.addLayout(random_len_layout)
        
        text_group.setLayout(text_layout)
        left_layout.addWidget(text_group)
        
        # Character Selection (scrollable)
        char_group = QGroupBox("🔤 Character Selection")
        char_layout = QVBoxLayout()
        
        self.characters_widget = QWidget()
        self.characters_layout = QVBoxLayout(self.characters_widget)
        self.character_checkboxes = {}
        
        char_scroll = QScrollArea()
        char_scroll.setWidget(self.characters_widget)
        char_scroll.setWidgetResizable(True)
        char_scroll.setMinimumHeight(200)
        
        char_layout.addWidget(char_scroll)
        char_group.setLayout(char_layout)
        left_layout.addWidget(char_group)
        
        # Crop to Text (moved here)
        self.crop_to_text_checkbox = QCheckBox("Crop to Text when saving")
        self.crop_to_text_checkbox.setChecked(True)
        left_layout.addWidget(self.crop_to_text_checkbox)
        
        left_layout.addStretch()
        left_dock.setWidget(self.create_scroll_widget(left_widget))
        self.addDockWidget(Qt.LeftDockWidgetArea, left_dock)
        
        # === RIGHT DOCK: Parameters ===
        right_dock = QDockWidget("Generation Parameters", self)
        right_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Number Parameters
        num_group = QGroupBox("🎲 Generation Parameters")
        num_layout = QVBoxLayout()
        
        # Character Dimension
        char_dim_layout = QHBoxLayout()
        char_dim_layout.addWidget(QLabel("Char Dimension:"))
        self.char_dimension = QSpinBox()
        self.char_dimension.setRange(32, 256)
        self.char_dimension.setValue(64)
        self.char_dimension.setSuffix(" px")
        char_dim_layout.addWidget(self.char_dimension)
        num_layout.addLayout(char_dim_layout)
        
        char_count_layout = QHBoxLayout()
        char_count_layout.addWidget(QLabel("Count:"))
        self.min_chars = QSpinBox()
        self.min_chars.setRange(1, 20)
        self.min_chars.setValue(4)
        char_count_layout.addWidget(self.min_chars)
        char_count_layout.addWidget(QLabel("-"))
        self.max_chars = QSpinBox()
        self.max_chars.setRange(1, 20)
        self.max_chars.setValue(6)
        char_count_layout.addWidget(self.max_chars)
        num_layout.addLayout(char_count_layout)
        
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale:"))
        self.min_resize_scale = QDoubleSpinBox()
        self.min_resize_scale.setRange(0.3, 2.0)
        self.min_resize_scale.setValue(0.9)
        self.min_resize_scale.setDecimals(2)
        scale_layout.addWidget(self.min_resize_scale)
        scale_layout.addWidget(QLabel("-"))
        self.max_resize_scale = QDoubleSpinBox()
        self.max_resize_scale.setRange(0.3, 2.0)
        self.max_resize_scale.setValue(1.2)
        self.max_resize_scale.setDecimals(2)
        scale_layout.addWidget(self.max_resize_scale)
        num_layout.addLayout(scale_layout)
        
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Rotation:"))
        self.min_rotation = QSpinBox()
        self.min_rotation.setRange(-45, 45)
        self.min_rotation.setValue(-15)
        rotation_layout.addWidget(self.min_rotation)
        rotation_layout.addWidget(QLabel("-"))
        self.max_rotation = QSpinBox()
        self.max_rotation.setRange(-45, 45)
        self.max_rotation.setValue(15)
        rotation_layout.addWidget(self.max_rotation)
        num_layout.addLayout(rotation_layout)
        
        perspective_layout = QHBoxLayout()
        perspective_layout.addWidget(QLabel("Perspective:"))
        self.min_perspective = QSpinBox()
        self.min_perspective.setRange(0, 45)
        self.min_perspective.setValue(0)
        perspective_layout.addWidget(self.min_perspective)
        perspective_layout.addWidget(QLabel("-"))
        self.max_perspective = QSpinBox()
        self.max_perspective.setRange(0, 45)
        self.max_perspective.setValue(15)
        perspective_layout.addWidget(self.max_perspective)
        num_layout.addLayout(perspective_layout)
        
        h_margin_layout = QHBoxLayout()
        h_margin_layout.addWidget(QLabel("H-Margin:"))
        self.min_h_margin = QSpinBox()
        self.min_h_margin.setRange(0, 50)
        self.min_h_margin.setValue(2)
        h_margin_layout.addWidget(self.min_h_margin)
        h_margin_layout.addWidget(QLabel("-"))
        self.max_h_margin = QSpinBox()
        self.max_h_margin.setRange(0, 50)
        self.max_h_margin.setValue(10)
        h_margin_layout.addWidget(self.max_h_margin)
        num_layout.addLayout(h_margin_layout)
        
        canvas_layout = QHBoxLayout()
        canvas_layout.addWidget(QLabel("Canvas H:"))
        self.canvas_height = QSpinBox()
        self.canvas_height.setRange(64, 256)
        self.canvas_height.setValue(128)
        canvas_layout.addWidget(self.canvas_height)
        num_layout.addLayout(canvas_layout)
        
        v_offset_layout = QHBoxLayout()
        v_offset_layout.addWidget(QLabel("V-Offset:"))
        self.max_v_offset = QSpinBox()
        self.max_v_offset.setRange(0, 64)
        self.max_v_offset.setValue(20)
        v_offset_layout.addWidget(self.max_v_offset)
        num_layout.addLayout(v_offset_layout)
        
        font_scale_layout = QHBoxLayout()
        font_scale_layout.addWidget(QLabel("Font Scale:"))
        self.font_scale = QDoubleSpinBox()
        self.font_scale.setRange(0.5, 3.0)
        self.font_scale.setValue(1.5)
        self.font_scale.setDecimals(1)
        font_scale_layout.addWidget(self.font_scale)
        num_layout.addLayout(font_scale_layout)
        
        num_group.setLayout(num_layout)
        right_layout.addWidget(num_group)
        
        # Transform Controls
        transform_group = QGroupBox("🔄 Transform")
        transform_layout = QVBoxLayout()
        
        transform_layout.addWidget(QLabel("Text Perspective:"))
        persp_slider_layout = QHBoxLayout()
        self.text_perspective_slider = QSlider(Qt.Horizontal)
        self.text_perspective_slider.setRange(-45, 45)
        self.text_perspective_slider.setValue(0)
        self.text_perspective_slider.setTickPosition(QSlider.TicksBelow)
        self.text_perspective_slider.setTickInterval(15)
        self.text_perspective_slider.valueChanged.connect(self.apply_text_perspective)
        persp_slider_layout.addWidget(self.text_perspective_slider)
        self.text_perspective_label = QLabel("0°")
        self.text_perspective_label.setMinimumWidth(35)
        persp_slider_layout.addWidget(self.text_perspective_label)
        transform_layout.addLayout(persp_slider_layout)
        
        reset_transform_btn = QPushButton("🔄 Reset Transform")
        reset_transform_btn.clicked.connect(self.reset_transform)
        reset_transform_btn.setStyleSheet("""
            QPushButton {
                background: #607D8B; 
                color: white; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background: #546E7A;
                color: white;
            }
        """)
        transform_layout.addWidget(reset_transform_btn)
        
        transform_group.setLayout(transform_layout)
        right_layout.addWidget(transform_group)
        
        # Color Options
        color_group = QGroupBox("🎨 Color")
        color_layout = QVBoxLayout()
        
        self.enable_color_checkbox = QCheckBox("Enable Random Colors")
        self.enable_color_checkbox.setChecked(False)
        self.enable_color_checkbox.toggled.connect(self.toggle_color_controls)
        color_layout.addWidget(self.enable_color_checkbox)
        
        rgb_r_layout = QHBoxLayout()
        rgb_r_layout.addWidget(QLabel("R:"))
        self.min_r = QSpinBox()
        self.min_r.setRange(0, 255)
        self.min_r.setValue(100)
        self.min_r.setEnabled(False)
        rgb_r_layout.addWidget(self.min_r)
        rgb_r_layout.addWidget(QLabel("-"))
        self.max_r = QSpinBox()
        self.max_r.setRange(0, 255)
        self.max_r.setValue(255)
        self.max_r.setEnabled(False)
        rgb_r_layout.addWidget(self.max_r)
        color_layout.addLayout(rgb_r_layout)
        
        rgb_g_layout = QHBoxLayout()
        rgb_g_layout.addWidget(QLabel("G:"))
        self.min_g = QSpinBox()
        self.min_g.setRange(0, 255)
        self.min_g.setValue(100)
        self.min_g.setEnabled(False)
        rgb_g_layout.addWidget(self.min_g)
        rgb_g_layout.addWidget(QLabel("-"))
        self.max_g = QSpinBox()
        self.max_g.setRange(0, 255)
        self.max_g.setValue(255)
        self.max_g.setEnabled(False)
        rgb_g_layout.addWidget(self.max_g)
        color_layout.addLayout(rgb_g_layout)
        
        rgb_b_layout = QHBoxLayout()
        rgb_b_layout.addWidget(QLabel("B:"))
        self.min_b = QSpinBox()
        self.min_b.setRange(0, 255)
        self.min_b.setValue(100)
        self.min_b.setEnabled(False)
        rgb_b_layout.addWidget(self.min_b)
        rgb_b_layout.addWidget(QLabel("-"))
        self.max_b = QSpinBox()
        self.max_b.setRange(0, 255)
        self.max_b.setValue(255)
        self.max_b.setEnabled(False)
        rgb_b_layout.addWidget(self.max_b)
        color_layout.addLayout(rgb_b_layout)
        
        color_group.setLayout(color_layout)
        right_layout.addWidget(color_group)
        
        right_layout.addStretch()
        right_dock.setWidget(self.create_scroll_widget(right_widget))
        self.addDockWidget(Qt.RightDockWidgetArea, right_dock)
        
        # === BOTTOM DOCK: Actions & Logs ===
        bottom_dock = QDockWidget("Actions & Logs", self)
        bottom_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Actions
        action_layout = QHBoxLayout()
        
        generate_btn = QPushButton("🎲 Generate Random Text")
        generate_btn.clicked.connect(self.generate_text)
        generate_btn.setStyleSheet("""
            QPushButton {
                background: #4CAF50; 
                color: white; 
                font-size: 11px; 
                padding: 10px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
                color: white;
            }
        """)
        action_layout.addWidget(generate_btn)
        
        load_bg_btn = QPushButton("🖼️ Select Random Background")
        load_bg_btn.clicked.connect(self.load_random_background)
        load_bg_btn.setStyleSheet("""
            QPushButton {
                background: #FF9800; 
                color: white; 
                font-size: 11px; 
                padding: 10px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background: #FB8C00;
                color: white;
            }
        """)
        action_layout.addWidget(load_bg_btn)
        
        self.save_btn = QPushButton("💾 Save Image")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3; 
                color: white; 
                font-size: 11px; 
                padding: 10px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1E88E5;
                color: white;
            }
        """)
        action_layout.addWidget(self.save_btn)
        
        hints_btn = QPushButton("❓")
        hints_btn.clicked.connect(self.show_hints)
        hints_btn.setStyleSheet("""
            QPushButton {
                background: #9C27B0; 
                color: white; 
                font-size: 11px; 
                padding: 10px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background: #8E24AA;
                color: white;
            }
        """)
        action_layout.addWidget(hints_btn)
        
        bottom_layout.addLayout(action_layout)
        
        # Generated text display
        text_display_layout = QHBoxLayout()
        self.generated_text_label = QLabel("Generated: <span style='background: #FFD700; color: #000; padding: 4px 8px; border-radius: 3px; font-weight: bold;'>None</span>")
        self.generated_text_label.setTextFormat(Qt.RichText)
        text_display_layout.addWidget(self.generated_text_label)
        text_display_layout.addStretch()
        bottom_layout.addLayout(text_display_layout)
        
        # Logs
        log_label = QLabel("📋 Logs:")
        bottom_layout.addWidget(log_label)
        self.log_display = QTextBrowser()
        self.log_display.setMaximumHeight(60)
        self.log_display.setStyleSheet("background: #1e1e1e; color: #00ff00; font-family: monospace; font-size: 10px;")
        bottom_layout.addWidget(self.log_display)
        
        bottom_dock.setWidget(bottom_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, bottom_dock)
        
        # Connect log handler
        self.log_handler.log_signal.connect(self.append_log)
        
        logger.info("Application ready - drag to select texture regions!")
    
    def update_generated_text_display(self):
        """Update the generated text display label"""
        if self.current_number:
            self.generated_text_label.setText(
                f"Generated: <span style='background: #FFD700; color: #000; padding: 4px 8px; border-radius: 3px; font-weight: bold;'>{self.current_number}</span>"
            )
        else:
            self.generated_text_label.setText(
                "Generated: <span style='background: #FFD700; color: #000; padding: 4px 8px; border-radius: 3px; font-weight: bold;'>None</span>"
            )
    
    def toggle_randomize_controls(self, enabled):
        """Enable/disable randomize character length controls"""
        self.min_random_chars.setEnabled(enabled)
        self.max_random_chars.setEnabled(enabled)
        if enabled:
            logger.info("Random text generation enabled")
        else:
            logger.info("Using exact custom text")
    
    def generate_random_text(self):
        """Generate random text from custom text pool"""
        char_pool = self.custom_text_input.text().strip()
        if not char_pool:
            char_pool = ''.join([char for char, cb in self.character_checkboxes.items() 
                                if cb.isChecked() and len(self.character_paths.get(char, [])) > 0])
            if not char_pool:
                char_pool = string.ascii_letters + string.digits
                logger.warning("No character pool, using alphanumeric")
        
        length = np.random.randint(self.min_random_chars.value(), self.max_random_chars.value() + 1)
        return ''.join(random.choice(char_pool) for _ in range(length))
    
    def reset_transform(self):
        """Reset rotation and scaling of text item"""
        if self.text_item and self.original_pixmap:
            logger.info("Resetting transform...")
            
            current_pos = self.text_item.pos()
            was_selected = self.text_item.isSelected()
            
            self.graphics_scene.removeItem(self.text_item)
            
            self.text_item = ResizableRotatableTextItem(self.original_pixmap)
            self.text_item.setPos(current_pos)
            self.text_item.setRotation(0)
            self.text_item.setSelected(was_selected)
            self.graphics_scene.addItem(self.text_item)
            
            self.text_perspective_slider.setValue(0)
            
            logger.success("Transform reset")
        else:
            logger.warning("No text to reset")
    
    def on_custom_text_changed(self, text):
        if text.strip():
            logger.info(f"Character pool: '{text}'")
    
    def render_character_with_cv2(self, char):
        char_dim = self.char_dimension.value()
        img = np.zeros((char_dim, char_dim), dtype=np.uint8)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = self.font_scale.value()
        thickness = max(2, int(font_scale * 2))
        
        (text_width, text_height), baseline = cv2.getTextSize(char, font, font_scale, thickness)
        
        x = (char_dim - text_width) // 2
        y = (char_dim + text_height) // 2
        
        cv2.putText(img, char, (x, y), font, font_scale, 255, thickness, cv2.LINE_AA)
        
        return img
    
    def toggle_color_controls(self, enabled):
        self.min_r.setEnabled(enabled)
        self.max_r.setEnabled(enabled)
        self.min_g.setEnabled(enabled)
        self.max_g.setEnabled(enabled)
        self.min_b.setEnabled(enabled)
        self.max_b.setEnabled(enabled)
    
    def apply_texture(self, gray_img):
        """Apply texture from selected region or random texture"""
        # If No Texture is selected, use original colors
        if self.no_texture_radio.isChecked():
            return self.apply_random_color(gray_img)
        
        # Use picked texture region if available
        if self.selected_texture_region is not None:
            texture = self.selected_texture_region
        elif self.texture_paths:
            texture_path = random.choice(self.texture_paths)
            texture = cv2.imread(str(texture_path), cv2.IMREAD_COLOR)
            if texture is None:
                return self.apply_random_color(gray_img)
        else:
            return self.apply_random_color(gray_img)
        
        h, w = gray_img.shape
        texture_resized = cv2.resize(texture, (w, h), interpolation=cv2.INTER_LINEAR)
        mask = gray_img.astype(np.float32) / 255.0
        
        textured = np.zeros((h, w, 3), dtype=np.uint8)
        for c in range(3):
            textured[:, :, c] = (texture_resized[:, :, c] * mask).astype(np.uint8)
        
        return textured
    
    def apply_random_color(self, gray_img):
        if not self.enable_color_checkbox.isChecked():
            return cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
        
        r = np.random.randint(self.min_r.value(), self.max_r.value() + 1)
        g = np.random.randint(self.min_g.value(), self.max_g.value() + 1)
        b = np.random.randint(self.min_b.value(), self.max_b.value() + 1)
        
        h, w = gray_img.shape
        colored = np.zeros((h, w, 3), dtype=np.uint8)
        normalized = gray_img.astype(np.float32) / 255.0
        
        colored[:, :, 2] = (normalized * r).astype(np.uint8)
        colored[:, :, 1] = (normalized * g).astype(np.uint8)
        colored[:, :, 0] = (normalized * b).astype(np.uint8)
        
        return colored
    
    def apply_text_perspective(self):
        angle = self.text_perspective_slider.value()
        self.text_perspective_label.setText(f"{angle}°")
        self.current_perspective_angle = angle
        
        if self.text_item and self.current_composite is not None:
            transformed = self.apply_perspective_to_image(self.current_composite, angle)
            
            old_pos = self.text_item.pos()
            old_rotation = self.text_item.rotation()
            was_selected = self.text_item.isSelected()
            
            self.graphics_scene.removeItem(self.text_item)
            
            text_rgba = self.color_to_rgba_transparent(transformed)
            
            text_qimg = self.cv2_to_qimage(text_rgba)
            text_pixmap = QPixmap.fromImage(text_qimg)
            self.text_item = ResizableRotatableTextItem(text_pixmap)
            
            self.text_item.setPos(old_pos)
            self.text_item.setRotation(old_rotation)
            self.text_item.setSelected(was_selected)
            self.graphics_scene.addItem(self.text_item)
            
            logger.info(f"Perspective: {angle}°")
    
    def apply_perspective_to_image(self, img, angle):
        if angle == 0:
            return img
        
        h, w = img.shape[:2]
        shift = int(w * 0.3 * np.sin(np.radians(abs(angle))))
        
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        
        if angle > 0:
            dst = np.float32([[shift, 0], [w, 0], [w-shift, h], [0, h]])
        else:
            dst = np.float32([[0, 0], [w-shift, 0], [w, h], [shift, h]])
        
        M = cv2.getPerspectiveTransform(src, dst)
        
        return cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    
    def select_dataset(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Dataset Folder")
        if folder:
            self.dataset_root = Path(folder)
            self.dataset_label.setText(f"{self.dataset_root.name}")
            self.scan_dataset()
    
    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir = Path(folder)
            self.output_label.setText(f"{self.output_dir.name}")
    
    def select_backgrounds(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Background Folder")
        if folder:
            self.background_dir = Path(folder)
            self.scan_backgrounds()
    
    def select_textures(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Texture Folder")
        if folder:
            self.texture_dir = Path(folder)
            self.scan_textures()
    
    def scan_backgrounds(self):
        if not self.background_dir.exists():
            return
        
        self.background_paths = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.bmp']:
            self.background_paths.extend(list(self.background_dir.glob(ext)))
        
        self.bg_label.setText(f"{len(self.background_paths)} backgrounds")
        logger.info(f"Found {len(self.background_paths)} backgrounds")
    
    def scan_textures(self):
        if not self.texture_dir.exists():
            logger.warning(f"Texture folder not found: {self.texture_dir}")
            return
        
        self.texture_paths = []
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.bmp']:
            self.texture_paths.extend(list(self.texture_dir.glob(ext)))
        
        self.texture_label.setText(f"{self.texture_dir.name} ({len(self.texture_paths)})")
        logger.info(f"Found {len(self.texture_paths)} textures")
    
    def scan_dataset(self):
        if not self.dataset_root.exists():
            logger.error("Dataset not found!")
            return
        
        for cb in self.character_checkboxes.values():
            self.characters_layout.removeWidget(cb)
            cb.deleteLater()
        self.character_checkboxes.clear()
        self.character_paths.clear()
        
        subfolders = [f for f in self.dataset_root.iterdir() if f.is_dir()]
        total = 0
        
        for folder in sorted(subfolders):
            char_name = folder.name
            self.character_paths[char_name] = []
            
            for ext in ['*.png', '*.jpg', '*.jpeg']:
                self.character_paths[char_name].extend(list(folder.glob(ext)))
            
            total += len(self.character_paths[char_name])
            
            cb = QCheckBox(f"{char_name} ({len(self.character_paths[char_name])})")
            cb.setChecked(True)
            self.character_checkboxes[char_name] = cb
            self.characters_layout.addWidget(cb)
        
        self.characters_layout.addStretch()
        
        logger.success(f"Loaded {total} images from {len(self.character_paths)} characters")
    
    def load_and_process_image(self, path):
        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if img is None:
            return None
        
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                b, g, r, alpha = cv2.split(img)
                gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)
                mask = alpha > 0
                inverted = 255 - gray
                result = np.where(mask, inverted, 0).astype(np.uint8)
            elif img.shape[2] == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                result = 255 - gray
        else:
            result = 255 - img
        
        return result
    
    def apply_rotation(self, img, angle):
        h, w = img.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        new_w = int(h * sin + w * cos)
        new_h = int(h * cos + w * sin)
        M[0, 2] += (new_w / 2) - center[0]
        M[1, 2] += (new_h / 2) - center[1]
        
        if len(img.shape) == 2:
            return cv2.warpAffine(img, M, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        else:
            return cv2.warpAffine(img, M, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    
    def apply_perspective(self, img, angle):
        h, w = img.shape[:2]
        shift = int(w * np.tan(np.radians(angle)))
        direction = np.random.choice(['left', 'right', 'top', 'bottom'])
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        
        if direction == 'left':
            dst = np.float32([[shift, 0], [w, 0], [w, h], [0, h]])
        elif direction == 'right':
            dst = np.float32([[0, 0], [w-shift, 0], [w, h], [shift, h]])
        elif direction == 'top':
            dst = np.float32([[0, shift], [w, 0], [w, h], [0, h-shift]])
        else:
            dst = np.float32([[0, 0], [w, shift], [w, h-shift], [0, h]])
        
        M = cv2.getPerspectiveTransform(src, dst)
        
        if len(img.shape) == 2:
            return cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        else:
            return cv2.warpPerspective(img, M, (w, h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    
    def resize_with_aspect_ratio(self, img, target_size, pad_value=0):
        h, w = img.shape[:2]
        target_w, target_h = target_size
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        if len(img.shape) == 2:
            canvas = np.full((target_h, target_w), pad_value, dtype=np.uint8)
        else:
            canvas = np.full((target_h, target_w, img.shape[2]), pad_value, dtype=np.uint8)
        
        y_offset = (target_h - new_h) // 2
        x_offset = (target_w - new_w) // 2
        canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
        return canvas
    
    def crop_resize_pad_char(self, img):
        char_dim = self.char_dimension.value()
        
        coords = cv2.findNonZero(img)
        if coords is None:
            return np.zeros((char_dim, char_dim, 3), dtype=np.uint8)
        
        x, y, w, h = cv2.boundingRect(coords)
        cropped = img[y:y+h, x:x+w]
        
        if self.min_rotation.value() != 0 or self.max_rotation.value() != 0:
            angle = np.random.uniform(self.min_rotation.value(), self.max_rotation.value())
            cropped = self.apply_rotation(cropped, angle)
        
        if self.max_perspective.value() > 0:
            angle = np.random.uniform(self.min_perspective.value(), self.max_perspective.value())
            cropped = self.apply_perspective(cropped, angle)
        
        if self.texture_per_char_radio.isChecked():
            cropped = self.apply_texture(cropped)
        else:
            cropped = self.apply_random_color(cropped)
        
        if len(cropped.shape) == 2:
            cropped = cv2.cvtColor(cropped, cv2.COLOR_GRAY2BGR)
        
        scale = np.random.uniform(self.min_resize_scale.value(), self.max_resize_scale.value())
        new_w = max(1, int(cropped.shape[1] * scale))
        new_h = max(1, int(cropped.shape[0] * scale))
        resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return self.resize_with_aspect_ratio(resized, (char_dim, char_dim), pad_value=0)
    
    def color_to_rgba_transparent(self, color_img):
        h, w = color_img.shape[:2]
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        rgba[:, :, :3] = color_img
        rgba[:, :, 3] = np.max(color_img, axis=2)
        return rgba
    
    def cv2_to_qimage(self, cv_img):
        if len(cv_img.shape) == 2:
            h, w = cv_img.shape
            return QImage(cv_img.data, w, h, w, QImage.Format_Grayscale8)
        elif cv_img.shape[2] == 3:
            h, w, ch = cv_img.shape
            return QImage(cv_img.data, w, h, ch * w, QImage.Format_RGB888)
        elif cv_img.shape[2] == 4:
            h, w, ch = cv_img.shape
            return QImage(cv_img.data, w, h, ch * w, QImage.Format_RGBA8888)
    
    def qimage_to_numpy(self, qimg):
        qimg = qimg.convertToFormat(QImage.Format_RGB888)
        width = qimg.width()
        height = qimg.height()
        bytes_per_line = qimg.bytesPerLine()
        ptr = qimg.constBits()
        arr = np.array(ptr).reshape(height, bytes_per_line)
        arr = arr[:, :width * 3].reshape(height, width, 3)
        return arr.copy()
    
    def generate_text(self):
        """Generate text"""
        char_dim = self.char_dimension.value()
        
        if self.randomize_text_checkbox.isChecked():
            custom_text = self.generate_random_text()
            logger.info(f"Random from pool: '{custom_text}'")
        else:
            custom_text = self.custom_text_input.text().strip()
        
        if custom_text:
            images = []
            labels = []
            
            for char in custom_text:
                if char in self.character_paths and len(self.character_paths[char]) > 0:
                    path = random.choice(self.character_paths[char])
                    char_img = self.load_and_process_image(path)
                else:
                    char_img = self.render_character_with_cv2(char)
                
                if char_img is not None:
                    aug = self.crop_resize_pad_char(char_img)
                    if aug is not None:
                        images.append(aug)
                        labels.append(char)
            
            self.current_number = custom_text
            
        else:
            available = [char for char, cb in self.character_checkboxes.items() 
                        if cb.isChecked() and len(self.character_paths.get(char, [])) > 0]
            
            if not available:
                logger.warning("No characters selected!")
                return
            
            if self.text_item:
                self.last_text_position = self.text_item.pos()
                self.last_text_rotation = self.text_item.rotation()
            
            required = np.random.randint(self.min_chars.value(), self.max_chars.value() + 1)
            
            images = []
            labels = []
            attempts = 0
            
            while len(images) < required and attempts < required * 10:
                attempts += 1
                char = random.choice(available)
                paths = self.character_paths[char]
                
                if paths:
                    path = random.choice(paths)
                    img = self.load_and_process_image(path)
                    
                    if img is not None and img.size > 0:
                        aug = self.crop_resize_pad_char(img)
                        if aug is not None:
                            images.append(aug)
                            labels.append(char)
            
            self.current_number = "".join(labels)
        
        if len(images) > 0:
            canvas_height = self.canvas_height.value()
            strips = []
            
            for i, img in enumerate(images):
                if len(img.shape) == 2:
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                
                v_offset = np.random.randint(-self.max_v_offset.value(), self.max_v_offset.value() + 1)
                y_pos = max(0, min(canvas_height // 2 - char_dim // 2 + v_offset, canvas_height - char_dim))
                
                strip = np.zeros((canvas_height, char_dim, 3), dtype=np.uint8)
                strip[y_pos:y_pos+char_dim] = img
                strips.append(strip)
                
                if i < len(images) - 1:
                    margin = np.random.randint(self.min_h_margin.value(), self.max_h_margin.value() + 1)
                    strips.append(np.zeros((canvas_height, margin, 3), dtype=np.uint8))
            
            self.current_composite = np.hstack(strips)
            
            if self.texture_whole_text_radio.isChecked():
                if self.selected_texture_region is not None:
                    texture = self.selected_texture_region
                elif self.texture_paths:
                    texture_path = random.choice(self.texture_paths)
                    texture = cv2.imread(str(texture_path), cv2.IMREAD_COLOR)
                else:
                    texture = None
                
                if texture is not None:
                    h, w = self.current_composite.shape[:2]
                    texture_resized = cv2.resize(texture, (w, h), interpolation=cv2.INTER_LINEAR)
                    mask = np.max(self.current_composite, axis=2).astype(np.float32) / 255.0
                    
                    for c in range(3):
                        self.current_composite[:, :, c] = (texture_resized[:, :, c] * mask).astype(np.uint8)
                    
                    logger.info("Applied texture to whole text")
            
            if self.current_perspective_angle != 0:
                self.current_composite = self.apply_perspective_to_image(self.current_composite, self.current_perspective_angle)
            
            if self.text_item:
                self.graphics_scene.removeItem(self.text_item)
            
            text_rgba = self.color_to_rgba_transparent(self.current_composite)
            
            text_qimg = self.cv2_to_qimage(text_rgba)
            text_pixmap = QPixmap.fromImage(text_qimg)
            
            self.original_pixmap = text_pixmap.copy()
            
            self.text_item = ResizableRotatableTextItem(text_pixmap)
            
            if self.last_text_position:
                self.text_item.setPos(self.last_text_position)
            else:
                viewport_rect = self.graphics_view.viewport().rect()
                visible_scene_rect = self.graphics_view.mapToScene(viewport_rect).boundingRect()
                center_x = visible_scene_rect.center().x() - self.current_composite.shape[1] / 2
                center_y = visible_scene_rect.center().y() - self.current_composite.shape[0] / 2
                self.text_item.setPos(center_x, center_y)
                self.last_text_position = self.text_item.pos()
            
            self.text_item.setRotation(self.last_text_rotation)
            self.text_item.setSelected(True)
            self.graphics_scene.addItem(self.text_item)
            
            # Update text display
            self.update_generated_text_display()
            
            if not self.background_item:
                self.graphics_view.fitInView(self.graphics_scene.sceneRect(), Qt.KeepAspectRatio)
            
            mode = "random" if self.randomize_text_checkbox.isChecked() else ("custom" if custom_text else "characters")
            texture_info = "no texture" if self.no_texture_radio.isChecked() else "with texture"
            logger.success(f"Generated ({mode}, {char_dim}px, {texture_info}): {self.current_number}")
            self.save_btn.setEnabled(True)
        else:
            logger.error("Failed to generate")
    
    def load_random_background(self):
        """Load random background image"""
        if not self.background_paths:
            logger.warning("No backgrounds available!")
            return
        
        bg_path = random.choice(self.background_paths)
        bg = cv2.imread(str(bg_path), cv2.IMREAD_COLOR)
        
        if bg is None:
            logger.error(f"Failed to load background: {bg_path.name}")
            return
        
        self.current_background = bg
        bg_rgb = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
        
        # Remove old background if exists
        if self.background_item:
            self.graphics_scene.removeItem(self.background_item)
            self.background_item = None
        
        bg_qimg = self.cv2_to_qimage(bg_rgb)
        bg_pixmap = QPixmap.fromImage(bg_qimg)
        self.background_item = self.graphics_scene.addPixmap(bg_pixmap)
        self.background_item.setZValue(0)  # Bottommost layer
        self.background_item.setPos(0, 0)
        
        # Update scene rect
        self.graphics_scene.setSceneRect(self.background_item.boundingRect())
        
        # Fit view to show the background
        self.graphics_view.fitInView(self.background_item, Qt.KeepAspectRatio)
        
        # Force scene update
        self.graphics_scene.update()
        self.graphics_view.viewport().update()
        
        logger.success(f"Background loaded: {bg_path.name} [{bg.shape[1]}x{bg.shape[0]}]")
    
    def save_image(self):
        if self.current_composite is None:
            return
        
        if not self.output_dir.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.text_item:
            was_selected = self.text_item.isSelected()
            self.text_item.setSelected(False)
        
        if self.crop_to_text_checkbox.isChecked() and self.text_item:
            render_rect = self.text_item.sceneBoundingRect()
        else:
            render_rect = self.graphics_scene.sceneRect()
        
        render_img = QImage(int(render_rect.width()), int(render_rect.height()), QImage.Format_RGB888)
        render_img.fill(Qt.white)
        
        painter = QPainter(render_img)
        self.graphics_scene.render(painter, QRectF(render_img.rect()), render_rect)
        painter.end()
        
        if self.text_item and was_selected:
            self.text_item.setSelected(True)
        
        arr = self.qimage_to_numpy(render_img)
        cv_img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        
        safe_filename = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in self.current_number)
        base = f"{safe_filename}.png"
        filepath = self.output_dir / base
        
        if filepath.exists():
            suffix = np.random.randint(1000, 9999)
            filepath = self.output_dir / f"{safe_filename}_{suffix}.png"
        
        success = cv2.imwrite(str(filepath), cv_img)
        
        if success:
            logger.success(f"Saved: {filepath.name} [{cv_img.shape[1]}x{cv_img.shape[0]}]")
        else:
            logger.error("Save failed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=r''C:\Users\Viper\Desktop\text_baker\assets\dataset'')
    parser.add_argument("--output", default=r''C:\Users\Viper\Desktop\text_baker\assets\output'')
    parser.add_argument("--backgrounds", default=r'C:\Users\Viper\Pictures')
    parser.add_argument("--textures", default=r'C:\Users\Viper\Pictures')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    window = DatasetMaker(args.dataset, args.output, args.backgrounds, args.textures)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
