from scipy.interpolate import CubicSpline
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QListWidget, QHBoxLayout, QFileDialog, QPushButton , QComboBox, QDialog, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QDoubleValidator
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import pyqtSignal
import csv
import os
from datetime import datetime
from collections import deque
from dataclasses import dataclass
from typing import List, Any
from Mixer_functions import handle_component_button, delete_signal, select_signal, update_signal_real_time, undo, redo, update_undo_redo_buttons, update_plot, generate_signal, on_parameter_changed, select_example, open_examples_dialog



class Mixer(QtWidgets.QWidget):

    signalGenerated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.undo_stack = deque(maxlen=20)  # Limit stack size
        self.redo_stack = deque(maxlen=20)
        self.setupUi()
        self.setStyleSheet("background-color: #343a40;")
        self.signals = []
        self.signal_properties = []  # Store signal properties
        self.selected_signal_index = -1
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: update_plot(self,False))
        self.timer.start(100)


        self.is_previewing = False
        self.preview_signal = None
        self.preview_params = {
            'amplitude': 0,
            'frequency': 0,
            'phase': 0,
            'signal_type': 'sine'
        }
        
        # Set up initial signal and add to list
        self.lineEdit.setText("1")
        self.lineEdit_2.setText("1")
        self.lineEdit_4.setText("0")
        self.comboBox.setCurrentIndex(0)
        handle_component_button(self)
        
        

    def setupUi(self):
        self.setObjectName("Mixer")
        self.setWindowTitle("Signal Mixer / Composer")
        self.resize(1600, 900)

        # Main horizontal layout
        self.mainLayout = QtWidgets.QHBoxLayout(self)
        self.mainLayout.setSpacing(20)

        # Left control panel
        self.leftPanel = QtWidgets.QWidget()
        self.leftPanel.setFixedWidth(400)
        self.leftLayout = QtWidgets.QVBoxLayout(self.leftPanel)
        
        # Signal parameters group
        self.paramGroup = QtWidgets.QGroupBox("Signal Parameters")
        self.paramGroup.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: white;
                border: 2px solid white;
                border-radius: 10px;
                padding: 15px;
                margin-top: 15px;
            }
        """)
        
        self.paramLayout = QtWidgets.QFormLayout(self.paramGroup)
        self.paramLayout.setSpacing(15)

        # Add parameters
        self.comboBox = self.createComboBox(["Sin", "Cos"])
        self.lineEdit = self.createLineEdit("0", QDoubleValidator(0.0, 100.0, 2))
        self.lineEdit_2 = self.createLineEdit("0", QDoubleValidator(0.0, 50.0, 2))
        self.lineEdit_3 = self.createLineEdit("untitled")
        self.lineEdit_4 = self.createLineEdit("0", QDoubleValidator(0.0, 360.0, 2))

        self.paramLayout.addRow(self.createLabel("Type:"), self.comboBox)
        self.paramLayout.addRow(self.createLabel("Amplitude:"), self.lineEdit)
        self.paramLayout.addRow(self.createLabel("Frequency:"), self.lineEdit_2)
        self.paramLayout.addRow(self.createLabel("Name:"), self.lineEdit_3)
        self.paramLayout.addRow(self.createLabel("Phase Shift:"), self.lineEdit_4)

        # Buttons group
        self.buttonGroup = QtWidgets.QWidget()
        self.buttonLayout = QtWidgets.QVBoxLayout(self.buttonGroup)
        self.buttonLayout.setSpacing(10)

        self.addComponent = self.createButton("Add Component")
        self.deleteComponent = self.createButton("Delete Component")
        self.buttonLayout.addWidget(self.addComponent)
        self.buttonLayout.addWidget(self.deleteComponent)

        # Signal list
        self.listWidget = QListWidget()
        self.listWidget.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                background-color: #000000;
                color: #ffffff;
                border: 2px solid #ffffff;
                border-radius: 10px;
                padding: 10px;
                min-height: 400px;
            }
            QListWidget::item {
                padding: 5px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #5a5a5a;
                border-radius: 5px;
            }
        """)

        # Start sampling button
        self.startSampling = self.createButton("Start Sampling")
        
        # Add all components to left panel
        self.leftLayout.addWidget(self.paramGroup)
        self.leftLayout.addWidget(self.buttonGroup)
        self.leftLayout.addWidget(self.listWidget)
        self.leftLayout.addWidget(self.startSampling)

        self.examples_button =  self.createButton("Examples")
        self.examples_button.clicked.connect(lambda: open_examples_dialog(self, True))
        self.leftLayout.addWidget(self.examples_button)


        # Right panel (graph)
        self.rightPanel = QtWidgets.QWidget()
        self.rightLayout = QtWidgets.QVBoxLayout(self.rightPanel)
        
        self.signalViewer = pg.PlotWidget(title="Signal Mixer")
        self.signalViewer.setBackground('#000000')
        self.signalViewer.getAxis('left').setPen('w')
        self.signalViewer.getAxis('bottom').setPen('w')
        self.signalViewer.showGrid(x=True, y=True)
        self.signalViewer.setMinimumWidth(1000)
        
        self.rightLayout.addWidget(self.signalViewer)

        # Add panels to main layout
        self.mainLayout.addWidget(self.leftPanel)
        self.mainLayout.addWidget(self.rightPanel)

        # Connect signals
        self.connectSignals()
        
        # Set global style
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
            }
            
            QLineEdit {
                padding: 8px;
                background-color: #363636;
                border: 1px solid #444444;
                border-radius: 4px;
                color: #ffffff;
            }
            
            QLineEdit:focus {
                border: 1px solid #0078d4;
            }
            
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #1084d8;
            }
            
            QPushButton:pressed {
                background-color: #006cbd;
            }
            
            QComboBox {
                padding: 8px;
                background-color: #363636;
                border: 1px solid #444444;
                border-radius: 4px;
                color: #ffffff;
            }
            
            QComboBox:drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            
            QLabel {
                color: #e0e0e0;
                font-size: 11pt;
            }
            
            QListWidget {
                background-color: #363636;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
            }
            
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            
            QListWidget::item:hover {
                background-color: #404040;
            }
        """)


        self.undo_button = QPushButton("↶ Undo")
        self.redo_button = QPushButton("↷ Redo")
        
        # Define button styles
        enabled_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """
        
        disabled_style = """
            QPushButton {
                background-color: #cccccc;
                color: #666666;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
            }
        """
        
        self.undo_button.setStyleSheet(disabled_style)
        self.redo_button.setStyleSheet(disabled_style)

        # Add tooltips
        self.comboBox.setToolTip("Select the type of waveform to generate")
        self.lineEdit.setToolTip("Enter amplitude value (0-100)")
        self.lineEdit_2.setToolTip("Enter frequency value (0-50 Hz)")
        self.lineEdit_3.setToolTip("Enter a name for your signal")
        self.lineEdit_4.setToolTip("Enter phase shift value (0-360 degrees)")
        
        # Add keyboard shortcuts
        self.addComponent.setShortcut("Ctrl+A")  
        self.deleteComponent.setShortcut("Delete")
        self.undo_button.setShortcut("Ctrl+Z")
        self.redo_button.setShortcut("Ctrl+Y")
        
        # Add preview labels
        self.previewLabel = QLabel("Signal Preview")
        self.previewLabel.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                padding: 5px;
            }
        """)
        self.rightLayout.insertWidget(0, self.previewLabel)
        
        # Reorganize buttons into action groups
        self.actionGroup = QtWidgets.QWidget()
        self.actionLayout = QtWidgets.QHBoxLayout(self.actionGroup)
        
        # Create button groups
        self.editGroup = QtWidgets.QWidget()
        self.editLayout = QtWidgets.QHBoxLayout(self.editGroup)
        self.editLayout.addWidget(self.undo_button)
        self.editLayout.addWidget(self.redo_button)
        
        self.signalGroup = QtWidgets.QWidget()
        self.signalLayout = QtWidgets.QHBoxLayout(self.signalGroup)
        self.signalLayout.addWidget(self.addComponent) 
        self.signalLayout.addWidget(self.deleteComponent)
        
        # Update styles for better visual hierarchy
        self.paramGroup.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: white;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 15px;
                margin-top: 20px;
            }
        """)
        
        self.listWidget.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 10px;
                min-height: 300px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #4CAF50;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
        """)
        
        # Update button layout
        self.buttonLayout.addWidget(self.editGroup)
        self.buttonLayout.addWidget(self.signalGroup)
        self.buttonLayout.addWidget(self.startSampling)
        
        # Add status bar
        self.statusBar = QLabel()
        self.statusBar.setStyleSheet("""
            QLabel {
                color: #90CAF9;
                padding: 5px;
                font-size: 12px;
            }
        """)
        self.leftLayout.addWidget(self.statusBar)
        
        # Store styles for later use
        self.button_styles = {
            'enabled': enabled_style,
            'disabled': disabled_style
        }

        self.undo_button.clicked.connect(lambda: undo(self))
        self.redo_button.clicked.connect(lambda: redo(self))
        self.buttonLayout.addWidget(self.undo_button)
        self.buttonLayout.addWidget(self.redo_button)
        
        update_undo_redo_buttons(self)


        self.lineEdit.textChanged.connect(lambda: on_parameter_changed(self))
        self.lineEdit_2.textChanged.connect(lambda: on_parameter_changed(self))
        self.lineEdit_4.textChanged.connect(lambda: on_parameter_changed(self))
        self.comboBox.currentTextChanged.connect(lambda: on_parameter_changed(self))

    

    def createLabel(self, text):
        label = QtWidgets.QLabel(text)
        label.setStyleSheet("font-size: 14px; font-weight: bold; color: white;")
        return label

    def createLineEdit(self, default_text, validator=None):
        lineEdit = QtWidgets.QLineEdit()
        lineEdit.setText(default_text)
        if validator:
            lineEdit.setValidator(validator)
        lineEdit.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                background-color: #000000;
                color: white;
                border: 1px solid white;
                border-radius: 5px;
                padding: 8px;
            }
        """)
        return lineEdit

    def createComboBox(self, items):
        comboBox = QtWidgets.QComboBox()
        comboBox.addItems(items)
        comboBox.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                background-color: #000000;
                color: white;
                border: 1px solid white;
                border-radius: 5px;
                padding: 8px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
        """)
        return comboBox

    def createButton(self, text):
        button = QtWidgets.QPushButton(text)
        button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                background-color: #000000;
                color: white;
                border: 2px solid white;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
        """)
        return button

    def connectSignals(self):
        self.addComponent.clicked.connect(lambda: handle_component_button(self,False))
        self.deleteComponent.clicked.connect(lambda: delete_signal(self,True))
        self.listWidget.itemClicked.connect(lambda: select_signal(self))
        
        self.lineEdit.textChanged.connect(lambda: update_signal_real_time(self,1))
        self.lineEdit_2.textChanged.connect(lambda: update_signal_real_time(self,2))
        self.lineEdit_4.textChanged.connect(lambda: update_signal_real_time(self,3))
        self.comboBox.currentTextChanged.connect(lambda: update_signal_real_time(self,4))

        

    def generate_filename(self, signal_properties):
        # Calculate total amplitude, frequency and phase
        total_amplitude = sum(prop['amplitude'] for prop in signal_properties)
        # Take max frequency since that's more meaningful for combined signals
        max_frequency = max(prop['frequency'] for prop in signal_properties)
        # Take average phase shift
        avg_phase = sum(prop['phase_shift'] for prop in signal_properties) / len(signal_properties)
        
        # Format combined signal parameters
        amp = f"{total_amplitude:.1f}A"
        freq = f"{max_frequency:.1f}Hz"
        phase = f"{avg_phase:.1f}deg"
        
        # Combine into filename
        filename = f"signal_{amp}_{freq}_{phase}.csv"
        # Clean filename of invalid characters
        filename = "".join(c for c in filename if c.isalnum() or c in '._-')
        
        return filename

    

    def clear_data(self):
        self.signals.clear()
        self.listWidget.clear()
        update_plot(self)

    def emit_signals(self, file_path):
        self.signalGenerated.emit(file_path)
        

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("Form", "Type"))
        self.label_2.setText(_translate("Form", "Amplitude"))
        self.comboBox.setItemText(0, _translate("Form", "Sin"))
        self.comboBox.setItemText(1, _translate("Form", "Cos"))
        self.lineEdit.setText(_translate("Form", "0"))
        self.label_3.setText(_translate("Form", "Frequency"))
        self.label_4.setText(_translate("Form", "Signal Name"))
        self.label_5.setText(_translate("Form", "Phase Shift"))
        self.lineEdit_2.setText(_translate("Form", "0"))
        self.lineEdit_3.setText(_translate("Form", "untitled"))
        self.lineEdit_4.setText(_translate("Form", "0"))
        self.addComponent.setText(_translate("Form", "Add Component"))
        self.startSampling.setText(_translate("Form", "Start Sampling"))
        self.deleteComponent.setText(_translate("Form", "Delete Component"))

    

    



    def save_signals_to_csv(self, file_path):
        combined_signal = np.sum(self.signals, axis=0)
        t = np.linspace(0, 1, len(combined_signal), endpoint=False)
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["time", "voltage"])
            for time, voltage in zip(t, combined_signal):
                writer.writerow([time, voltage])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mixer = Mixer()
    mixer.show()
    sys.exit(app.exec_())
