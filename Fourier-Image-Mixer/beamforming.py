import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import json
from matplotlib import style
import matplotlib as mpl
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum

@dataclass
class ArrayUnit:
    id: int
    x_pos: float  # Center position
    y_pos: float
    num_elements: int
    element_spacing: float
    steering_angle: float
    geometry_type: str
    curvature: float
    operating_freq: float
    phase_shift: float
    enabled: bool = True

class ScenarioType(Enum):
    FiveG = "5G Communications"
    ULTRASOUND = "Medical Ultrasound"
    ABLATION = "Tumor Ablation"

# Add this constant after STYLE_SHEET
PLOT_STYLE = {
    'axes.labelcolor': 'white',
    'axes.edgecolor': 'white',
    'text.color': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'grid.color': '#404040',
    'figure.facecolor': '#1e1e1e',
    'axes.facecolor': '#2d2d2d',
}


STYLE_SHEET = """
QMainWindow {
    background-color: #1e1e1e;
    color: #ffffff;
}
QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
}
QGroupBox {
    border: 2px solid #3a3a3a;
    border-radius: 5px;
    margin-top: 1em;
    padding-top: 10px;
    color: #ffffff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}
QLabel {
    color: #ffffff;
}
QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #3a3a3a;
    border-radius: 3px;
    color: #ffffff;
    padding: 5px;
}
QPushButton {
    background-color: #0d47a1;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    text-align: center;
}
QPushButton:hover {
    background-color: #1565c0;
}
QPushButton:pressed {
    background-color: #0a3d91;
}
QDockWidget {
    border: 1px solid #3a3a3a;
    titlebar-close-icon: url(close.png);
}
QDockWidget::title {
    text-align: left;
    background: #2d2d2d;
    padding-left: 5px;
    height: 25px;
}
QMenuBar {
    background-color: #2d2d2d;
    color: white;
}
QMenuBar::item {
    spacing: 3px;
    padding: 5px 10px;
    background: transparent;
}
QMenuBar::item:selected {
    background: #3a3a3a;
}
"""

STYLE_SHEET += """
QDoubleSpinBox::up-button, QSpinBox::up-button {
    border-radius: 3px;
}
QDoubleSpinBox::down-button, QSpinBox::down-button {
    border-radius: 3px;
}
QToolTip {
    background-color: #2d2d2d;
    color: white;
    border: 1px solid #3a3a3a;
    padding: 5px;
}
QGroupBox {
    background-color: #252525;
    border-radius: 8px;
    margin-top: 1.5em;
}
"""

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(35)
        self.setCursor(Qt.PointingHandCursor)
        style.use('dark_background')
        mpl.rcParams.update(PLOT_STYLE)

class BeamformingSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2D Beamforming Simulator")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(STYLE_SHEET)
        
        # Initialize field variables
        self.x_field = np.linspace(-10, 10, 200)
        self.y_field = np.linspace(0, 20, 200)
        self.X, self.Y = np.meshgrid(self.x_field, self.y_field)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
        # Create widgets
        self.create_control_panel()
        self.create_visualization_area()
        self.create_menu_bar()

        self.array_units: List[ArrayUnit] = []
        self.current_unit_id = 0
        self.setup_preset_scenarios()
        
    def create_control_panel(self):
        control_dock = QDockWidget("Parameters", self)
        control_dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        control_layout.setSpacing(15)
        
        # Array parameters
        array_group = QGroupBox("Array Parameters")
        array_layout = QFormLayout()
        array_layout.setSpacing(10)
        
        self.num_elements = QSpinBox()
        self.num_elements.setRange(1, 128)
        self.num_elements.setValue(16)
        array_layout.addRow("Number of Elements:", self.num_elements)
        
        self.element_spacing = QDoubleSpinBox()
        self.element_spacing.setRange(0.1, 10.0)
        self.element_spacing.setValue(0.5)
        array_layout.addRow("Element Spacing (λ):", self.element_spacing)
        
        self.steering_angle = QDoubleSpinBox()
        self.steering_angle.setRange(-90, 90)
        self.steering_angle.setValue(0)
        array_layout.addRow("Steering Angle (°):", self.steering_angle)
        
        array_group.setLayout(array_layout)
        control_layout.addWidget(array_group)
        
        # Geometry parameters
        geometry_group = QGroupBox("Array Geometry")
        geometry_layout = QFormLayout()
        geometry_layout.setSpacing(10)
        
        self.geometry_type = QComboBox()
        self.geometry_type.addItems(["Linear", "Curved"])
        geometry_layout.addRow("Array Type:", self.geometry_type)
        
        self.curvature = QDoubleSpinBox()
        self.curvature.setRange(0, 360)
        self.curvature.setValue(0)
        geometry_layout.addRow("Curvature (°):", self.curvature)
        
        geometry_group.setLayout(geometry_layout)
        control_layout.addWidget(geometry_group)
        
        # Frequency parameters
        freq_group = QGroupBox("Frequency Settings")
        freq_layout = QFormLayout()
        freq_layout.setSpacing(10)
        
        self.freq = QDoubleSpinBox()
        self.freq.setRange(1, 1000)
        self.freq.setValue(100)
        freq_layout.addRow("Frequency (MHz):", self.freq)
        
        freq_group.setLayout(freq_layout)
        control_layout.addWidget(freq_group)
        
        # Add update button
        update_button = ModernButton("Update Pattern")
        update_button.clicked.connect(self.update_pattern)
        control_layout.addWidget(update_button)
        
        control_layout.addStretch()
        control_widget.setLayout(control_layout)
        control_dock.setWidget(control_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, control_dock)

        # Add tooltips
        self.num_elements.setToolTip("Number of array elements (1-128)")
        self.element_spacing.setToolTip("Spacing between elements in wavelengths")
        self.steering_angle.setToolTip("Beam steering angle in degrees")
        self.curvature.setToolTip("Array curvature angle for curved arrays")
        
        # Enhance spinboxes
        for spinbox in [self.num_elements, self.element_spacing, self.steering_angle, self.curvature, self.freq]:
            spinbox.setFixedHeight(30)
            spinbox.setAlignment(Qt.AlignCenter)
            
        # Add value changed connections for real-time updates
        self.num_elements.valueChanged.connect(self.update_pattern)
        self.element_spacing.valueChanged.connect(self.update_pattern)
        self.steering_angle.valueChanged.connect(self.update_pattern)
        self.geometry_type.currentTextChanged.connect(self.update_pattern)
        self.curvature.valueChanged.connect(self.update_pattern)
        
    def create_visualization_area(self):
        viz_widget = QWidget()
        viz_layout = QVBoxLayout()
        viz_layout.setSpacing(10)
        
        # Set dark background for matplotlib
        plt.style.use('dark_background')
        
        # Create matplotlib figures
        self.pattern_fig = Figure(figsize=(8, 5))
        self.pattern_fig.patch.set_facecolor('#1e1e1e')
        self.pattern_canvas = FigureCanvasQTAgg(self.pattern_fig)
        viz_layout.addWidget(self.pattern_canvas)
        
        self.array_fig = Figure(figsize=(8, 3))
        self.array_fig.patch.set_facecolor('#1e1e1e')
        self.array_canvas = FigureCanvasQTAgg(self.array_fig)
        viz_layout.addWidget(self.array_canvas)
        
        viz_widget.setLayout(viz_layout)
        self.layout.addWidget(viz_widget)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        
        load_scenario = QAction("Load Scenario", self)
        load_scenario.setShortcut("Ctrl+O")
        load_scenario.triggered.connect(self.load_scenario)
        file_menu.addAction(load_scenario)
        
        save_scenario = QAction("Save Scenario", self)
        save_scenario.setShortcut("Ctrl+S")
        save_scenario.triggered.connect(self.save_scenario)
        file_menu.addAction(save_scenario)

        scenario_menu = self.menuBar().addMenu("Scenarios")
        
        for scenario_type in ScenarioType:
            action = QAction(scenario_type.value, self)
            action.triggered.connect(
                lambda checked, st=scenario_type: self.load_preset_scenario(st)
            )
            scenario_menu.addAction(action)
        
    def create_visualization_area(self):
        viz_widget = QWidget()
        viz_layout = QVBoxLayout()
        viz_layout.setSpacing(10)
        
        # Create horizontal layout for side-by-side plots
        plot_layout = QHBoxLayout()
        
        # Left side - Pattern and Array plots
        left_plots = QVBoxLayout()
        
        # Beam pattern plot
        self.pattern_fig = Figure(figsize=(6, 4))
        self.pattern_fig.patch.set_facecolor('#1e1e1e')
        self.pattern_canvas = FigureCanvasQTAgg(self.pattern_fig)
        left_plots.addWidget(self.pattern_canvas)
        
        # Array geometry plot
        self.array_fig = Figure(figsize=(6, 2))
        self.array_fig.patch.set_facecolor('#1e1e1e')
        self.array_canvas = FigureCanvasQTAgg(self.array_fig)
        left_plots.addWidget(self.array_canvas)
        
        plot_layout.addLayout(left_plots)
        
        # Right side - Interference map
        self.interference_fig = Figure(figsize=(6, 6))
        self.interference_fig.patch.set_facecolor('#1e1e1e')
        self.interference_canvas = FigureCanvasQTAgg(self.interference_fig)
        plot_layout.addWidget(self.interference_canvas)
        
        viz_layout.addLayout(plot_layout)
        viz_widget.setLayout(viz_layout)
        self.layout.addWidget(viz_widget)

    def update_pattern(self):
        if not self.array_units:
            # If no array units, use current parameters
            unit = ArrayUnit(
                id=-1,
                x_pos=0,
                y_pos=0,
                num_elements=self.num_elements.value(),
                element_spacing=self.element_spacing.value(),
                steering_angle=self.steering_angle.value(),
                geometry_type=self.geometry_type.currentText(),
                curvature=self.curvature.value(),
                operating_freq=self.freq.value(),
                phase_shift=0
            )
            self.calculate_single_pattern(unit)
        else:
            # Calculate combined pattern for all units
            self.calculate_combined_pattern()

    def calculate_single_pattern(self, unit):
        k = 2 * np.pi  # wavenumber (normalized wavelength)
        
        # Create array geometry
        x, y = self.calculate_array_geometry(unit)
        
        # Calculate beam pattern (polar)
        theta = np.linspace(-np.pi/2, np.pi/2, 1000)
        pattern = np.zeros_like(theta)
        theta_steer = np.radians(unit.steering_angle)
        
        for i in range(len(theta)):
            phase = k * (x * np.sin(theta[i]) + y * np.cos(theta[i]))
            steer_phase = k * x * np.sin(theta_steer)
            pattern[i] = np.abs(np.sum(np.exp(1j * (phase - steer_phase))))
        
        pattern = pattern / np.max(pattern)
        
        # Calculate interference map
        interference = np.zeros_like(self.X, dtype=np.complex128)
        
        for i in range(len(x)):
            r = np.sqrt((self.X - x[i])**2 + (self.Y - y[i])**2)
            phase = k * r
            steer_phase = k * x[i] * np.sin(theta_steer)
            interference += np.exp(1j * (phase - steer_phase))
        
        interference = np.abs(interference)
        interference = interference / np.max(interference)
        
        # Update visualizations
        self.update_pattern_plot(theta, pattern)
        self.update_array_plot(x, y)
        self.update_interference_plot(self.x_field, self.y_field, interference)

    def calculate_array_geometry(self, unit):
        if unit.geometry_type == "Linear":
            x = (np.arange(unit.num_elements) - unit.num_elements/2) * unit.element_spacing + unit.x_pos
            y = np.zeros_like(x) + unit.y_pos
        else:
            radius = 10
            arc_angle = np.radians(unit.curvature)
            angles = np.linspace(-arc_angle/2, arc_angle/2, unit.num_elements)
            x = radius * np.sin(angles) + unit.x_pos
            y = radius * (1 - np.cos(angles)) + unit.y_pos
        return x, y

    def calculate_combined_pattern(self):
        k = 2 * np.pi
        theta = np.linspace(-np.pi/2, np.pi/2, 1000)
        pattern = np.zeros_like(theta, dtype=np.complex128)
        interference = np.zeros_like(self.X, dtype=np.complex128)
        
        all_x = []
        all_y = []
        
        for unit in self.array_units:
            if not unit.enabled:
                continue
                
            x, y = self.calculate_array_geometry(unit)
            all_x.extend(x)
            all_y.extend(y)
            theta_steer = np.radians(unit.steering_angle)
            
            # Add to beam pattern
            for i in range(len(theta)):
                phase = k * (x * np.sin(theta[i]) + y * np.cos(theta[i]))
                steer_phase = k * x * np.sin(theta_steer)
                pattern[i] += np.sum(np.exp(1j * (phase - steer_phase)))
            
            # Add to interference map
            for i in range(len(x)):
                r = np.sqrt((self.X - x[i])**2 + (self.Y - y[i])**2)
                phase = k * r
                steer_phase = k * x[i] * np.sin(theta_steer)
                interference += np.exp(1j * (phase - steer_phase))
        
        pattern = np.abs(pattern)
        pattern = pattern / np.max(pattern)
        
        interference = np.abs(interference)
        interference = interference / np.max(interference)
        
        # Update visualizations
        self.update_pattern_plot(theta, pattern)
        self.update_array_plot(np.array(all_x), np.array(all_y))
        self.update_interference_plot(self.x_field, self.y_field, interference)
        
    def update_interference_plot(self, x, y, interference):
        self.interference_fig.clear()
        ax = self.interference_fig.add_subplot(111)
        im = ax.imshow(interference, 
                    extent=[x.min(), x.max(), y.min(), y.max()],
                    origin='lower',
                    cmap='RdBu_r',
                    aspect='equal')
        ax.set_title('Interference Pattern', color='white', pad=10)
        ax.set_xlabel('X Position (λ)', color='white')
        ax.set_ylabel('Y Position (λ)', color='white')
        
        # Enhance colorbar
        cbar = self.interference_fig.colorbar(im, label='Normalized Amplitude')
        cbar.ax.yaxis.label.set_color('white')
        cbar.ax.tick_params(colors='white')
        
        self.interference_canvas.draw()
        
    def update_pattern_plot(self, theta, pattern):
        self.pattern_fig.clear()
        ax = self.pattern_fig.add_subplot(111, projection='polar')
        ax.plot(theta, pattern, color='#2196f3', linewidth=2)
        ax.set_title('Beam Pattern', color='white', pad=10)
        ax.grid(True, color='#404040', alpha=0.5)
        
        # Enhance tick labels
        ax.tick_params(colors='white')
        
        self.pattern_canvas.draw()
        
    def update_array_plot(self, x, y):
        self.array_fig.clear()
        ax = self.array_fig.add_subplot(111)
        ax.scatter(x, y, c='#2196f3', marker='o', s=100)
        ax.set_title('Array Geometry', color='white', pad=10)
        ax.set_xlabel('X Position (λ)', color='white')
        ax.set_ylabel('Y Position (λ)', color='white')
        ax.grid(True, color='#404040', alpha=0.5)
        
        # Add element numbers
        for i, (xi, yi) in enumerate(zip(x, y)):
            ax.annotate(f'{i+1}', (xi, yi), 
                       xytext=(0, 10), 
                       textcoords='offset points',
                       ha='center',
                       color='white')
        
        self.array_canvas.draw()
        
    def save_scenario(self):
        params = {
            'num_elements': self.num_elements.value(),
            'element_spacing': self.element_spacing.value(),
            'steering_angle': self.steering_angle.value(),
            'geometry_type': self.geometry_type.currentText(),
            'curvature': self.curvature.value(),
            'frequency': self.freq.value()
        }
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Scenario",
            "",
            "JSON Files (*.json)"
        )
        
        if filename:
            with open(filename, 'w') as f:
                json.dump(params, f, indent=4)
                
    def load_scenario(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Scenario",
            "",
            "JSON Files (*.json)"
        )
        
        if filename:
            with open(filename, 'r') as f:
                params = json.load(f)
                
            self.num_elements.setValue(params['num_elements'])
            self.element_spacing.setValue(params['element_spacing'])
            self.steering_angle.setValue(params['steering_angle'])
            self.geometry_type.setCurrentText(params['geometry_type'])
            self.curvature.setValue(params['curvature'])
            self.freq.setValue(params['frequency'])
            
            # Update visualization
            self.update_pattern()

    def load_preset_scenario(self, scenario_type: ScenarioType):
        scenario = self.scenarios[scenario_type]
        self.array_units.clear()
        
        for unit_params in scenario["params"]["units"]:
            unit = ArrayUnit(
                id=self.current_unit_id,
                **unit_params
            )
            self.array_units.append(unit)
            self.current_unit_id += 1
            
        self.update_pattern()

    def setup_preset_scenarios(self):
        self.scenarios = {
            ScenarioType.FiveG: {
                "description": "5G Beamforming Array (28 GHz)",
                "params": {
                    "units": [
                        {
                            "num_elements": 64,
                            "element_spacing": 0.5,
                            "steering_angle": 0,
                            "geometry_type": "Linear",
                            "curvature": 0,
                            "operating_freq": 28000,
                            "x_pos": 0,
                            "y_pos": 0,
                            "phase_shift": 0
                        }
                    ]
                }
            },
            ScenarioType.ULTRASOUND: {
                "description": "Medical Ultrasound Scanner (5 MHz)",
                "params": {
                    "units": [
                        {
                            "num_elements": 128,
                            "element_spacing": 0.25,
                            "steering_angle": 0,
                            "geometry_type": "Curved",
                            "curvature": 60,
                            "operating_freq": 5,
                            "x_pos": 0,
                            "y_pos": 0,
                            "phase_shift": 0
                        }
                    ]
                }
            },
            ScenarioType.ABLATION: {
                "description": "Focused Ultrasound Ablation (1 MHz)",
                "params": {
                    "units": [
                        {
                            "num_elements": 32,
                            "element_spacing": 1.0,
                            "steering_angle": -30,
                            "geometry_type": "Linear",
                            "curvature": 0,
                            "operating_freq": 1,
                            "x_pos": -5,
                            "y_pos": 0,
                            "phase_shift": 0
                        },
                        {
                            "num_elements": 32,
                            "element_spacing": 1.0,
                            "steering_angle": 30,
                            "geometry_type": "Linear",
                            "curvature": 0,
                            "operating_freq": 1,
                            "x_pos": 5,
                            "y_pos": 0,
                            "phase_shift": 0
                        }
                    ]
                }
            }
        }

    def add_array_unit(self):
        unit = ArrayUnit(
            id=self.current_unit_id,
            x_pos=0,
            y_pos=0,
            num_elements=self.num_elements.value(),
            element_spacing=self.element_spacing.value(),
            steering_angle=self.steering_angle.value(),
            geometry_type=self.geometry_type.currentText(),
            curvature=self.curvature.value(),
            operating_freq=self.freq.value(),
            phase_shift=0
        )
        self.array_units.append(unit)
        self.current_unit_id += 1
        self.update_pattern()

    def remove_array_unit(self, unit_id: int):
        self.array_units = [u for u in self.array_units if u.id != unit_id]
        self.update_pattern()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BeamformingSimulator()
    window.show()
    sys.exit(app.exec_())