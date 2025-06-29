import sys
import random
import math
import colorsys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QSlider, QCheckBox, QFileDialog, QComboBox,
    QGroupBox, QSpinBox, QDoubleSpinBox, QColorDialog, QTabWidget
)
from PyQt5.QtGui import (
    QPainter, QColor, QPixmap, QPolygonF, QPainterPath, QBrush, QPen,
    QLinearGradient, QRadialGradient, QConicalGradient, QImage, QFont
)
from PyQt5.QtCore import Qt, QPointF, QSize


class AbstractArtGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Abstract Art Generator")
        self.canvas_width = 800
        self.canvas_height = 600

        # Initialize with some colors
        self.colors = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3", "#33FFF3"]
        self.selected_colors = []
        self.shape_checkboxes = {}
        self.last_pixmap = None
        self.random_seed = 42

        # Create main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Create tabs for organization
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs, 3)

        # Canvas
        self.canvas = QLabel()
        self.canvas.setFixedSize(self.canvas_width, self.canvas_height)
        self.canvas.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        self.main_layout.addWidget(self.canvas, 7)

        # Create tab widgets
        self.create_color_tab()
        self.create_shape_tab()
        self.create_effects_tab()
        self.create_render_tab()

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # Render initial art
        self.render_art()

    def create_color_tab(self):
        """Create the color options tab"""
        color_tab = QWidget()
        layout = QVBoxLayout(color_tab)

        # Color palette group
        palette_group = QGroupBox("Color Palette")
        palette_layout = QVBoxLayout()

        self.color_layout = QGridLayout()
        self.color_layout.setColumnMinimumWidth(0, 120)

        # Add predefined colors
        self.add_color_button = QPushButton("Add Color")
        self.add_color_button.clicked.connect(self.add_custom_color)
        palette_layout.addWidget(self.add_color_button)

        self.clear_colors_button = QPushButton("Clear Custom Colors")
        self.clear_colors_button.clicked.connect(self.clear_custom_colors)
        palette_layout.addWidget(self.clear_colors_button)

        # Color harmony controls
        harmony_group = QGroupBox("Color Harmony")
        harmony_layout = QGridLayout()

        harmony_layout.addWidget(QLabel("Base Hue:"), 0, 0)
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setRange(0, 360)
        self.hue_slider.setValue(180)
        harmony_layout.addWidget(self.hue_slider, 0, 1)

        harmony_layout.addWidget(QLabel("Harmony:"), 1, 0)
        self.harmony_combo = QComboBox()
        self.harmony_combo.addItems(["Complementary", "Analogous", "Triadic", "Tetradic", "Monochromatic", "Random"])
        harmony_layout.addWidget(self.harmony_combo, 1, 1)

        harmony_layout.addWidget(QLabel("Saturation:"), 2, 0)
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(0, 100)
        self.saturation_slider.setValue(80)
        harmony_layout.addWidget(self.saturation_slider, 2, 1)

        harmony_layout.addWidget(QLabel("Value:"), 3, 0)
        self.value_slider = QSlider(Qt.Horizontal)
        self.value_slider.setRange(0, 100)
        self.value_slider.setValue(90)
        harmony_layout.addWidget(self.value_slider, 3, 1)

        harmony_group.setLayout(harmony_layout)

        # Add to layout
        palette_layout.addLayout(self.color_layout)
        palette_layout.addWidget(harmony_group)
        palette_group.setLayout(palette_layout)
        layout.addWidget(palette_group)

        # Background group
        bg_group = QGroupBox("Background")
        bg_layout = QVBoxLayout()

        bg_layout.addWidget(QLabel("Background Type:"))
        self.bg_combo = QComboBox()
        self.bg_combo.addItems(["Random", "Solid", "Gradient", "Pattern"])
        bg_layout.addWidget(self.bg_combo)

        self.bg_color_button = QPushButton("Choose Color")
        self.bg_color_button.clicked.connect(self.choose_bg_color)
        bg_layout.addWidget(self.bg_color_button)

        self.bg_color_preview = QLabel()
        self.bg_color_preview.setFixedSize(40, 40)
        self.bg_color_preview.setStyleSheet("background-color: #FFFFFF; border: 1px solid #ccc;")
        bg_layout.addWidget(self.bg_color_preview)

        bg_group.setLayout(bg_layout)
        layout.addWidget(bg_group)

        layout.addStretch()
        self.tabs.addTab(color_tab, "Colors")

        # Initialize color checkboxes
        self.update_color_checkboxes()

    def create_shape_tab(self):
        """Create the shape options tab"""
        shape_tab = QWidget()
        layout = QVBoxLayout(shape_tab)

        # Shape selection
        shape_group = QGroupBox("Shape Selection")
        shape_layout = QVBoxLayout()

        # Available shapes - use "rotated_rect" instead of "rect"
        self.shapes = ["rotated_rect", "ellipse", "polygon", "spiral", "bezier", "star", "arc", "donut", "cross",
                       "line", "text"]

        # Create checkboxes for each shape
        shape_grid = QGridLayout()
        row, col = 0, 0
        for shape in self.shapes:
            display_name = shape.replace("_", " ").title()
            box = QCheckBox(display_name)
            box.setChecked(True)
            self.shape_checkboxes[shape] = box
            shape_grid.addWidget(box, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        shape_layout.addLayout(shape_grid)
        shape_group.setLayout(shape_layout)
        layout.addWidget(shape_group)

        # Shape parameters
        param_group = QGroupBox("Shape Parameters")
        param_layout = QGridLayout()

        param_layout.addWidget(QLabel("Min Size:"), 0, 0)
        self.min_size_slider = QSlider(Qt.Horizontal)
        self.min_size_slider.setRange(5, 200)
        self.min_size_slider.setValue(10)
        param_layout.addWidget(self.min_size_slider, 0, 1)

        param_layout.addWidget(QLabel("Max Size:"), 1, 0)
        self.max_size_slider = QSlider(Qt.Horizontal)
        self.max_size_slider.setRange(10, 500)
        self.max_size_slider.setValue(150)
        param_layout.addWidget(self.max_size_slider, 1, 1)

        param_layout.addWidget(QLabel("Min Rotation:"), 2, 0)
        self.min_rot_slider = QSlider(Qt.Horizontal)
        self.min_rot_slider.setRange(0, 360)
        self.min_rot_slider.setValue(0)
        param_layout.addWidget(self.min_rot_slider, 2, 1)

        param_layout.addWidget(QLabel("Max Rotation:"), 3, 0)
        self.max_rot_slider = QSlider(Qt.Horizontal)
        self.max_rot_slider.setRange(0, 360)
        self.max_rot_slider.setValue(360)
        param_layout.addWidget(self.max_rot_slider, 3, 1)

        param_layout.addWidget(QLabel("Shape Detail:"), 4, 0)
        self.detail_slider = QSlider(Qt.Horizontal)
        self.detail_slider.setRange(3, 20)
        self.detail_slider.setValue(8)
        param_layout.addWidget(self.detail_slider, 4, 1)

        param_layout.addWidget(QLabel("Text Content:"), 5, 0)
        self.text_content = QComboBox()
        self.text_content.addItems(["ABC", "123", "!@#", "XYZ", "&*?", "Art", "Design", "Random"])
        param_layout.addWidget(self.text_content, 5, 1)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # Symmetry
        symmetry_group = QGroupBox("Symmetry")
        symmetry_layout = QGridLayout()

        symmetry_layout.addWidget(QLabel("Symmetry Type:"), 0, 0)
        self.symmetry_combo = QComboBox()
        self.symmetry_combo.addItems(["None", "Horizontal", "Vertical", "Radial"])
        symmetry_layout.addWidget(self.symmetry_combo, 0, 1)

        symmetry_layout.addWidget(QLabel("Radial Sections:"), 1, 0)
        self.radial_sections = QSpinBox()
        self.radial_sections.setRange(2, 12)
        self.radial_sections.setValue(6)
        symmetry_layout.addWidget(self.radial_sections, 1, 1)

        symmetry_group.setLayout(symmetry_layout)
        layout.addWidget(symmetry_group)

        layout.addStretch()
        self.tabs.addTab(shape_tab, "Shapes")

    def create_effects_tab(self):
        """Create the effects options tab"""
        effects_tab = QWidget()
        layout = QVBoxLayout(effects_tab)

        # Transparency
        alpha_group = QGroupBox("Transparency")
        alpha_layout = QGridLayout()

        self.alpha_checkbox = QCheckBox("Enable Transparency")
        self.alpha_checkbox.setChecked(True)
        alpha_layout.addWidget(self.alpha_checkbox, 0, 0, 1, 2)

        alpha_layout.addWidget(QLabel("Min Opacity:"), 1, 0)
        self.min_alpha_slider = QSlider(Qt.Horizontal)
        self.min_alpha_slider.setRange(50, 255)
        self.min_alpha_slider.setValue(100)
        alpha_layout.addWidget(self.min_alpha_slider, 1, 1)

        alpha_layout.addWidget(QLabel("Max Opacity:"), 2, 0)
        self.max_alpha_slider = QSlider(Qt.Horizontal)
        self.max_alpha_slider.setRange(50, 255)
        self.max_alpha_slider.setValue(255)
        alpha_layout.addWidget(self.max_alpha_slider, 2, 1)

        alpha_group.setLayout(alpha_layout)
        layout.addWidget(alpha_group)

        # Gradients
        gradient_group = QGroupBox("Gradients")
        gradient_layout = QGridLayout()

        self.gradient_checkbox = QCheckBox("Use Gradients")
        self.gradient_checkbox.setChecked(True)
        gradient_layout.addWidget(self.gradient_checkbox, 0, 0, 1, 2)

        gradient_layout.addWidget(QLabel("Gradient Type:"), 1, 0)
        self.gradient_combo = QComboBox()
        self.gradient_combo.addItems(["Linear", "Radial", "Conical", "Random"])
        gradient_layout.addWidget(self.gradient_combo, 1, 1)

        gradient_layout.addWidget(QLabel("Complexity:"), 2, 0)
        self.gradient_complexity = QSlider(Qt.Horizontal)
        self.gradient_complexity.setRange(1, 5)
        self.gradient_complexity.setValue(3)
        gradient_layout.addWidget(self.gradient_complexity, 2, 1)

        gradient_group.setLayout(gradient_layout)
        layout.addWidget(gradient_group)

        # Stroke
        stroke_group = QGroupBox("Stroke / Outline")
        stroke_layout = QGridLayout()

        self.stroke_checkbox = QCheckBox("Enable Stroke")
        self.stroke_checkbox.setChecked(True)
        stroke_layout.addWidget(self.stroke_checkbox, 0, 0, 1, 2)

        stroke_layout.addWidget(QLabel("Stroke Width:"), 1, 0)
        self.stroke_width = QSlider(Qt.Horizontal)
        self.stroke_width.setRange(1, 20)
        self.stroke_width.setValue(2)
        stroke_layout.addWidget(self.stroke_width, 1, 1)

        stroke_layout.addWidget(QLabel("Stroke Color:"), 2, 0)
        self.stroke_color_combo = QComboBox()
        self.stroke_color_combo.addItems(["Contrast", "Complementary", "Random", "Black", "White"])
        stroke_layout.addWidget(self.stroke_color_combo, 2, 1)

        stroke_group.setLayout(stroke_layout)
        layout.addWidget(stroke_group)

        # Texture
        texture_group = QGroupBox("Texture")
        texture_layout = QGridLayout()

        self.texture_checkbox = QCheckBox("Add Texture")
        self.texture_checkbox.setChecked(False)
        texture_layout.addWidget(self.texture_checkbox, 0, 0, 1, 2)

        texture_layout.addWidget(QLabel("Texture Type:"), 1, 0)
        self.texture_combo = QComboBox()
        self.texture_combo.addItems(["Noise", "Lines", "Dots", "Paper"])
        texture_layout.addWidget(self.texture_combo, 1, 1)

        texture_layout.addWidget(QLabel("Intensity:"), 2, 0)
        self.texture_intensity = QSlider(Qt.Horizontal)
        self.texture_intensity.setRange(1, 100)
        self.texture_intensity.setValue(30)
        texture_layout.addWidget(self.texture_intensity, 2, 1)

        texture_group.setLayout(texture_layout)
        layout.addWidget(texture_group)

        layout.addStretch()
        self.tabs.addTab(effects_tab, "Effects")

    def create_render_tab(self):
        """Create the render options tab"""
        render_tab = QWidget()
        layout = QVBoxLayout(render_tab)

        # Complexity
        complexity_group = QGroupBox("Complexity")
        complexity_layout = QGridLayout()

        complexity_layout.addWidget(QLabel("Number of Shapes:"), 0, 0)
        self.complexity_slider = QSlider(Qt.Horizontal)
        self.complexity_slider.setMinimum(10)
        self.complexity_slider.setMaximum(500)
        self.complexity_slider.setValue(150)
        complexity_layout.addWidget(self.complexity_slider, 0, 1)

        complexity_layout.addWidget(QLabel("Shape Density:"), 1, 0)
        self.density_slider = QSlider(Qt.Horizontal)
        self.density_slider.setMinimum(1)
        self.density_slider.setMaximum(100)
        self.density_slider.setValue(50)
        complexity_layout.addWidget(self.density_slider, 1, 1)

        complexity_group.setLayout(complexity_layout)
        layout.addWidget(complexity_group)

        # Randomness
        random_group = QGroupBox("Randomness")
        random_layout = QGridLayout()

        random_layout.addWidget(QLabel("Random Seed:"), 0, 0)
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(1, 999999)
        self.seed_spin.setValue(42)
        random_layout.addWidget(self.seed_spin, 0, 1)

        self.random_seed_button = QPushButton("Random Seed")
        self.random_seed_button.clicked.connect(self.set_random_seed)
        random_layout.addWidget(self.random_seed_button, 1, 0, 1, 2)

        random_layout.addWidget(QLabel("Chaos Factor:"), 2, 0)
        self.chaos_slider = QSlider(Qt.Horizontal)
        self.chaos_slider.setRange(0, 100)
        self.chaos_slider.setValue(30)
        random_layout.addWidget(self.chaos_slider, 2, 1)

        random_group.setLayout(random_layout)
        layout.addWidget(random_group)

        # Buttons
        button_row = QHBoxLayout()
        self.render_button = QPushButton("Render Art")
        self.render_button.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.render_button.clicked.connect(self.render_art)
        button_row.addWidget(self.render_button)

        self.save_button = QPushButton("Save Image")
        self.save_button.setStyleSheet("background-color: #2196F3; color: white;")
        self.save_button.clicked.connect(self.save_image)
        button_row.addWidget(self.save_button)

        layout.addLayout(button_row)
        layout.addStretch()
        self.tabs.addTab(render_tab, "Render")

    def update_color_checkboxes(self):
        """Update the color checkboxes based on current color list"""
        # Clear existing checkboxes
        for i in reversed(range(self.color_layout.count())):
            widget = self.color_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Add new checkboxes
        row, col = 0, 0
        for i, color in enumerate(self.colors):
            checkbox = QCheckBox("")
            checkbox.setStyleSheet(f"background-color: {color}; border: 1px solid #ccc;")
            checkbox.setFixedSize(30, 30)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.make_color_toggle(i))

            # Add color label
            color_label = QLabel(f"Color {i + 1}")
            color_label.setFixedWidth(60)

            self.color_layout.addWidget(color_label, row, col * 2)
            self.color_layout.addWidget(checkbox, row, col * 2 + 1)

            col += 1
            if col > 2:
                col = 0
                row += 1

    def make_color_toggle(self, idx):
        """Create a toggle function for color checkboxes"""

        def toggle(state):
            if state == Qt.Checked:
                if idx not in self.selected_colors:
                    self.selected_colors.append(idx)
            elif idx in self.selected_colors:
                self.selected_colors.remove(idx)

        return toggle

    def add_custom_color(self):
        """Add a custom color to the palette"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.colors.append(color.name())
            self.update_color_checkboxes()

    def clear_custom_colors(self):
        """Clear all custom colors"""
        # Keep the first 6 default colors
        self.colors = self.colors[:6]
        self.update_color_checkboxes()

    def choose_bg_color(self):
        """Choose a background color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color_preview.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #ccc;")

    def set_random_seed(self):
        """Set a random seed value"""
        seed = random.randint(1, 999999)
        self.seed_spin.setValue(seed)

    def generate_harmony_colors(self, base_hue, harmony_type):
        """Generate a color harmony based on the selected type"""
        saturation = self.saturation_slider.value() / 100.0
        value = self.value_slider.value() / 100.0

        base_rgb = colorsys.hsv_to_rgb(base_hue / 360, saturation, value)
        base_color = QColor.fromRgbF(*base_rgb)

        harmonies = []

        if harmony_type == "Complementary":
            comp_hue = (base_hue + 180) % 360
            comp_rgb = colorsys.hsv_to_rgb(comp_hue / 360, saturation, value)
            harmonies = [base_color, QColor.fromRgbF(*comp_rgb)]

        elif harmony_type == "Analogous":
            harmonies = [
                QColor.fromRgbF(*colorsys.hsv_to_rgb(((base_hue - 30) % 360) / 360, saturation, value)),
                base_color,
                QColor.fromRgbF(*colorsys.hsv_to_rgb(((base_hue + 30) % 360) / 360, saturation, value))
            ]

        elif harmony_type == "Triadic":
            harmonies = [
                base_color,
                QColor.fromRgbF(*colorsys.hsv_to_rgb(((base_hue + 120) % 360) / 360, saturation, value)),
                QColor.fromRgbF(*colorsys.hsv_to_rgb(((base_hue + 240) % 360) / 360, saturation, value))
            ]

        elif harmony_type == "Tetradic":
            harmonies = [
                base_color,
                QColor.fromRgbF(*colorsys.hsv_to_rgb(((base_hue + 60) % 360) / 360, saturation, value)),
                QColor.fromRgbF(*colorsys.hsv_to_rgb(((base_hue + 180) % 360) / 360, saturation, value)),
                QColor.fromRgbF(*colorsys.hsv_to_rgb(((base_hue + 240) % 360) / 360, saturation, value))
            ]

        elif harmony_type == "Monochromatic":
            harmonies = [
                QColor.fromRgbF(
                    *colorsys.hsv_to_rgb(base_hue / 360, max(0.2, saturation * 0.7), min(1.0, value * 1.2))),
                base_color,
                QColor.fromRgbF(*colorsys.hsv_to_rgb(base_hue / 360, min(1.0, saturation * 1.2), max(0.2, value * 0.7)))
            ]

        else:  # Random
            harmonies = [self.generate_random_color() for _ in range(4)]

        return harmonies

    def generate_random_color(self):
        """Generate a random color"""
        return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def create_texture(self, width, height, texture_type, intensity):
        """Create a texture image"""
        img = QImage(width, height, QImage.Format_ARGB32)
        img.fill(Qt.transparent)

        painter = QPainter(img)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # Adjust intensity (0-100 to 0.0-1.0)
        intensity = intensity / 100.0

        if texture_type == "Noise":
            for x in range(0, width, 5):
                for y in range(0, height, 5):
                    if random.random() < intensity * 0.3:
                        size = random.randint(1, 4)
                        alpha = random.randint(30, 100)
                        color = QColor(0, 0, 0, alpha)
                        painter.setBrush(color)
                        painter.drawEllipse(x, y, size, size)

        elif texture_type == "Lines":
            line_count = int(50 * intensity)
            for _ in range(line_count):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = x1 + random.randint(-50, 50)
                y2 = y1 + random.randint(-50, 50)
                width_val = random.randint(1, 3)
                alpha = random.randint(30, 80)
                color = QColor(0, 0, 0, alpha)
                pen = QPen(color, width_val)
                painter.setPen(pen)
                painter.drawLine(x1, y1, x2, y2)

        elif texture_type == "Dots":
            dot_count = int(500 * intensity)
            for _ in range(dot_count):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(1, 4)
                alpha = random.randint(30, 100)
                color = QColor(0, 0, 0, alpha)
                painter.setBrush(color)
                painter.drawEllipse(x, y, size, size)

        elif texture_type == "Paper":
            # Create a subtle paper-like texture
            for x in range(0, width, 3):
                for y in range(0, height, 3):
                    if random.random() < intensity * 0.1:
                        alpha = random.randint(5, 15)
                        color = QColor(200, 200, 200, alpha)
                        painter.setBrush(color)
                        painter.drawRect(x, y, 2, 2)

        painter.end()
        return img

    def draw_rotated_rect(self, painter):
        """Draw a rotated rectangle"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()
        min_rot = self.min_rot_slider.value()
        max_rot = self.max_rot_slider.value()

        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        x = random.randint(0, self.canvas_width - w)
        y = random.randint(0, self.canvas_height - h)
        angle = random.randint(min_rot, max_rot)

        painter.save()
        painter.translate(x + w / 2, y + h / 2)
        painter.rotate(angle)
        painter.drawRect(int(-w / 2), int(-h / 2), int(w), int(h))
        painter.restore()

    def draw_ellipse(self, painter):
        """Draw an ellipse"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()

        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        x = random.randint(0, self.canvas_width - w)
        y = random.randint(0, self.canvas_height - h)
        painter.drawEllipse(x, y, w, h)

    def draw_polygon(self, painter):
        """Draw a polygon"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()
        detail = self.detail_slider.value()

        # Create a center point
        cx = random.randint(50, self.canvas_width - 50)
        cy = random.randint(50, self.canvas_height - 50)

        points = []
        for i in range(detail):
            angle = 2 * math.pi * i / detail
            radius = random.randint(min_size // 2, max_size // 2)
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append(QPointF(x, y))

        polygon = QPolygonF(points)
        painter.drawPolygon(polygon)

    def draw_spiral(self, painter):
        """Draw a spiral"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()
        detail = self.detail_slider.value()

        center = QPointF(random.randint(100, self.canvas_width - 100),
                         random.randint(100, self.canvas_height - 100))
        size = random.randint(min_size // 2, max_size // 2)
        turns = random.randint(3, 8)
        path = self.generate_spiral(center, size, turns, detail)
        painter.drawPath(path)

    def draw_bezier(self, painter):
        """Draw a Bezier curve"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()

        start = QPointF(random.randint(0, self.canvas_width), random.randint(0, self.canvas_height))
        ctrl1 = QPointF(random.randint(0, self.canvas_width), random.randint(0, self.canvas_height))
        ctrl2 = QPointF(random.randint(0, self.canvas_width), random.randint(0, self.canvas_height))
        end = QPointF(random.randint(0, self.canvas_width), random.randint(0, self.canvas_height))

        # Create a path with thickness
        path = QPainterPath()
        path.moveTo(start)
        path.cubicTo(ctrl1, ctrl2, end)

        # Draw the curve with thickness
        pen = painter.pen()
        pen.setWidth(random.randint(1, 5))
        painter.setPen(pen)
        painter.drawPath(path)

    def draw_star(self, painter):
        """Draw a star"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()
        detail = self.detail_slider.value()

        cx = random.randint(50, self.canvas_width - 50)
        cy = random.randint(50, self.canvas_height - 50)
        outer_radius = random.randint(min_size // 2, max_size // 2)
        inner_radius = outer_radius * 0.5

        points = []
        for i in range(detail * 2):
            angle = math.pi * i / detail
            radius = inner_radius if i % 2 == 1 else outer_radius
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            points.append(QPointF(x, y))

        polygon = QPolygonF(points)
        painter.drawPolygon(polygon)

    def draw_arc(self, painter):
        """Draw an arc"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()

        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        x = random.randint(0, self.canvas_width - w)
        y = random.randint(0, self.canvas_height - h)
        start_angle = random.randint(0, 360) * 16
        span_angle = random.randint(45, 270) * 16

        painter.drawArc(x, y, w, h, start_angle, span_angle)

    def draw_donut(self, painter):
        """Draw a donut shape"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()

        cx = random.randint(50, self.canvas_width - 50)
        cy = random.randint(50, self.canvas_height - 50)
        outer_radius = random.randint(min_size // 2, max_size // 2)
        inner_radius = outer_radius * random.uniform(0.3, 0.7)

        path = QPainterPath()
        path.addEllipse(cx, cy, outer_radius, outer_radius)
        inner_path = QPainterPath()
        inner_path.addEllipse(cx + (outer_radius - inner_radius) / 2,
                              cy + (outer_radius - inner_radius) / 2,
                              inner_radius, inner_radius)
        path = path.subtracted(inner_path)
        painter.drawPath(path)

    def draw_cross(self, painter):
        """Draw a cross"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()

        cx = random.randint(50, self.canvas_width - 50)
        cy = random.randint(50, self.canvas_height - 50)
        size = random.randint(min_size, max_size)
        thickness = random.randint(5, size // 3)

        # Horizontal bar
        painter.drawRect(cx - size // 2, cy - thickness // 2, size, thickness)
        # Vertical bar
        painter.drawRect(cx - thickness // 2, cy - size // 2, thickness, size)

    def draw_line(self, painter):
        """Draw a line"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()

        x1 = random.randint(0, self.canvas_width)
        y1 = random.randint(0, self.canvas_height)
        length = random.randint(min_size, max_size)
        angle = random.uniform(0, 2 * math.pi)

        x2 = x1 + length * math.cos(angle)
        y2 = y1 + length * math.sin(angle)

        # Set pen width
        pen = painter.pen()
        pen.setWidth(random.randint(1, 5))
        painter.setPen(pen)

        painter.drawLine(x1, y1, x2, y2)

    def draw_text(self, painter):
        """Draw text as a shape"""
        min_size = self.min_size_slider.value()
        max_size = self.max_size_slider.value()

        x = random.randint(50, self.canvas_width - 50)
        y = random.randint(50, self.canvas_height - 50)
        size = random.randint(min_size, max_size)

        # Choose text content
        text_choice = self.text_content.currentText()
        if text_choice == "Random":
            text_options = ["A", "B", "C", "1", "2", "3", "!", "@", "#", "&", "*", "X", "Y", "Z"]
            text = random.choice(text_options)
        else:
            text = text_choice

        font = QFont("Arial", size)
        painter.setFont(font)
        painter.drawText(x, y, text)

    def generate_spiral(self, center, size, turns, detail):
        """Generate a spiral path"""
        path = QPainterPath()
        angle = 0
        max_angle = turns * 360
        step = 5

        path.moveTo(center)
        for i in range(0, max_angle, step):
            r = size * (1 + i / max_angle)
            rad_angle = math.radians(i)
            x = center.x() + r * math.cos(rad_angle)
            y = center.y() + r * math.sin(rad_angle)
            path.lineTo(QPointF(x, y))

        return path

    def random_gradient(self, base_color, width, height):
        """Create a random gradient"""
        gradient_type = self.gradient_combo.currentText()
        if gradient_type == "Random":
            gradient_type = random.choice(["Linear", "Radial", "Conical"])

        if gradient_type == "Linear":
            grad = QLinearGradient(
                random.randint(0, width),
                random.randint(0, height),
                random.randint(0, width),
                random.randint(0, height)
            )
        elif gradient_type == "Radial":
            cx = random.randint(0, width)
            cy = random.randint(0, height)
            radius = random.randint(50, min(width, height) // 2)
            grad = QRadialGradient(cx, cy, radius)
        else:  # Conical
            cx = random.randint(0, width)
            cy = random.randint(0, height)
            angle = random.randint(0, 360)
            grad = QConicalGradient(cx, cy, angle)

        # Add color stops
        stops = self.gradient_complexity.value() + 1
        for i in range(stops):
            pos = i / (stops - 1) if stops > 1 else 0.5
            # Create a variation of the base color
            h, s, v, a = base_color.getHsvF()
            h = (h + random.uniform(-0.1, 0.1)) % 1.0
            s = min(1.0, max(0.0, s + random.uniform(-0.2, 0.2)))
            v = min(1.0, max(0.0, v + random.uniform(-0.2, 0.2)))
            color = QColor.fromHsvF(h, s, v, a)
            grad.setColorAt(pos, color)

        return grad

    def get_stroke_color(self, base_color):
        """Get a stroke color based on the selected option"""
        stroke_type = self.stroke_color_combo.currentText()

        if stroke_type == "Contrast":
            # Return black or white based on color brightness
            brightness = base_color.red() * 0.299 + base_color.green() * 0.587 + base_color.blue() * 0.114
            return QColor(Qt.black) if brightness > 128 else QColor(Qt.white)

        elif stroke_type == "Complementary":
            # Get complementary color
            h, s, v, a = base_color.getHsvF()
            comp_h = (h + 0.5) % 1.0
            return QColor.fromHsvF(comp_h, s, v)

        elif stroke_type == "Random":
            return self.generate_random_color()

        elif stroke_type == "Black":
            return QColor(Qt.black)

        else:  # White
            return QColor(Qt.white)

    def apply_symmetry(self, painter, shape_func):
        """Apply symmetry to a shape"""
        symmetry_type = self.symmetry_combo.currentText()

        if symmetry_type == "None":
            shape_func(painter)
            return

        # Save the original transformation
        painter.save()

        if symmetry_type == "Horizontal":
            # Draw original
            shape_func(painter)

            # Draw reflection
            painter.translate(self.canvas_width, 0)
            painter.scale(-1, 1)
            shape_func(painter)

        elif symmetry_type == "Vertical":
            # Draw original
            shape_func(painter)

            # Draw reflection
            painter.translate(0, self.canvas_height)
            painter.scale(1, -1)
            shape_func(painter)

        elif symmetry_type == "Radial":
            sections = self.radial_sections.value()
            angle_step = 360 / sections

            for i in range(sections):
                # Save state for each section
                painter.save()

                # Move to center and rotate
                painter.translate(self.canvas_width / 2, self.canvas_height / 2)
                painter.rotate(i * angle_step)
                painter.translate(-self.canvas_width / 2, -self.canvas_height / 2)

                # Draw the shape
                shape_func(painter)

                # Restore to original state
                painter.restore()

        # Restore original transformation
        painter.restore()

    def render_art(self):
        """Render the abstract art based on current settings"""
        try:
            # Set random seed for reproducibility
            self.random_seed = self.seed_spin.value()
            random.seed(self.random_seed)

            # Create pixmap and painter
            pixmap = QPixmap(self.canvas_width, self.canvas_height)

            # Set background
            bg_type = self.bg_combo.currentText()
            if bg_type == "Random":
                bg_color = self.generate_random_color()
                pixmap.fill(bg_color)
            elif bg_type == "Solid":
                bg_color = QColor(self.bg_color_preview.palette().window().color())
                pixmap.fill(bg_color)
            elif bg_type == "Gradient":
                # Create a random gradient background
                painter = QPainter(pixmap)
                gradient = self.random_gradient(self.generate_random_color(),
                                                self.canvas_width, self.canvas_height)
                painter.fillRect(0, 0, self.canvas_width, self.canvas_height, gradient)
                painter.end()
            else:  # Pattern
                pixmap.fill(Qt.white)
                painter = QPainter(pixmap)
                for _ in range(100):
                    color = self.generate_random_color()
                    color.setAlpha(50)
                    painter.setBrush(color)
                    size = random.randint(10, 100)
                    x = random.randint(0, self.canvas_width)
                    y = random.randint(0, self.canvas_height)
                    painter.drawEllipse(x, y, size, size)
                painter.end()

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # Get selected colors or generate harmony
            selected_colors = [QColor(color) for i, color in enumerate(self.colors)
                               if i in self.selected_colors or not self.selected_colors]

            if not selected_colors:
                base_hue = self.hue_slider.value()
                harmony_type = self.harmony_combo.currentText()
                selected_colors = self.generate_harmony_colors(base_hue, harmony_type)

            # Get enabled shapes
            enabled_shapes = [s for s in self.shapes if self.shape_checkboxes[s].isChecked()]

            # Get number of shapes based on complexity and density
            complexity = self.complexity_slider.value()
            density = self.density_slider.value() / 100.0
            num_shapes = int(complexity * density)

            # Set stroke if enabled
            if self.stroke_checkbox.isChecked():
                pen_width = self.stroke_width.value()
                painter.setPen(QPen(Qt.black, pen_width))
            else:
                painter.setPen(Qt.NoPen)

            # Draw shapes
            for _ in range(num_shapes):
                color = random.choice(selected_colors)

                # Set transparency
                if self.alpha_checkbox.isChecked():
                    min_alpha = self.min_alpha_slider.value()
                    max_alpha = self.max_alpha_slider.value()
                    alpha = random.randint(min_alpha, max_alpha)
                    color.setAlpha(alpha)
                else:
                    color.setAlpha(255)

                # Set fill style (solid or gradient)
                if self.gradient_checkbox.isChecked():
                    brush = QBrush(self.random_gradient(color, self.canvas_width, self.canvas_height))
                else:
                    brush = QBrush(color)

                painter.setBrush(brush)

                # Set stroke color if enabled
                if self.stroke_checkbox.isChecked():
                    stroke_color = self.get_stroke_color(color)
                    painter.setPen(QPen(stroke_color, self.stroke_width.value()))

                # Choose shape function
                shape_type = random.choice(enabled_shapes)
                shape_func = getattr(self, f"draw_{shape_type}")

                # Apply symmetry
                self.apply_symmetry(painter, shape_func)

            # Add texture if enabled
            if self.texture_checkbox.isChecked():
                texture_type = self.texture_combo.currentText()
                intensity = self.texture_intensity.value()
                texture = self.create_texture(self.canvas_width, self.canvas_height,
                                              texture_type, intensity)
                painter.drawImage(0, 0, texture)

            painter.end()

            # Update canvas
            self.canvas.setPixmap(pixmap)
            self.last_pixmap = pixmap
            self.status_bar.showMessage(f"Rendered {num_shapes} shapes with seed {self.random_seed}")

        except Exception as e:
            self.status_bar.showMessage(f"Error: {str(e)}")

    def save_image(self):
        """Save the generated image to a file"""
        if not self.last_pixmap:
            self.status_bar.showMessage("No image to save")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Art", "",
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*)"
        )

        if file_path:
            if file_path.endswith(('.png', '.jpg', '.jpeg')):
                self.last_pixmap.save(file_path)
                self.status_bar.showMessage(f"Image saved to {file_path}")
            else:
                # Default to PNG if no extension
                self.last_pixmap.save(file_path + ".png")
                self.status_bar.showMessage(f"Image saved to {file_path}.png")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Modern style

    # Set a consistent font
    font = QFont("Arial", 10)
    app.setFont(font)

    window = AbstractArtGenerator()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
