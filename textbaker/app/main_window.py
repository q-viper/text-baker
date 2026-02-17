"""
Main window for TextBaker application.

This is the main GUI application for generating synthetic text datasets for OCR training.
"""

import string
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import cv2
import numpy as np
from loguru import logger
from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QDockWidget,
    QDoubleSpinBox,
    QFileDialog,
    QGraphicsScene,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from textbaker.core.image_processing import ImageProcessor
from textbaker.utils.helpers import sanitize_filename
from textbaker.utils.logging import LogHandler
from textbaker.utils.random_state import rng
from textbaker.widgets.dialogs import HintsDialog, TexturePickerDialog
from textbaker.widgets.drawing_canvas import DrawingCanvas
from textbaker.widgets.graphics import (
    InteractiveGraphicsView,
    ResizableRotatableTextItem,
)

if TYPE_CHECKING:
    from textbaker.core.configs import GeneratorConfig


class DatasetMaker(QMainWindow):
    """
    Main window for the Synthetic Text Dataset Generator.

    This application allows users to generate synthetic text images for OCR training
    by combining character images with backgrounds and applying various transformations.
    """

    def __init__(
        self,
        dataset_root: Optional[str] = None,
        output_dir: Optional[str] = None,
        background_dir: Optional[str] = None,
        texture_dir: Optional[str] = None,
        config: Optional["GeneratorConfig"] = None,
    ):
        super().__init__()
        self.setWindowTitle("TextBaker - Synthetic Text Dataset Generator")
        self.resize(1600, 900)

        # Set window icon
        icon_path = Path(__file__).parent.parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Paths - use config if provided, otherwise use arguments
        if config:
            self.dataset_root = Path(config.dataset.dataset_dir)
            self.output_dir = Path(config.output.output_dir)
            self.background_dir = (
                Path(config.background.background_dir)
                if config.background.background_dir
                else Path("")
            )
            self.texture_dir = (
                Path(config.texture.texture_dir) if config.texture.texture_dir else Path("")
            )
        else:
            self.dataset_root = Path(dataset_root) if dataset_root else Path("")
            self.output_dir = Path(output_dir) if output_dir else Path("")
            self.background_dir = Path(background_dir) if background_dir else Path("")
            self.texture_dir = Path(texture_dir) if texture_dir else Path("")

        # Custom characters directory in current working directory
        self.custom_char_dir = Path.cwd() / ".textbaker" / "custom_characters"
        self.custom_char_dir.mkdir(parents=True, exist_ok=True)

        # Data storage
        self.character_paths: dict[str, list[Path]] = {}
        self.background_paths: list[Path] = []
        self.texture_paths: list[Path] = []
        self.character_checkboxes: dict[str, QCheckBox] = {}

        # State
        self.current_composite: Optional[np.ndarray] = None
        self.current_background: Optional[np.ndarray] = None
        self.text_item: Optional[ResizableRotatableTextItem] = None
        self.background_item = None
        self.last_text_position = None
        self.last_text_rotation = 0
        self.last_text_scale = 1.0
        self.last_text_size = None  # Store (width, height) of last text item
        self.current_perspective_angle = 0
        self.current_number = ""
        self.original_pixmap = None
        self.selected_texture_region: Optional[np.ndarray] = None

        # Image processor
        self.image_processor = ImageProcessor()

        # Setup log handler
        self.log_handler = LogHandler()
        logger.add(self.log_handler.write, format="{time:HH:mm:ss} | {level} | {message}")

        self._init_ui()

        # Apply config if provided
        if config:
            self._apply_config(config)

        # Scan directories if they exist
        if self.dataset_root.exists():
            self.scan_dataset()
        if self.background_dir.exists():
            self.scan_backgrounds()
        if self.texture_dir.exists():
            self.scan_textures()

        QTimer.singleShot(100, self._auto_start)

    def _apply_config(self, config: "GeneratorConfig"):
        """Apply configuration to UI widgets.

        Args:
            config: GeneratorConfig instance to apply
        """

        logger.info("Applying configuration to UI...")

        # Character settings
        self.char_dimension.setValue(config.character.width)

        # Text length
        self.min_chars.setValue(config.text_length[0])
        self.max_chars.setValue(config.text_length[1])

        # Spacing (horizontal margin)
        self.min_h_margin.setValue(config.spacing)
        self.max_h_margin.setValue(config.spacing)

        # Canvas and layout
        self.canvas_height.setValue(config.canvas_height)
        self.max_v_offset.setValue(config.max_v_offset)
        self.font_scale.setValue(config.font_scale)

        # Transform settings
        self.min_rotation.setValue(int(config.transform.rotation_range[0]))
        self.max_rotation.setValue(int(config.transform.rotation_range[1]))
        self.min_perspective.setValue(int(config.transform.perspective_range[0]))
        self.max_perspective.setValue(int(config.transform.perspective_range[1]))
        self.min_resize_scale.setValue(config.transform.scale_range[0])
        self.max_resize_scale.setValue(config.transform.scale_range[1])

        # Color settings
        self.enable_color_checkbox.setChecked(config.color.random_color)
        self.min_r.setValue(config.color.color_range_r[0])
        self.max_r.setValue(config.color.color_range_r[1])
        self.min_g.setValue(config.color.color_range_g[0])
        self.max_g.setValue(config.color.color_range_g[1])
        self.min_b.setValue(config.color.color_range_b[0])
        self.max_b.setValue(config.color.color_range_b[1])

        # Texture settings
        if config.texture.enabled:
            if config.texture.per_character:
                self.texture_per_char_radio.setChecked(True)
            else:
                self.texture_whole_text_radio.setChecked(True)
        else:
            self.no_texture_radio.setChecked(True)

        # Output settings
        self.crop_to_text_checkbox.setChecked(config.output.crop_to_text)

        logger.success("Configuration applied successfully")

    def _auto_start(self):
        """Auto-start with random background and text if available."""
        if (
            self.background_paths
            and len([cb for cb in self.character_checkboxes.values() if cb.isChecked()]) > 0
        ):
            logger.info("Auto-starting...")
            self.load_random_background()
            QTimer.singleShot(50, self.generate_text)

    def show_hints(self):
        """Show the hints dialog."""
        dialog = HintsDialog(self)
        dialog.exec()

    def append_log(self, message: str):
        """Append message to log display."""
        self.log_display.append(message)
        scrollbar = self.log_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _create_scroll_widget(self, widget: QWidget) -> QScrollArea:
        """Wrap a widget in a scroll area."""
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        return scroll

    def open_texture_picker(self):
        """Open texture picker dialog."""
        if not self.texture_paths and not self.background_paths:
            QMessageBox.warning(self, "No Images", "No texture or background images available!")
            return

        dialog = TexturePickerDialog(self.texture_paths, self.background_paths, self)
        if dialog.exec() == QDialog.Accepted:
            self.selected_texture_region = dialog.get_selected_texture()
            self.image_processor.selected_texture_region = self.selected_texture_region
            if self.selected_texture_region is not None:
                logger.success(f"Texture region selected: {self.selected_texture_region.shape}")
            else:
                logger.warning("No texture region selected")

    def _init_ui(self):
        """Initialize the user interface."""
        # Central widget - Graphics View
        self.graphics_view = InteractiveGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        self.setCentralWidget(self.graphics_view)

        self._init_left_dock()
        self._init_right_dock()
        self._init_bottom_dock()

        # Connect log handler
        self.log_handler.log_signal.connect(self.append_log)

        logger.info("TextBaker ready - drag to select texture regions!")

    def _init_left_dock(self):
        """Initialize left dock with input settings."""
        left_dock = QDockWidget("Input Settings", self)
        left_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Folders group
        folder_group = QGroupBox("📁 Folders")
        folder_layout = QVBoxLayout()

        dataset_btn = QPushButton("Dataset Folder")
        dataset_btn.clicked.connect(self.select_dataset)
        folder_layout.addWidget(dataset_btn)
        self.dataset_label = QLabel(
            f"{self.dataset_root.name if self.dataset_root.exists() else 'None'}"
        )
        self.dataset_label.setWordWrap(True)
        folder_layout.addWidget(self.dataset_label)

        output_btn = QPushButton("Output Folder")
        output_btn.clicked.connect(self.select_output)
        folder_layout.addWidget(output_btn)
        self.output_label = QLabel(
            f"{self.output_dir.name if self.output_dir.exists() else 'None'}"
        )
        self.output_label.setWordWrap(True)
        folder_layout.addWidget(self.output_label)

        bg_btn = QPushButton("Background Folder")
        bg_btn.clicked.connect(self.select_backgrounds)
        folder_layout.addWidget(bg_btn)
        self.bg_label = QLabel("0 backgrounds")
        folder_layout.addWidget(self.bg_label)

        texture_btn = QPushButton("Texture Folder")
        texture_btn.clicked.connect(self.select_textures)
        folder_layout.addWidget(texture_btn)
        self.texture_label = QLabel(
            f"{self.texture_dir.name if self.texture_dir.exists() else 'None'}"
        )
        self.texture_label.setWordWrap(True)
        folder_layout.addWidget(self.texture_label)

        folder_group.setLayout(folder_layout)
        left_layout.addWidget(folder_group)

        # Texture Mode group
        texture_mode_group = QGroupBox("🎨 Texture Application")
        texture_mode_layout = QVBoxLayout()

        self.texture_button_group = QButtonGroup()

        self.no_texture_radio = QRadioButton("No Texture (use original colors)")
        self.no_texture_radio.setChecked(True)
        self.texture_per_char_radio = QRadioButton("Per Character")
        self.texture_whole_text_radio = QRadioButton("Whole Text")

        self.texture_button_group.addButton(self.no_texture_radio)
        self.texture_button_group.addButton(self.texture_per_char_radio)
        self.texture_button_group.addButton(self.texture_whole_text_radio)

        texture_mode_layout.addWidget(self.no_texture_radio)
        texture_mode_layout.addWidget(self.texture_per_char_radio)
        texture_mode_layout.addWidget(self.texture_whole_text_radio)

        pick_texture_btn = QPushButton("🎨 Pick Texture Region")
        pick_texture_btn.clicked.connect(self.open_texture_picker)
        pick_texture_btn.setStyleSheet("""
            QPushButton { background: #673AB7; color: white; padding: 8px; font-weight: bold; }
            QPushButton:hover { background: #5E35B1; color: white; }
        """)
        texture_mode_layout.addWidget(pick_texture_btn)

        texture_mode_group.setLayout(texture_mode_layout)
        left_layout.addWidget(texture_mode_group)

        # Draw Character button (above Custom Text group)
        draw_btn = QPushButton("✏️ Draw Character")
        draw_btn.setToolTip("Draw a custom character")
        draw_btn.clicked.connect(self.open_drawing_canvas)
        draw_btn.setStyleSheet("""
            QPushButton {
                background: #9C27B0;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7B1FA2;
            }
        """)
        left_layout.addWidget(draw_btn)

        # Custom Text group
        text_group = QGroupBox("📝 Custom Text")
        text_layout = QVBoxLayout()

        text_layout.addWidget(QLabel("Character Pool:"))
        self.custom_text_input = QLineEdit()
        self.custom_text_input.setPlaceholderText("e.g., ABC123 (chars to use)")
        self.custom_text_input.textChanged.connect(self._on_custom_text_changed)
        text_layout.addWidget(self.custom_text_input)

        self.randomize_text_checkbox = QCheckBox("Randomize from pool")
        self.randomize_text_checkbox.setChecked(False)
        self.randomize_text_checkbox.toggled.connect(self._toggle_randomize_controls)
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

        # Character Selection group
        char_group = QGroupBox("🔤 Character Selection")
        char_layout = QVBoxLayout()

        self.characters_widget = QWidget()
        self.characters_layout = QVBoxLayout(self.characters_widget)

        char_scroll = QScrollArea()
        char_scroll.setWidget(self.characters_widget)
        char_scroll.setWidgetResizable(True)
        char_scroll.setMinimumHeight(200)

        char_layout.addWidget(char_scroll)
        char_group.setLayout(char_layout)
        left_layout.addWidget(char_group)

        # Crop to Text option
        self.crop_to_text_checkbox = QCheckBox("Crop to Text when saving")
        self.crop_to_text_checkbox.setChecked(True)
        left_layout.addWidget(self.crop_to_text_checkbox)

        left_layout.addStretch()
        left_dock.setWidget(self._create_scroll_widget(left_widget))
        self.addDockWidget(Qt.LeftDockWidgetArea, left_dock)

    def _init_right_dock(self):
        """Initialize right dock with generation parameters."""
        right_dock = QDockWidget("Generation Parameters", self)
        right_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Generation Parameters group
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

        # Character Count
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

        # Scale
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

        # Rotation
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

        # Perspective
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

        # Horizontal Margin
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

        # Canvas Height
        canvas_layout = QHBoxLayout()
        canvas_layout.addWidget(QLabel("Canvas H:"))
        self.canvas_height = QSpinBox()
        self.canvas_height.setRange(64, 256)
        self.canvas_height.setValue(128)
        canvas_layout.addWidget(self.canvas_height)
        num_layout.addLayout(canvas_layout)

        # Vertical Offset
        v_offset_layout = QHBoxLayout()
        v_offset_layout.addWidget(QLabel("V-Offset:"))
        self.max_v_offset = QSpinBox()
        self.max_v_offset.setRange(0, 64)
        self.max_v_offset.setValue(20)
        v_offset_layout.addWidget(self.max_v_offset)
        num_layout.addLayout(v_offset_layout)

        # Font Scale
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

        # Transform group
        transform_group = QGroupBox("🔄 Transform")
        transform_layout = QVBoxLayout()

        transform_layout.addWidget(QLabel("Text Perspective:"))
        persp_slider_layout = QHBoxLayout()
        self.text_perspective_slider = QSlider(Qt.Horizontal)
        self.text_perspective_slider.setRange(-45, 45)
        self.text_perspective_slider.setValue(0)
        self.text_perspective_slider.setTickPosition(QSlider.TicksBelow)
        self.text_perspective_slider.setTickInterval(15)
        self.text_perspective_slider.valueChanged.connect(self._apply_text_perspective)
        persp_slider_layout.addWidget(self.text_perspective_slider)
        self.text_perspective_label = QLabel("0°")
        self.text_perspective_label.setMinimumWidth(35)
        persp_slider_layout.addWidget(self.text_perspective_label)
        transform_layout.addLayout(persp_slider_layout)

        reset_transform_btn = QPushButton("🔄 Reset Transform")
        reset_transform_btn.clicked.connect(self._reset_transform)
        reset_transform_btn.setStyleSheet("""
            QPushButton { background: #607D8B; color: white; padding: 8px; font-weight: bold; }
            QPushButton:hover { background: #546E7A; color: white; }
        """)
        transform_layout.addWidget(reset_transform_btn)

        transform_group.setLayout(transform_layout)
        right_layout.addWidget(transform_group)

        # Color group
        color_group = QGroupBox("🎨 Color")
        color_layout = QVBoxLayout()

        self.enable_color_checkbox = QCheckBox("Enable Random Colors")
        self.enable_color_checkbox.setChecked(False)
        self.enable_color_checkbox.toggled.connect(self._toggle_color_controls)
        color_layout.addWidget(self.enable_color_checkbox)

        # RGB controls
        for color, (default_min, default_max) in [
            ("R", (100, 255)),
            ("G", (100, 255)),
            ("B", (100, 255)),
        ]:
            rgb_layout = QHBoxLayout()
            rgb_layout.addWidget(QLabel(f"{color}:"))
            min_spin = QSpinBox()
            min_spin.setRange(0, 255)
            min_spin.setValue(default_min)
            min_spin.setEnabled(False)
            rgb_layout.addWidget(min_spin)
            rgb_layout.addWidget(QLabel("-"))
            max_spin = QSpinBox()
            max_spin.setRange(0, 255)
            max_spin.setValue(default_max)
            max_spin.setEnabled(False)
            rgb_layout.addWidget(max_spin)
            color_layout.addLayout(rgb_layout)

            setattr(self, f"min_{color.lower()}", min_spin)
            setattr(self, f"max_{color.lower()}", max_spin)

        color_group.setLayout(color_layout)
        right_layout.addWidget(color_group)

        right_layout.addStretch()
        right_dock.setWidget(self._create_scroll_widget(right_widget))
        self.addDockWidget(Qt.RightDockWidgetArea, right_dock)

    def _init_bottom_dock(self):
        """Initialize bottom dock with actions and logs."""
        bottom_dock = QDockWidget("Actions & Logs", self)
        bottom_dock.setAllowedAreas(Qt.BottomDockWidgetArea)
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        # Action buttons
        action_layout = QHBoxLayout()

        generate_btn = QPushButton("🎲 Generate Random Text")
        generate_btn.clicked.connect(self.generate_text)
        generate_btn.setStyleSheet("""
            QPushButton { background: #4CAF50; color: white; font-size: 11px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background: #45a049; color: white; }
        """)
        action_layout.addWidget(generate_btn)

        load_bg_btn = QPushButton("🖼️ Select Random Background")
        load_bg_btn.clicked.connect(self.load_random_background)
        load_bg_btn.setStyleSheet("""
            QPushButton { background: #FF9800; color: white; font-size: 11px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background: #FB8C00; color: white; }
        """)
        action_layout.addWidget(load_bg_btn)

        self.save_btn = QPushButton("💾 Save Image")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton { background: #2196F3; color: white; font-size: 11px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background: #1E88E5; color: white; }
        """)
        action_layout.addWidget(self.save_btn)

        export_config_btn = QPushButton("📋 Export Config")
        export_config_btn.clicked.connect(self.export_config)
        export_config_btn.setStyleSheet("""
            QPushButton { background: #607D8B; color: white; font-size: 11px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background: #546E7A; color: white; }
        """)
        action_layout.addWidget(export_config_btn)

        hints_btn = QPushButton("❓")
        hints_btn.clicked.connect(self.show_hints)
        hints_btn.setStyleSheet("""
            QPushButton { background: #9C27B0; color: white; font-size: 11px; padding: 10px; font-weight: bold; }
            QPushButton:hover { background: #8E24AA; color: white; }
        """)
        action_layout.addWidget(hints_btn)

        bottom_layout.addLayout(action_layout)

        # Generated text display
        text_display_layout = QHBoxLayout()
        self.generated_text_label = QLabel(
            "Generated: <span style='background: #FFD700; color: #000; padding: 4px 8px; "
            "border-radius: 3px; font-weight: bold;'>None</span>"
        )
        self.generated_text_label.setTextFormat(Qt.RichText)
        text_display_layout.addWidget(self.generated_text_label)
        text_display_layout.addStretch()
        bottom_layout.addLayout(text_display_layout)

        # Logs
        log_label = QLabel("📋 Logs:")
        bottom_layout.addWidget(log_label)
        self.log_display = QTextBrowser()
        self.log_display.setMaximumHeight(60)
        self.log_display.setStyleSheet(
            "background: #1e1e1e; color: #00ff00; font-family: monospace; font-size: 10px;"
        )
        bottom_layout.addWidget(self.log_display)

        bottom_dock.setWidget(bottom_widget)
        self.addDockWidget(Qt.BottomDockWidgetArea, bottom_dock)

    def _update_generated_text_display(self):
        """Update the generated text display label."""
        text = self.current_number if self.current_number else "None"
        self.generated_text_label.setText(
            f"Generated: <span style='background: #FFD700; color: #000; padding: 4px 8px; "
            f"border-radius: 3px; font-weight: bold;'>{text}</span>"
        )

    def _toggle_randomize_controls(self, enabled: bool):
        """Enable/disable randomize character length controls."""
        self.min_random_chars.setEnabled(enabled)
        self.max_random_chars.setEnabled(enabled)
        logger.info("Random text generation enabled" if enabled else "Using exact custom text")

    def _generate_random_text(self) -> str:
        """Generate random text from custom text pool."""
        char_pool = self.custom_text_input.text().strip()
        if not char_pool:
            char_pool = "".join(
                [
                    char
                    for char, cb in self.character_checkboxes.items()
                    if cb.isChecked() and len(self.character_paths.get(char, [])) > 0
                ]
            )
            if not char_pool:
                char_pool = string.ascii_letters + string.digits
                logger.warning("No character pool, using alphanumeric")

        length = rng.randint(self.min_random_chars.value(), self.max_random_chars.value())
        return "".join(rng.choice(char_pool) for _ in range(length))

    def _reset_transform(self):
        """Reset rotation and scaling of text item."""
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

    def _on_custom_text_changed(self, text: str):
        """Handle custom text input changes."""
        if text.strip():
            logger.info(f"Character pool: '{text}'")

    def _toggle_color_controls(self, enabled: bool):
        """Enable/disable color controls."""
        for attr in ["min_r", "max_r", "min_g", "max_g", "min_b", "max_b"]:
            getattr(self, attr).setEnabled(enabled)

    def _apply_text_perspective(self):
        """Apply perspective transformation to text."""
        angle = self.text_perspective_slider.value()
        self.text_perspective_label.setText(f"{angle}°")
        self.current_perspective_angle = angle

        if self.text_item and self.current_composite is not None:
            transformed = self.image_processor.apply_perspective_to_image(
                self.current_composite, angle
            )

            old_pos = self.text_item.pos()
            old_rotation = self.text_item.rotation()
            was_selected = self.text_item.isSelected()

            self.graphics_scene.removeItem(self.text_item)

            text_rgba = self.image_processor.color_to_rgba_transparent(transformed)
            text_qimg = self._cv2_to_qimage(text_rgba)
            text_pixmap = QPixmap.fromImage(text_qimg)
            self.text_item = ResizableRotatableTextItem(text_pixmap)

            self.text_item.setPos(old_pos)
            self.text_item.setRotation(old_rotation)
            self.text_item.setSelected(was_selected)
            self.graphics_scene.addItem(self.text_item)

            logger.info(f"Perspective: {angle}°")

    # File selection methods
    def select_dataset(self):
        """Select dataset folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Dataset Folder")
        if folder:
            self.dataset_root = Path(folder)
            self.dataset_label.setText(f"{self.dataset_root.name}")
            self.scan_dataset()

    def select_output(self):
        """Select output folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_dir = Path(folder)
            self.output_label.setText(f"{self.output_dir.name}")

    def select_backgrounds(self):
        """Select background folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Background Folder")
        if folder:
            self.background_dir = Path(folder)
            self.scan_backgrounds()

    def select_textures(self):
        """Select texture folder."""
        folder = QFileDialog.getExistingDirectory(self, "Select Texture Folder")
        if folder:
            self.texture_dir = Path(folder)
            self.scan_textures()

    # Scanning methods
    def scan_backgrounds(self):
        """Scan background folder for images."""
        if not self.background_dir.exists():
            return

        self.background_paths = []
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.bmp"]:
            self.background_paths.extend(list(self.background_dir.glob(ext)))

        self.bg_label.setText(f"{len(self.background_paths)} backgrounds")
        logger.info(f"Found {len(self.background_paths)} backgrounds")

    def scan_textures(self):
        """Scan texture folder for images."""
        if not self.texture_dir.exists():
            logger.warning(f"Texture folder not found: {self.texture_dir}")
            return

        self.texture_paths = []
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.bmp"]:
            self.texture_paths.extend(list(self.texture_dir.glob(ext)))

        self.image_processor.texture_paths = self.texture_paths
        self.texture_label.setText(f"{self.texture_dir.name} ({len(self.texture_paths)})")
        logger.info(f"Found {len(self.texture_paths)} textures")

    def open_drawing_canvas(self):
        """Open the drawing canvas dialog."""
        dialog = DrawingCanvas(self, self.custom_char_dir)
        dialog.character_saved.connect(self._on_character_drawn)
        dialog.exec()

    def _on_character_drawn(self, character: str, image_path: str):
        """Handle newly drawn character."""
        logger.success(f"New character '{character}' saved to {image_path}")
        # Use incremental update instead of full rescan
        QTimer.singleShot(50, lambda: self._add_character_incremental(character, image_path))

    def _add_character_incremental(self, character: str, image_path: str):
        """Add a single character to the dataset without full rescan."""
        from pathlib import Path

        img_path = Path(image_path)

        # Add to character_paths
        if character not in self.character_paths:
            self.character_paths[character] = []

        if img_path not in self.character_paths[character]:
            self.character_paths[character].append(img_path)

        # Update or create checkbox
        if character in self.character_checkboxes:
            # Update existing checkbox with new count
            count = len(self.character_paths[character])
            self.character_checkboxes[character].setText(f"{character} ({count})")
        else:
            # Create new checkbox
            count = len(self.character_paths[character])
            cb = QCheckBox(f"{character} ({count})")
            cb.setChecked(True)
            self.character_checkboxes[character] = cb
            # Insert in sorted position
            inserted = False
            for i in range(self.characters_layout.count()):
                widget = self.characters_layout.itemAt(i).widget()
                if widget and hasattr(widget, "text") and widget.text().split()[0] > character:
                    self.characters_layout.insertWidget(i, cb)
                    inserted = True
                    break
            if not inserted:
                # Remove stretch if it exists, add checkbox, then re-add stretch
                last_item = self.characters_layout.itemAt(self.characters_layout.count() - 1)
                if last_item and last_item.spacerItem():
                    self.characters_layout.removeItem(last_item)
                self.characters_layout.addWidget(cb)
                self.characters_layout.addStretch()

        logger.info(
            f"Added character '{character}' to dataset (now {len(self.character_paths[character])} samples)"
        )

    def scan_dataset(self):
        """
        Scan dataset folder for character images recursively.

        Images are organized by their parent folder name as the character label.
        Supports nested folder structures - character name is taken from
        the immediate parent folder of each image file.
        Also scans custom characters from .textbaker directory.
        """
        if not self.dataset_root.exists():
            logger.error("Dataset not found!")
            return

        # Clear existing
        for cb in self.character_checkboxes.values():
            self.characters_layout.removeWidget(cb)
            cb.deleteLater()
        self.character_checkboxes.clear()
        self.character_paths.clear()

        # Recursively find all images, character is parent folder name
        image_extensions = {".png", ".jpg", ".jpeg"}
        total = 0

        # Scan main dataset
        for img_path in self.dataset_root.rglob("*"):
            if img_path.suffix.lower() in image_extensions and img_path.is_file():
                # Character name is the immediate parent folder
                char_name = img_path.parent.name

                if char_name not in self.character_paths:
                    self.character_paths[char_name] = []

                self.character_paths[char_name].append(img_path)
                total += 1

        # Scan custom characters directory
        if self.custom_char_dir.exists():
            for img_path in self.custom_char_dir.rglob("*"):
                if img_path.suffix.lower() in image_extensions and img_path.is_file():
                    char_name = img_path.parent.name

                    if char_name not in self.character_paths:
                        self.character_paths[char_name] = []

                    self.character_paths[char_name].append(img_path)
                    total += 1

        # Create checkboxes for each character
        for char_name in sorted(self.character_paths.keys()):
            count = len(self.character_paths[char_name])
            cb = QCheckBox(f"{char_name} ({count})")
            cb.setChecked(True)
            self.character_checkboxes[char_name] = cb
            self.characters_layout.addWidget(cb)

        self.characters_layout.addStretch()
        logger.success(f"Loaded {total} images from {len(self.character_paths)} characters")

    # Image conversion methods
    def _cv2_to_qimage(self, cv_img: np.ndarray) -> QImage:
        """Convert OpenCV image to QImage."""
        if len(cv_img.shape) == 2:
            h, w = cv_img.shape
            return QImage(cv_img.data, w, h, w, QImage.Format_Grayscale8)
        elif cv_img.shape[2] == 3:
            h, w, ch = cv_img.shape
            return QImage(cv_img.data, w, h, ch * w, QImage.Format_RGB888)
        elif cv_img.shape[2] == 4:
            h, w, ch = cv_img.shape
            return QImage(cv_img.data, w, h, ch * w, QImage.Format_RGBA8888)

    def _qimage_to_numpy(self, qimg: QImage) -> np.ndarray:
        """Convert QImage to numpy array."""
        qimg = qimg.convertToFormat(QImage.Format_RGB888)
        width = qimg.width()
        height = qimg.height()
        bytes_per_line = qimg.bytesPerLine()
        ptr = qimg.constBits()
        arr = np.array(ptr).reshape(height, bytes_per_line)
        arr = arr[:, : width * 3].reshape(height, width, 3)
        return arr.copy()

    def _get_color_range(self):
        """Get color range tuple if color is enabled."""
        if not self.enable_color_checkbox.isChecked():
            return None
        return (
            (self.min_r.value(), self.max_r.value()),
            (self.min_g.value(), self.max_g.value()),
            (self.min_b.value(), self.max_b.value()),
        )

    def generate_text(self):
        """Generate text composite image."""
        char_dim = self.char_dimension.value()

        # Save current text item state before generating new text
        if self.text_item:
            self.last_text_position = self.text_item.pos()
            self.last_text_rotation = self.text_item.rotation()
            # Save the current size of the text item
            self.last_text_size = (
                self.text_item.boundingRect().width(),
                self.text_item.boundingRect().height(),
            )

        if self.randomize_text_checkbox.isChecked():
            custom_text = self._generate_random_text()
            logger.info(f"Random from pool: '{custom_text}'")
        else:
            custom_text = self.custom_text_input.text().strip()

        images = []
        labels = []

        if custom_text:
            for char in custom_text:
                if char in self.character_paths and len(self.character_paths[char]) > 0:
                    path = rng.choice(self.character_paths[char])
                    char_img = self.image_processor.load_and_process_image(path)
                else:
                    char_img = self.image_processor.render_character_with_cv2(
                        char, char_dim, self.font_scale.value()
                    )

                if char_img is not None:
                    aug = self.image_processor.crop_resize_pad_char(
                        char_img,
                        char_dim,
                        rotation_range=(self.min_rotation.value(), self.max_rotation.value()),
                        perspective_range=(
                            self.min_perspective.value(),
                            self.max_perspective.value(),
                        ),
                        scale_range=(self.min_resize_scale.value(), self.max_resize_scale.value()),
                        apply_texture=self.texture_per_char_radio.isChecked(),
                        color_range=self._get_color_range(),
                    )
                    if aug is not None:
                        images.append(aug)
                        labels.append(char)

            self.current_number = custom_text
        else:
            available = [
                char
                for char, cb in self.character_checkboxes.items()
                if cb.isChecked() and len(self.character_paths.get(char, [])) > 0
            ]

            if not available:
                logger.warning("No characters selected!")
                return

            required = rng.randint(self.min_chars.value(), self.max_chars.value())
            attempts = 0

            while len(images) < required and attempts < required * 10:
                attempts += 1
                char = rng.choice(available)
                paths = self.character_paths[char]

                if paths:
                    path = rng.choice(paths)
                    img = self.image_processor.load_and_process_image(path)

                    if img is not None and img.size > 0:
                        aug = self.image_processor.crop_resize_pad_char(
                            img,
                            char_dim,
                            rotation_range=(self.min_rotation.value(), self.max_rotation.value()),
                            perspective_range=(
                                self.min_perspective.value(),
                                self.max_perspective.value(),
                            ),
                            scale_range=(
                                self.min_resize_scale.value(),
                                self.max_resize_scale.value(),
                            ),
                            apply_texture=self.texture_per_char_radio.isChecked(),
                            color_range=self._get_color_range(),
                        )
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

                v_offset = rng.randint(-self.max_v_offset.value(), self.max_v_offset.value())
                y_pos = max(
                    0, min(canvas_height // 2 - char_dim // 2 + v_offset, canvas_height - char_dim)
                )

                strip = np.zeros((canvas_height, char_dim, 3), dtype=np.uint8)
                strip[y_pos : y_pos + char_dim] = img
                strips.append(strip)

                if i < len(images) - 1:
                    margin = rng.randint(self.min_h_margin.value(), self.max_h_margin.value())
                    strips.append(np.zeros((canvas_height, margin, 3), dtype=np.uint8))

            self.current_composite = np.hstack(strips)

            # Apply whole-text texture if selected
            if self.texture_whole_text_radio.isChecked():
                texture = self.selected_texture_region
                if texture is None and self.texture_paths:
                    texture_path = rng.choice(self.texture_paths)
                    texture = cv2.imread(str(texture_path), cv2.IMREAD_COLOR)

                if texture is not None:
                    h, w = self.current_composite.shape[:2]
                    texture_resized = cv2.resize(texture, (w, h), interpolation=cv2.INTER_LINEAR)
                    mask = np.max(self.current_composite, axis=2).astype(np.float32) / 255.0

                    for c in range(3):
                        self.current_composite[:, :, c] = (texture_resized[:, :, c] * mask).astype(
                            np.uint8
                        )

                    logger.info("Applied texture to whole text")

            # Apply perspective
            if self.current_perspective_angle != 0:
                self.current_composite = self.image_processor.apply_perspective_to_image(
                    self.current_composite, self.current_perspective_angle
                )

            # Update graphics scene
            if self.text_item:
                self.graphics_scene.removeItem(self.text_item)

            text_rgba = self.image_processor.color_to_rgba_transparent(self.current_composite)
            text_qimg = self._cv2_to_qimage(text_rgba)
            text_pixmap = QPixmap.fromImage(text_qimg)

            self.original_pixmap = text_pixmap.copy()
            self.text_item = ResizableRotatableTextItem(text_pixmap)

            # Apply saved state (position, rotation, size)
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

            # Scale to match previous size if available
            if self.last_text_size:
                current_width = self.text_item.boundingRect().width()
                current_height = self.text_item.boundingRect().height()
                if current_width > 0 and current_height > 0:
                    target_width, target_height = self.last_text_size
                    scaled_pixmap = text_pixmap.scaled(
                        int(target_width),
                        int(target_height),
                        Qt.IgnoreAspectRatio,
                        Qt.SmoothTransformation,
                    )
                    self.text_item.setPixmap(scaled_pixmap)
                    self.text_item.update_handles()

            self.text_item.setSelected(True)
            self.graphics_scene.addItem(self.text_item)

            self._update_generated_text_display()

            if not self.background_item:
                self.graphics_view.fitInView(self.graphics_scene.sceneRect(), Qt.KeepAspectRatio)

            mode = (
                "random"
                if self.randomize_text_checkbox.isChecked()
                else ("custom" if custom_text else "characters")
            )
            texture_info = "no texture" if self.no_texture_radio.isChecked() else "with texture"
            logger.success(
                f"Generated ({mode}, {char_dim}px, {texture_info}): {self.current_number}"
            )
            self.save_btn.setEnabled(True)
        else:
            logger.error("Failed to generate")

    def load_random_background(self):
        """Load random background image."""
        if not self.background_paths:
            logger.warning("No backgrounds available!")
            return

        bg_path = rng.choice(self.background_paths)
        bg = cv2.imread(str(bg_path), cv2.IMREAD_COLOR)

        if bg is None:
            logger.error(f"Failed to load background: {bg_path.name}")
            return

        self.current_background = bg
        bg_rgb = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)

        if self.background_item:
            self.graphics_scene.removeItem(self.background_item)
            self.background_item = None

        bg_qimg = self._cv2_to_qimage(bg_rgb)
        bg_pixmap = QPixmap.fromImage(bg_qimg)
        self.background_item = self.graphics_scene.addPixmap(bg_pixmap)
        self.background_item.setZValue(0)
        self.background_item.setPos(0, 0)

        self.graphics_scene.setSceneRect(self.background_item.boundingRect())
        self.graphics_view.fitInView(self.background_item, Qt.KeepAspectRatio)

        self.graphics_scene.update()
        self.graphics_view.viewport().update()

        logger.success(f"Background loaded: {bg_path.name} [{bg.shape[1]}x{bg.shape[0]}]")

    def save_image(self):
        """Save the generated image."""
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

        render_img = QImage(
            int(render_rect.width()), int(render_rect.height()), QImage.Format_RGB888
        )
        render_img.fill(Qt.white)

        painter = QPainter(render_img)
        self.graphics_scene.render(painter, QRectF(render_img.rect()), render_rect)
        painter.end()

        if self.text_item and was_selected:
            self.text_item.setSelected(True)

        arr = self._qimage_to_numpy(render_img)
        cv_img = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

        safe_filename = sanitize_filename(self.current_number)
        base = f"{safe_filename}.png"
        filepath = self.output_dir / base

        if filepath.exists():
            suffix = rng.randint(1000, 9999)
            filepath = self.output_dir / f"{safe_filename}_{suffix}.png"

        success = cv2.imwrite(str(filepath), cv_img)

        if success:
            logger.success(f"Saved: {filepath.name} [{cv_img.shape[1]}x{cv_img.shape[0]}]")
        else:
            logger.error("Save failed")

    def export_config(self):
        """Export current settings to a YAML config file."""
        from textbaker.core.configs import (
            BackgroundConfig,
            CharacterConfig,
            ColorConfig,
            DatasetConfig,
            GeneratorConfig,
            OutputConfig,
            TextureConfig,
            TransformConfig,
        )

        # Build config from current GUI settings
        config = GeneratorConfig(
            seed=42,  # Default seed
            spacing=self.min_h_margin.value(),
            text_length=(self.min_chars.value(), self.max_chars.value()),
            canvas_height=self.canvas_height.value(),
            max_v_offset=self.max_v_offset.value(),
            font_scale=self.font_scale.value(),
            dataset=DatasetConfig(
                dataset_dir=self.dataset_root
                if self.dataset_root.exists()
                else Path("assets/dataset"),
            ),
            transform=TransformConfig(
                rotation_range=(float(self.min_rotation.value()), float(self.max_rotation.value())),
                perspective_range=(
                    float(self.min_perspective.value()),
                    float(self.max_perspective.value()),
                ),
                scale_range=(self.min_resize_scale.value(), self.max_resize_scale.value()),
            ),
            color=ColorConfig(
                random_color=self.enable_color_checkbox.isChecked(),
                color_range_r=(self.min_r.value(), self.max_r.value()),
                color_range_g=(self.min_g.value(), self.max_g.value()),
                color_range_b=(self.min_b.value(), self.max_b.value()),
            ),
            texture=TextureConfig(
                enabled=not self.no_texture_radio.isChecked(),
                texture_dir=self.texture_dir if self.texture_dir.exists() else None,
                per_character=self.texture_per_char_radio.isChecked(),
            ),
            background=BackgroundConfig(
                enabled=bool(self.background_paths),
                background_dir=self.background_dir if self.background_dir.exists() else None,
            ),
            output=OutputConfig(
                output_dir=self.output_dir if self.output_dir.exists() else Path("output"),
                crop_to_text=self.crop_to_text_checkbox.isChecked(),
            ),
            character=CharacterConfig(
                width=self.char_dimension.value(),
                height=self.char_dimension.value(),
            ),
        )

        # Ask user where to save
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Configuration",
            "textbaker_config.yaml",
            "YAML Files (*.yaml *.yml);;JSON Files (*.json);;All Files (*)",
        )

        if filepath:
            filepath = Path(filepath)
            try:
                config.to_file(filepath)
                logger.success(f"Config exported: {filepath.name}")
                QMessageBox.information(
                    self, "Config Exported", f"Configuration saved to:\n{filepath}"
                )
            except Exception as e:
                logger.error(f"Failed to export config: {e}")
                QMessageBox.warning(self, "Export Failed", f"Failed to export config:\n{e}")
