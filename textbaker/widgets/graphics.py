"""
Graphics widgets for TextBaker.

Contains custom Qt graphics items and views for the main canvas.
"""

import numpy as np
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsPixmapItem, QGraphicsEllipseItem,
    QGraphicsRectItem, QGraphicsItem
)
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QWheelEvent, QPainter, QPen, QColor, QBrush, QCursor, QPainterPath
)
from loguru import logger


class ResizableRotatableTextItem(QGraphicsPixmapItem):
    """Text overlay with rotation handle, resize handles, and dotted border."""
    
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
        
        # State variables
        self.dragging_handle = False
        self.dragging_resize = False
        self.resize_handle_index = -1
        self.initial_angle = 0
        self.initial_rotation = 0
        self.initial_pixmap = None
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
        """Get index of resize handle at position."""
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
        
        # Check resize handles
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
        
        # Check rotation handle
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
        """Update handle positions after resize."""
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
    """Custom graphics view with zoom and pan capabilities."""
    
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
        """Handle mouse wheel for zooming."""
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
        """Handle key press for panning mode."""
        if event.key() == Qt.Key_Space and not self.panning:
            self.panning = True
            self.viewport().setCursor(QCursor(Qt.OpenHandCursor))
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        """Handle key release to exit panning mode."""
        if event.key() == Qt.Key_Space:
            self.panning = False
            self.viewport().setCursor(QCursor(Qt.ArrowCursor))
        super().keyReleaseEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press for panning."""
        if self.panning and event.button() == Qt.LeftButton:
            self.pan_start = event.pos()
            self.viewport().setCursor(QCursor(Qt.ClosedHandCursor))
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for panning."""
        if self.panning:
            delta = event.pos() - self.pan_start
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.pan_start = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release for panning."""
        if self.panning:
            self.viewport().setCursor(QCursor(Qt.OpenHandCursor))
            event.accept()
        else:
            super().mouseReleaseEvent(event)
