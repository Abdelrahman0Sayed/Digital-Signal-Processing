# main.py
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMenu, QAction, QToolTip
from functools import partial


# Define color palette
COLORS = {
    'background': '#1e1e1e',
    'surface': '#252526',
    'primary': '#007ACC',
    'secondary': '#3E3E42',
    'text': '#CCCCCC',
    'border': '#323232'
}

# Add to COLORS dictionary
COLORS.update({
    'hover': '#404040',
    'success': '#4CAF50',
    'warning': '#FFA726',
    'info': '#29B6F6'
})

class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.viewers = []
        self.outputViewers = []
        self._setup_ui()
        self._setup_theme()
        self.oldPos = None
        self.controller = None
        self._setup_shortcuts()
        self._setup_statusbar()
        self._setup_menus()
        self.undo_stack = []
        self.redo_stack = []

    def _setup_theme(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {COLORS['background']};
            }}
            QWidget#container {{
                background: {COLORS['background']};
                border: 1px solid {COLORS['border']};
            }}
            QWidget {{
                background: {COLORS['background']};
                color: {COLORS['text']};
            }}
            
            /* Enhanced Button Styling */
            QPushButton {{
                background: {COLORS['secondary']};
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                color: {COLORS['text']};
                transition: background 0.3s;
            }}
            QPushButton:hover {{
                background: {COLORS['primary']};
                color: white;
            }}
            QPushButton:pressed {{
                background: #005999;
            }}
            
            /* Window Control Buttons */
            QPushButton#windowControl {{
                background: transparent;
                border-radius: 0px;
                padding: 4px 8px;
            }}
            QPushButton#windowControl:hover {{
                background: #3E3E42;
            }}
            QPushButton#closeButton:hover {{
                background: #E81123;
                color: white;
            }}
            
            /* Enhanced ComboBox */
            QComboBox {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 5px;
                color: {COLORS['text']};
                min-width: 100px;
            }}
            QComboBox:hover {{
                border: 1px solid {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }}
            
            /* Enhanced GroupBox */
            QGroupBox {{
                border: 1px solid {COLORS['border']};
                color: {COLORS['text']};
                margin-top: 12px;
                font-weight: bold;
                padding-top: 10px;
            }}
            QGroupBox:title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: {COLORS['primary']};
            }}
            
            /* Enhanced Slider */
            QSlider::groove:horizontal {{
                background: {COLORS['surface']};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['primary']};
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #2299FF;
                width: 18px;
                margin: -7px 0;
            }}
            
            /* Enhanced Progress Bar */
            QProgressBar {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text']};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                        stop:0 {COLORS['primary']}, 
                                        stop:1 #2299FF);
                border-radius: 3px;
            }}
            
            /* Image Display Enhancement */
            QLabel#imageDisplay {{
                background-color: {COLORS['background']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 2px;
            }}
            QLabel#imageDisplay:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """)

    def _setup_ui(self):
        # Main container
        self.container = QWidget()
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Custom title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(32)
        title_bar.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['surface']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)

        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(10, 0, 10, 0)
        title_bar_layout.setSpacing(4)

        title = QLabel("Fourier Transform Mixer")
        title.setStyleSheet(f"color: {COLORS['text']}; font-size: 12px;")

        # Window controls
        controls = QWidget()
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(4)

        for btn_data in [("⚊", self.showMinimized), 
                ("☐", self.toggleMaximized),
                ("✕", self.close)]:
            btn = QPushButton(btn_data[0])
            btn.setFixedSize(24, 24)
            btn.clicked.connect(btn_data[1])
            
            # Set object name based on button type
            if btn_data[0] == "✕":
                btn.setObjectName("closeButton")
            else:
                btn.setObjectName("windowControl")
            
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #CCCCCC;
                }
                QPushButton#windowControl:hover {
                    background: #3E3E42;
                    color: white;
                }
                QPushButton#closeButton:hover {
                    background: #E81123;
                    color: white;
                }
            """)
            controls_layout.addWidget(btn)

        title_bar_layout.addWidget(title)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(controls)

        # Main content area
        content = QWidget()
        content_layout = QHBoxLayout(content)  # Changed to horizontal layout
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Left panel for image viewers
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Image viewers grid
        viewers_grid = QGridLayout()
        viewers_grid.setSpacing(10)
        
        for i in range(4):
            viewer = ImageViewerWidget('', is_output=False)
            self.viewers.append(viewer)
            viewers_grid.addWidget(viewer, i // 2, i % 2)

        
        left_layout.addLayout(viewers_grid)
        
        # Right panel for output and controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Output viewers
        output_group = QGroupBox("Output Viewers")
        output_layout = QVBoxLayout(output_group)
        for i in range(2):
            viewer = ImageViewerWidget(f"Output {i+1}", is_output=True)
            self.outputViewers.append(viewer)
            output_layout.addWidget(viewer)
        output_group.setLayout(output_layout)  # Set the layout for group box

        # Region selection controls
        region_group = QGroupBox("Region Selection")
        region_layout = QVBoxLayout(region_group)
        
        region_controls = QWidget()
        region_controls_layout = QHBoxLayout(region_controls)
        
        self.inner_region = QRadioButton("Inner")
        self.outer_region = QRadioButton("Outer")
        self.inner_region.setChecked(True)
        
        self.region_size = QSlider(Qt.Horizontal)
        self.region_size.setRange(1, 100)
        self.region_size.setValue(50)
        self.region_size.setToolTip("Adjust the size of selected region")
        
        self.deselect_btn = QPushButton("Clear Selection")
        
        region_controls_layout.addWidget(self.inner_region)
        region_controls_layout.addWidget(self.outer_region)
        region_controls_layout.addWidget(self.region_size)
        region_controls_layout.addWidget(self.deselect_btn)
        
        region_layout.addWidget(region_controls)
        
        # Add to right panel
        right_layout.addWidget(output_group)
        right_layout.addWidget(region_group)
        right_layout.addStretch()

        # Add panels to main content
        content_layout.addWidget(left_panel, stretch=60)  # 60% width
        content_layout.addWidget(right_panel, stretch=40)  # 40% width

        # Add content to main layout
        layout.addWidget(title_bar)
        layout.addWidget(content)

        # Mixing controls
        mixing_group = QGroupBox("Mixing Controls")
        mixing_layout = QHBoxLayout(mixing_group)

        self.mix_button = QPushButton("Start Mix")
        self.mix_button.setMinimumWidth(100)
        self.mix_button.setStyleSheet("""
            QPushButton[loading="true"] {
                background: #2d2d2d;
                color: #666666;
            }
        """)
        self.mix_button.setToolTip("Mix selected components from input images")

        self.mix_progress = QProgressBar()
        self.mix_progress.setMinimum(0)
        self.mix_progress.setMaximum(100)
        self.mix_progress.setValue(0)
        self.mix_progress.setTextVisible(True)
        self.mix_progress.hide()

        mixing_layout.addWidget(self.mix_button)
        mixing_layout.addWidget(self.mix_progress, stretch=1)

        # Add to right panel layout (before addStretch)
        right_layout.addWidget(mixing_group)

        # Component mixing controls
        mixing_type_group = QGroupBox("Mixing Type")
        mixing_type_layout = QVBoxLayout(mixing_type_group)

        self.mix_type = QComboBox()
        self.mix_type.addItems(["Magnitude/Phase", "Real/Imaginary"])
        self.mix_type.currentIndexChanged.connect(self.update_mixing_mode)

        # Output selector
        output_selector_layout = QHBoxLayout()
        output_label = QLabel("Mix to Output:")
        self.output_selector = QComboBox()
        self.output_selector.addItems(["Output 1", "Output 2"])
        output_selector_layout.addWidget(output_label)
        output_selector_layout.addWidget(self.output_selector)

        # Add widgets to layout
        mixing_type_layout.addWidget(self.mix_type)
        mixing_type_layout.addLayout(output_selector_layout)
        right_layout.addWidget(mixing_type_group)
        
        self.setCentralWidget(self.container)


    def update_mixing_mode(self, index):
        mode = self.mix_type.currentText()
        for viewer in self.viewers:
            viewer.update_weight_labels(mode)

    def toggleMaximized(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = None

    def show_error(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("Error")
        error_dialog.setInformativeText(message)
        error_dialog.setStyleSheet(f"""
            QMessageBox {{
                background: {COLORS['background']};
                color: {COLORS['text']};
            }}
            QPushButton {{
                background: {COLORS['secondary']};
                border: none;
                padding: 5px 15px;
                border-radius: 4px;
            }}
        """)
        error_dialog.exec_()

    def _setup_shortcuts(self):
        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+M"), self, self.showMinimized)
        QShortcut(QKeySequence("F11"), self, self.toggleMaximized)
        QShortcut(QKeySequence("Ctrl+R"), self, self.reset_all)

    def _setup_statusbar(self):
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet(f"""
            QStatusBar {{
                background: {COLORS['surface']};
                color: {COLORS['text']};
                border-top: 1px solid {COLORS['border']};
            }}
        """)
        self.setCentralWidget(self.container)
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")

    def reset_all(self):
        for viewer in self.viewers:
            viewer.reset()
        for output in self.outputViewers:
            output.reset()
        self.statusBar.showMessage("All viewers reset", 3000)
    
    def _setup_menus(self):
        self.context_menu = QMenu(self)
        
        # File operations
        #self.context_menu.addAction("Open Image...", self.open_image)
        #self.context_menu.addAction("Save Result...", self.save_result)
        self.context_menu.addSeparator()
        
        # Edit operations
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        self.context_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        self.context_menu.addAction(redo_action)
        
    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def undo(self):
        if self.undo_stack:
            state = self.undo_stack.pop()
            self.redo_stack.append(state)
            self.restore_state(state)
            self.statusBar.showMessage("Undo successful", 2000)

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.undo_stack.append(state)
            self.restore_state(state)
            self.statusBar.showMessage("Redo successful", 2000)
        
class ImageViewerWidget(QFrame):
    weightChanged = pyqtSignal(float, str)
    
    def __init__(self, title, window=None, is_output=False):  # Add is_output parameter
        super().__init__()
        self.setObjectName("imageViewer")
        self.window = window
        self.image = None
        self.ft_components = None
        self.brightness = 0
        self.contrast = 1
        self.is_output = is_output
        self._setup_ui(title)
        self._setup_animations()
        self.zoom_level = 1.0
        self._setup_zoom_controls()

    def _setup_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        # Header with title
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        title_label = QLabel(title)
        header_layout.addWidget(title_label)
        layout.addWidget(header)

        if self.is_output:
            # Single display for output viewers
            self.originalImageLabel = ImageDisplay()
            self.originalImageLabel.setAlignment(Qt.AlignCenter)
            self.originalImageLabel.setMinimumSize(200, 200)
            self.originalImageLabel.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    border: 1px solid #323232;
                    border-radius: 4px;
                }
            """)
            layout.addWidget(self.originalImageLabel)
            
        else:
            # Dual display for input viewers
            displays_layout = QHBoxLayout()

            # Original image section (left)
            original_section = QVBoxLayout()
            original_label = QLabel("Original Image")
            self.originalImageLabel = ImageDisplay()
            self.originalImageLabel.setAlignment(Qt.AlignCenter)
            self.originalImageLabel.setMinimumSize(200, 200)
            self.originalImageLabel.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    border: 1px solid #323232;
                    border-radius: 4px;
                }
            """)
            original_section.addWidget(original_label)
            original_section.addWidget(self.originalImageLabel)
            displays_layout.addLayout(original_section)

            # FT Component section (right)
            ft_section = QVBoxLayout()
            self.component_selector = QComboBox()
            self.component_selector.addItems([
                'FT Magnitude',
                'FT Phase',
                'FT Real',
                'FT Imaginary'
            ])
            self.component_selector.setToolTip("Select which Fourier component to view")
            ft_section.addWidget(self.component_selector)

            self.ftComponentLabel = ImageDisplay()
            self.ftComponentLabel.setAlignment(Qt.AlignCenter)
            self.ftComponentLabel.setMinimumSize(200, 200)
            self.ftComponentLabel.setStyleSheet("""
                QLabel {
                    background-color: #1e1e1e;
                    border: 1px solid #323232;
                    border-radius: 4px;
                }
            """)
            
            ft_label = QLabel("Fourier Transform Component")
            ft_section.addWidget(ft_label)
            ft_section.addWidget(self.ftComponentLabel)
            displays_layout.addLayout(ft_section)

            # Add displays layout to main layout
            layout.addLayout(displays_layout)

            # Add weights section
            self.weights_group = QGroupBox("Component Weights")
            weights_layout = QVBoxLayout(self.weights_group)
            weight_widget = QWidget()
            weight_layout = QHBoxLayout(weight_widget)
            
            self.weight1_label = QLabel("Magnitude:")
            self.weight2_label = QLabel("Phase:")
            
            self.weight1_slider = QSlider(Qt.Horizontal)
            self.weight1_slider.setRange(0, 100)
            self.weight1_slider.setValue(50)

            self.weight2_slider = QSlider(Qt.Horizontal)
            self.weight2_slider.setRange(0, 100)
            self.weight2_slider.setValue(50)

            weight_layout.addWidget(self.weight1_label)
            weight_layout.addWidget(self.weight1_slider)
            weight_layout.addWidget(self.weight2_label)
            weight_layout.addWidget(self.weight2_slider)
            
            weights_layout.addWidget(weight_widget)
            layout.addWidget(self.weights_group)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.hide()
        layout.addWidget(self.progress)

        # Add output port selector (for input viewers)
        # if not self.is_output:
        #     port_selector = QComboBox()
        #     port_selector.addItems(["Output 1", "Output 2"])
        #     header_layout.addWidget(port_selector)

    def update_weight_labels(self, mode):
        if mode == "Magnitude/Phase":
            self.weight1_label.setText("Magnitude:")
            self.weight2_label.setText("Phase:")
        else:
            self.weight1_label.setText("Real:")
            self.weight2_label.setText("Imaginary:")

    def _setup_animations(self):
        self.highlight_animation = QPropertyAnimation(self, b"styleSheet")
        self.highlight_animation.setDuration(300)
        self.highlight_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def highlight(self):
        self.highlight_animation.setStartValue(f"""
            QFrame#imageViewer {{
                background: {COLORS['background']};
                border: 1px solid {COLORS['border']};
            }}
        """)
        self.highlight_animation.setEndValue(f"""
            QFrame#imageViewer {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['primary']};
            }}
        """)
        self.highlight_animation.start()

    def reset(self):
        self.image = None
        self.ft_components = None
        self.brightness = 0
        self.contrast = 1
        self.originalImageLabel.clear()
        if not self.is_output:
            self.ftComponentLabel.clear()
            self.weight1_slider.setValue(50)
            self.weight2_slider.setValue(50)

    def _setup_zoom_controls(self):
        zoom_layout = QHBoxLayout()
        
        zoom_out = QPushButton("-")
        zoom_out.setFixedSize(24, 24)
        zoom_out.clicked.connect(partial(self.adjust_zoom, -0.1))
        
        self.zoom_label = QLabel("100%")
        self.zoom_label.setFixedWidth(50)
        
        zoom_in = QPushButton("+")
        zoom_in.setFixedSize(24, 24)
        zoom_in.clicked.connect(partial(self.adjust_zoom, 0.1))
        
        zoom_layout.addWidget(zoom_out)
        zoom_layout.addWidget(self.zoom_label)
        zoom_layout.addWidget(zoom_in)
        
        self.layout().addLayout(zoom_layout)

    def adjust_zoom(self, delta):
        self.zoom_level = max(0.1, min(5.0, self.zoom_level + delta))
        self.zoom_label.setText(f"{int(self.zoom_level * 100)}%")
        self.update_display()

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y() / 1200
            self.adjust_zoom(delta)
            event.accept()
        else:
            super().wheelEvent(event)

    def update_display(self):
        if self.image:
            scaled_size = self.image.size() * self.zoom_level
            self.originalImageLabel.setPixmap(self.image.scaled(
                scaled_size.toSize(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

class ImageDisplay(QLabel):
    # Add custom signal
    dragComplete = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.last_pos = None
        self.setToolTip("Drag & Drop images here\nDrag mouse to adjust brightness/contrast")
        self.loading_spinner = None
        self._setup_loading_spinner()
        self.setAcceptDrops(True)
        self.drop_indicator = QLabel(self)
        self.drop_indicator.hide()
        self._setup_drop_indicator()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_pos = event.pos()
            
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.last_pos:
            # Vertical movement controls brightness
            delta_y = event.pos().y() - self.last_pos.y()
            # Horizontal movement controls contrast
            delta_x = event.pos().x() - self.last_pos.x()
            
            self.parent().adjust_brightness_contrast(delta_y/100, delta_x/100)
            self.last_pos = event.pos()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_pos = None
            # Emit signal when drag is complete
            self.dragComplete.emit()

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        self.hide_drop_indicator()
        if event.mimeData().hasImage():
            self.setPixmap(QPixmap.fromImage(event.mimeData().imageData()))
        elif event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.setPixmap(QPixmap(file_path))
    
    def _setup_loading_spinner(self):
        self.loading_spinner = QProgressIndicator(self)
        self.loading_spinner.hide()
        
    def showLoadingSpinner(self):
        if self.loading_spinner:
            self.loading_spinner.start()
            self.loading_spinner.show()
    
    def hideLoadingSpinner(self):
        if self.loading_spinner:
            self.loading_spinner.stop()
            self.loading_spinner.hide()

    def _setup_drop_indicator(self):
        self.drop_indicator.setStyleSheet(f"""
            QLabel {{
                background: {COLORS['info']};
                color: white;
                padding: 10px;
                border-radius: 5px;
            }}
        """)
        self.drop_indicator.setText("Drop image here")
        self.drop_indicator.setAlignment(Qt.AlignCenter)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage() or event.mimeData().hasUrls():
            event.accept()
            self.show_drop_indicator()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.hide_drop_indicator()

    def show_drop_indicator(self):
        if self.drop_indicator:
            self.drop_indicator.show()
            # Center the indicator
            self.drop_indicator.move(
                (self.width() - self.drop_indicator.width()) // 2,
                (self.height() - self.drop_indicator.height()) // 2
            )

    def hide_drop_indicator(self):
        if self.drop_indicator:
            self.drop_indicator.hide()

class MainController:
    def __init__(self, window):
        self.window = window
        self.current_thread = None
        #self.setup_connections()

# Add a custom loading spinner widget
class QProgressIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.setFixedSize(40, 40)

    def rotate(self):
        self.angle = (self.angle + 30) % 360
        self.update()

    def start(self):
        self.timer.start(100)

    def stop(self):
        self.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(self.angle)
        
        painter.setPen(QPen(QColor(COLORS['primary']), 3))
        painter.drawArc(-15, -15, 30, 30, 0, 300 * 16)

class InfoButton(QPushButton):
    def __init__(self, tooltip, parent=None):
        super().__init__("ⓘ", parent)
        self.setToolTip(tooltip)
        self.setFixedSize(16, 16)
        self.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['info']};
                border-radius: 8px;
                color: white;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background: {COLORS['primary']};
            }}
        """)

# Add custom QSlider with value tooltip
class SliderWithTooltip(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        value = self.value_at_pos(event.pos())
        QToolTip.showText(event.globalPos(), str(value), self)
        super().mouseMoveEvent(event)

    def value_at_pos(self, pos):
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        groove = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self)
        handle = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self)

        if self.orientation() == Qt.Horizontal:
            slider_length = handle.width()
            slider_min = groove.x()
            slider_max = groove.right() - slider_length + 1
            pos = pos.x()
        else:
            slider_length = handle.height()
            slider_min = groove.y()
            slider_max = groove.bottom() - slider_length + 1
            pos = pos.y()

        return QStyle.sliderValueFromPosition(
            self.minimum(), self.maximum(), pos - slider_min,
            slider_max - slider_min, opt.upsideDown)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.controller = MainController(window)  # Set controller after window creation
    window.show()
    sys.exit(app.exec_())
