from scipy.interpolate import CubicSpline
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider
from PyQt5.QtGui import QIcon , QFont, QPixmap, QColor # Package to set an icon , fonts and images
from PyQt5.QtCore import Qt , QTimer  # used for alignments.
from PyQt5.QtWidgets import QLayout , QVBoxLayout , QHBoxLayout, QGridLayout ,QWidget, QFileDialog, QPushButton, QColorDialog, QInputDialog, QComboBox, QDialog, QDoubleSpinBox
import pyqtgraph as pg
import random
import pandas as pd
from scipy.signal import find_peaks
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem
from scipy import signal
from Mixer import Mixer
import matplotlib.pyplot as plt
from Mixer_functions import handle_component_button, delete_signal, select_signal, update_signal_real_time, undo, redo, update_undo_redo_buttons, generate_signal, on_parameter_changed, update_plot, load_signals_from_json, select_example, open_examples_dialog
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from style import COLORS, BROWSE_BUTTON_STYLE, OPTIONS_GROUP_STYLE, SLIDER_STYLE, LIST_STYLE, COMBO_STYLE, MAIN_WINDOW_STYLE,LINE_EDIT_STYLE,BUTTON_STYLE
 

class Ui_MainWindow(QMainWindow):


    def __init__(self):
        super().__init__()
        with open ('signals.json', 'w') as file:
            file.write('{"signals":[],"properties":[]}')
        self.signals, self.signal_properties = load_signals_from_json()
        # add the signals to the list widget
        self.signalData = None
        self.copyData = None
        self.combined_signal = np.array([])  # Initialize as an empty array
        self.f_max = 0
        self.selected_signal_index = -1
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: update_plot(self, True, False))
        self.timer.start(100)

        self.loadedSignals = []
        self.samplingFrequency = 0
        self.samplingFactor= 0
        
        self.frequencyShape = "Pulses"
        self.samplingTimer = QTimer()
        self.samplingRate  = 7000 # Number of samples per second

        self.is_previewing = False
        self.preview_signal = None
        self.preview_params = {
            'amplitude': 0,
            'frequency': 0,
            'phase': 0,
            'signal_type': 'sine'
        }

        
        
        self.setupUi()
        self.setStyleSheet("background-color:#001523;color:white;")

        # Set up initial signal and add to list
        self.lineEdit.setText("50")
        self.lineEdit_2.setText("50")
        self.lineEdit_4.setText("0")
        self.comboBox.setCurrentIndex(0)
        handle_component_button(self, True)

        # append the default signal to the loaded signals
        self.mixer = Mixer()
        self.mixer.signalGenerated.connect(self.loadSignalFromFile)


        # Set default selection
        self.samplingType.setCurrentIndex(0)  # Select the first item by default

        self.selectedInterpolation = self.samplingType.currentText()  # Initialize with default value
        # Connecting the Combobox to an Event Handler
        self.samplingType.currentIndexChanged.connect(self.updateInterpolationMethod)

        self.setStyleSheet(MAIN_WINDOW_STYLE)


    def updateInterpolationMethod(self):
        self.selectedInterpolation = self.samplingType.currentText()
        self.startSampling(self.t_orig ,self.signalData)
   

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(1200, 950)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.setMinimumSize(900, 700)

        # Creating main horizontal layout
        self.mainLayout = QtWidgets.QHBoxLayout(self.centralwidget)

        # Add left control panel
        self.leftPanel = QtWidgets.QWidget()
        self.leftPanel.setMaximumWidth(400)
        self.leftLayout = QtWidgets.QVBoxLayout(self.leftPanel)


        # Browse File
        self.uploadIcon = QtGui.QIcon("Images/upload.png")
        self.browseFileButton = QtWidgets.QPushButton("Browse Signal",self.centralwidget)
        self.browseFileButton.setObjectName("pushButton")
        self.browseFileButton.setStyleSheet("""
            QPushButton{
                border: 3px solid #d1d1d1;
                border-radius: 10px;
                font-weight:normal;
                font-size:12px;             
                padding: 5px 5px;
                background-color:transparent;
                color:#d1d1d1;
                margin-left: 10px;
            }                                                
        """)
        
        self.browseFileButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.browseFileButton.setMinimumSize(40, 40)
        self.browseFileButton.clicked.connect(lambda: self.openFileDialog())
        self.leftLayout.addWidget(self.browseFileButton)
        self.browseFileButton.setIcon(self.uploadIcon)
        self.browseFileButton.setIconSize(QtCore.QSize(20, 20))
        
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

        # Add parameters
        self.comboBox = self.createComboBox(["Sin", "Cos"])
        self.lineEdit = self.createLineEdit("10", QtGui.QDoubleValidator(0.0, 100.0, 2))
        self.lineEdit_2 = self.createLineEdit("10", QtGui.QDoubleValidator(0.0, 50.0, 2))
        self.lineEdit_3 = self.createLineEdit("untitled")
        self.lineEdit_4 = self.createLineEdit("0", QtGui.QDoubleValidator(0.0, 360.0, 2))

        self.paramLayout.addRow(self.createLabel("Type:"), self.comboBox)
        self.paramLayout.addRow(self.createLabel("Amplitude:"), self.lineEdit)
        self.paramLayout.addRow(self.createLabel("Frequency:"), self.lineEdit_2)
        self.paramLayout.addRow(self.createLabel("Name:"), self.lineEdit_3)
        self.paramLayout.addRow(self.createLabel("Phase Shift:"), self.lineEdit_4)

        self.lineEdit.textChanged.connect(lambda: on_parameter_changed(self))
        self.lineEdit_2.textChanged.connect(lambda: on_parameter_changed(self))
        self.lineEdit_4.textChanged.connect(lambda: on_parameter_changed(self))
        self.comboBox.currentTextChanged.connect(lambda: on_parameter_changed(self))

        # Add buttons
        self.buttonGroup = QtWidgets.QWidget()
        self.buttonLayout = QtWidgets.QVBoxLayout(self.buttonGroup)
        self.addComponent = self.createButton("Add Component")
        self.deleteComponent = self.createButton("Delete Component")
        self.buttonLayout.addWidget(self.addComponent)
        self.buttonLayout.addWidget(self.deleteComponent)

        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setStyleSheet("""
            QListWidget {
                font-size: 14px;
                background-color: #001b2c;
                color: white;
                border: 3px solid white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.listWidget.setFixedHeight(200)  
        self.listWidget.setMaximumSize(400, 300)  

        self.listWidget.setSpacing(10)

        # Add left panel to main layout
        self.mainLayout.addWidget(self.leftPanel)


        self.optionsGroup = QtWidgets.QGroupBox()
        self.optionsGroup.setStyleSheet("""
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
        self.optionsGroup.setMinimumHeight(400)
        self.optionsLayout = QtWidgets.QFormLayout(self.optionsGroup)

        self.samplingType = self.createComboBox(["Whittaker", "Cubic Spline", "Zero-Order"])
        self.samplingType.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                background-color: transparent;
                color: white;
                border: 2px solid white;
                border-radius: 5px;
                padding: 5px;
                font-weight:bold;
            }
        """)
        # Noise Slider
        self.snr_slider = QSlider(Qt.Horizontal)
        self.snr_slider.setMinimum(0)  
        self.snr_slider.setMaximum(100) 
        self.snr_slider.setValue(50)  
        self.snr_slider.setTickInterval(5) 
        self.snr_slider.setSingleStep(1)  
        self.snr_slider.setTickPosition(QSlider.TicksBelow)
        self.snr_slider.valueChanged.connect(lambda: 
        (self, True))


        # Sampling Factor Slider
        self.sampling_factor = QSlider(Qt.Horizontal)
        self.sampling_factor.setMinimum(0)                   # Equivalent to 0.0 in steps of 0.2
        self.sampling_factor.setMaximum(50)                  # Equivalent to 5.0 in steps of 0.2
        self.sampling_factor.setValue(0) # Convert initial value to match slider scale
        self.sampling_factor.setTickInterval(1)              # Visual ticks (1 = 0.2 in real value)
        self.sampling_factor.setSingleStep(1)                # Movement in steps of 0.2
        self.sampling_factor.setTickPosition(QSlider.TicksBelow)




        # Slider for changing Hertz
        self.sampling_frequency = QSlider(Qt.Horizontal)
        self.sampling_frequency.setMinimum(0)           
        self.sampling_frequency.setValue(0) 
        self.sampling_frequency.setTickInterval(1)       
        self.sampling_frequency.setSingleStep(1)        
        self.sampling_frequency.setTickPosition(QSlider.TicksBelow)


        # Frequency Domain Mode
        self.frequencyPlotting = QPushButton()
        self.frequencyPlotting.setStyleSheet("""
            QPushButton{
                background-color: transparent;
                border-radius: 5px; 
                border: 1px solid white;
                color:white;
                font-size:14px;
                Padding: 10px 5px;
                font-weight: bold;                   
            }""")
        self.frequencyPlotting.setText(f"{self.frequencyShape}")
        self.frequencyPlotting.clicked.connect(lambda: self.changeFrequencyPlotting(self.frequencyShape))
        # Update frequency plotting button style
        self.frequencyPlotting.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['secondary']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['primary']};
                border-radius: 5px;
                font-size: 14px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary']};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: {COLORS['hover']};
            }}
        """)

        # Update plot widgets style
        PLOT_STYLE = {
            'background': COLORS['background'],
            'foreground': COLORS['text'],
            'title': {'color': COLORS['primary'], 'size': '14pt'},
            'labels': {'color': COLORS['text'], 'font-size': '12pt'},
            'axis': {'color': COLORS['border']}
        }
        self.samplingFrequencyLabel = self.createLabel(f"{self.samplingFrequency:.2f}")
        self.samplingFactorLabel = self.createLabel(f"{self.samplingFactor:.2f}")


        # Adding a little margin (spacer) between each row
        self.optionsLayout.addRow(self.createLabel("SNR(dB):"))
        self.optionsLayout.addRow(self.snr_slider)
        self.optionsLayout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))  # Add vertical space


        # Create a horizontal layout to add spacing between the label and its value
        samplingFactorLayout = QtWidgets.QHBoxLayout()
        samplingFactorLabel = self.createLabel("Nquist Rate:")
        samplingFactorLayout.addWidget(samplingFactorLabel)
        samplingFactorLayout.addStretch()  # Adds flexible space

        samplingFactorLayout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.factorMiddleLabel = self.createLabel("0 Fmax")
        samplingFactorLayout.addWidget(self.factorMiddleLabel)

        samplingFactorLayout.addItem(QtWidgets.QSpacerItem(60, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # Replace the label with an input field
        self.samplingFactorInput = QtWidgets.QLineEdit()
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.samplingFactorInput.setValidator(validator)

        self.samplingFactorInput.setFixedWidth(70)
        self.samplingFactorInput.setStyleSheet(LINE_EDIT_STYLE)
        self.samplingFactorInput.textChanged.connect(lambda: self.changeSamplingFactor(self.samplingFactorInput, self.samplingFactorInput.text()))
        samplingFactorLayout.addWidget(self.samplingFactorInput)  

        self.optionsLayout.addRow(samplingFactorLayout)
        self.optionsLayout.addRow(self.sampling_factor)
        self.optionsLayout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))  # Add vertical space


        samplingFrequencyLayout = QtWidgets.QHBoxLayout()
        samplingFrequencyLabel = self.createLabel("Sampling Frequency:")
        samplingFrequencyLayout.addWidget(samplingFrequencyLabel)
        samplingFrequencyLayout.addStretch()  # Adds flexible space





        self.middleLabel = self.createLabel("0 HZ")
        samplingFrequencyLayout.addWidget(self.middleLabel)

        samplingFrequencyLayout.addItem(QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # Create the input field
        self.samplingFrequencyInput = QtWidgets.QLineEdit()
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)
        self.samplingFrequencyInput.setValidator(validator)

        self.samplingFrequencyInput.setFixedWidth(70)
        self.samplingFrequencyInput.setStyleSheet(LINE_EDIT_STYLE)
        self.samplingFrequencyInput.textChanged.connect(lambda: self.changeSamplingFrequency(self.samplingFrequencyInput, self.samplingFrequencyInput.text()))
        
        samplingFrequencyLayout.addWidget(self.samplingFrequencyInput)


        self.optionsLayout.addRow(samplingFrequencyLayout)
        self.optionsLayout.addRow(self.sampling_frequency)
        self.optionsLayout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))  # Add vertical space

       

        self.optionsLayout.addRow(self.createLabel("Reconstruction Method:"), self.samplingType)
        self.optionsLayout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))  # Add vertical space
        self.optionsLayout.addRow(self.createLabel("Frequency Domain Mode:"), self.frequencyPlotting)

        self.sampling_factor.valueChanged.connect(  
            lambda: self.changeSamplingFactor(self.samplingFactorLabel, self.sampling_factor.value() * 0.1)
        )
        self.sampling_frequency.valueChanged.connect(
            lambda: self.changeSamplingFrequency(self.samplingFrequencyLabel, self.sampling_frequency.value())
        )
        

        # Add all to left panel
        self.leftLayout.addWidget(self.paramGroup)
        self.leftLayout.addWidget(self.buttonGroup)
        self.leftLayout.addWidget(self.listWidget)
        self.leftLayout.addWidget(self.optionsGroup)
        self.examples_button =  self.createButton("Examples")
        self.examples_button.clicked.connect(lambda: open_examples_dialog(self))
        self.leftLayout.addWidget(self.examples_button)


        # Creating central widget layout
        self.centralLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addLayout(self.centralLayout)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.centralLayout.addLayout(self.horizontalLayout)


        # Top widget (widget)
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.centralLayout.addWidget(self.widget)
        self.originalSignalLayout = QHBoxLayout(self.widget)
        self.signalViewer = pg.PlotWidget(title="Original Signal")
        self.signalViewer.setBackground("#001523")
        self.signalViewer.showGrid(x=True, y=True)
        self.originalSignalLayout.addWidget(self.signalViewer)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.centralLayout.addLayout(self.horizontalLayout)



        

        # Adding signal display widgets
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setObjectName("widget_2")
        self.centralLayout.addWidget(self.widget_2)
        self.samplingGraphLayout = QHBoxLayout(self.widget_2)
        self.samplingGraph = pg.PlotWidget(title="Reconstructed Single")
        self.samplingGraph.setBackground("#001523")
        self.samplingGraphLayout.addWidget(self.samplingGraph)
        self.samplingGraph.showGrid(x=True, y=True)



        self.widget_3 = QtWidgets.QWidget(self.centralwidget)
        self.widget_3.setObjectName("widget_3")
        self.centralLayout.addWidget(self.widget_3)
        self.differenceGraphLayout = QHBoxLayout(self.widget_3)
        self.differenceGraph = pg.PlotWidget(title="Signals Difference")
        self.differenceGraph.setBackground("#001523")
        self.differenceGraphLayout.addWidget(self.differenceGraph)
        self.differenceGraph.showGrid(x=True, y=True)

        

        self.widget_4 = QtWidgets.QWidget(self.centralwidget)
        self.widget_4.setObjectName("widget_4")
        self.centralLayout.addWidget(self.widget_4)
        self.frequencyDomainGraphLayout = QHBoxLayout(self.widget_4)
        self.frequencyDomainGraph = pg.PlotWidget(title="Frequency Domain")
        self.frequencyDomainGraph.setBackground("#001523")
        self.frequencyDomainGraphLayout.addWidget(self.frequencyDomainGraph)
        self.frequencyDomainGraph.showGrid(x=True, y=True)

        self.signalViewer.setBackground(COLORS['background'])
        self.samplingGraph.setBackground(COLORS['background'])
        self.differenceGraph.setBackground(COLORS['background']) 
        self.frequencyDomainGraph.setBackground(COLORS['background'])
        self.listWidget.setStyleSheet(LIST_STYLE)

        self.paramGroup.setStyleSheet(f"""
            QGroupBox {{
                color: {COLORS['text']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                margin-top: 16px;
                padding: 8px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }}
        """)

        self.browseFileButton.setStyleSheet(BROWSE_BUTTON_STYLE)

        # Update options group style
        self.optionsGroup.setStyleSheet(OPTIONS_GROUP_STYLE)

        # Update all sliders
        self.snr_slider.setStyleSheet(SLIDER_STYLE)
        self.sampling_factor.setStyleSheet(SLIDER_STYLE)
        self.sampling_frequency.setStyleSheet(SLIDER_STYLE)

        self.setCentralWidget(self.centralwidget)
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.leftPanelbuttons()


    def changeFrequencyPlotting(self, shape):
        if shape == "Pulses":
            self.frequencyShape = "Blocks"
            self.frequencyPlotting.setText(f"{self.frequencyShape}")
            self.frequencyDomainGraph.clear()
            self.plotSignificantFrequencies(self.signalData)
        else:
            self.frequencyShape = "Pulses"
            self.frequencyPlotting.setText(f"{self.frequencyShape}")
            self.frequencyDomainGraph.clear()
            self.plotSignificantFrequencies(self.signalData)


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Sampling Studio"))



    def add_noise(self, signal, snr_db):
        signal_power = np.mean(signal ** 2)
        snr_linear = 10 ** (snr_db / 10)
        noise_power = signal_power / snr_linear
        noise = np.sqrt(noise_power) * np.random.normal(size=signal.shape)
        noisy_signal = signal + noise
        return noisy_signal



    def showMixer(self):
        self.mixer.show()

    def changeSamplingFrequency(self, input_field, samplingFrequency):
        try:
            self.samplingFrequency = float(samplingFrequency)
            print(f"Sampling Frequency: {self.samplingFrequency}")

            self.samplingFactor = float(f"{self.samplingFrequency / self.f_max:.2f}")

            self.factorMiddleLabel.setText(f"{float(self.samplingFactor):.2f} Fmax")
            self.sampling_factor.setValue(int(self.samplingFactor / 0.1))
            self.middleLabel.setText(f"{float(self.samplingFrequency):.2f} HZ")

            # Set the value in the input field
            input_field.setText(f"{self.samplingFrequency:.2f}")

            # self.samplingFactorLabel.setText(f"{self.samplingFactor:.2f}")
            self.sampling_factor.setValue(int(self.samplingFactor / 0.1))

        except ValueError:
            # Handle the case where the text cannot be converted to a float
            print("Invalid input for sampling frequency")
        


    def changeSamplingFactor(self, label, samplingFactor):
        self.samplingFactor = float(samplingFactor)
        
        # Debug prints
        print(f"Sampling Factor: {self.samplingFactor}")
        print(f"Has f_max: {hasattr(self, 'f_max')}")
        if hasattr(self, 'f_max'):
            print(f"f_max value: {self.f_max}")
        
        # Calculate sampling frequency
        if hasattr(self, 'f_max') and self.f_max is not None:
            self.samplingFrequency = self.samplingFactor * self.f_max
            print(f"Calculated sampling frequency: {self.samplingFrequency}")
            
            # Ensure we're passing a number to setText
            if isinstance(self.samplingFrequency, (int, float)):
                label.setText(f"{self.samplingFactor:.2f}")
                self.factorMiddleLabel.setText(f"{float(self.samplingFactor):.2f} Fmax")
                self.sampling_frequency.setValue(int(self.samplingFrequency))
                self.middleLabel.setText(f"{float(self.samplingFrequency):.2f} HZ")
            else:
                print(f"Invalid sampling frequency type: {type(self.samplingFrequency)}") 
        else:
            print("f_max not set or is None")
        
        # Update plots if we have the required attributes
        if hasattr(self, 't_orig') and hasattr(self, 'signalData'):
            self.t_orig = np.linspace(0, 4, 15000, endpoint=False)
            snr_db = self.snr_slider.value()
            self.noisy_signal = self.add_noise(self.signalData, snr_db)
            self.startSampling(self.t_orig, self.noisy_signal)



    def openFileDialog(self):
        options = QFileDialog.Options()
        filePath,_ = QFileDialog.getOpenFileName(self,"Open Signal File", "", "(*.csv)",options=options)
        if filePath:  
            self.loadSignalFromFile(filePath)



    def loadSignalFromFile(self, filePath):
        try:
            # Clear existing signals and properties
            self.signals = []
            self.signal_properties = []
            self.signalViewer.clear()
            self.signalData = 0
            print(f"Data Loaded : {filePath}")
            data = pd.read_csv(filePath)
            if filePath not in self.loadedSignals:
                self.loadedSignals.append(filePath)

            print("Signal Loaded")
            t_new = data['time'].values  
            signal_new = data['voltage'].values
            self.copyData = signal_new

            # Perform FFT analysis
            sampling_rate = 1 / (t_new[1] - t_new[0])
            n_samples = len(signal_new)
            fft_result = np.fft.fft(signal_new)
            frequencies = np.fft.fftfreq(n_samples, 1/sampling_rate)
            magnitudes = np.abs(fft_result)
            
            # Find significant components (threshold can be adjusted)
            threshold = 0.1 * np.max(magnitudes)
            significant_idx = np.where(magnitudes > threshold)[0]
            
            # Debug prints for FFT results
            print(f"FFT Frequencies: {frequencies}")
            print(f"FFT Magnitudes: {magnitudes}")
            print(f"Significant Indices: {significant_idx}")
            
            # Store original combined signal
            self.t_orig = t_new
            self.signalData = signal_new

            # Update plot limits
            self.signalViewer.setLimits(
                xMin=0, 
                xMax=len(self.signalData), 
                yMin=min(self.signalData) - 0.5, 
                yMax=(max(self.signalData)) + 0.5
            )
            
            self.t_orig = np.linspace(0, 4, 15000, endpoint=False)
            
            # Generate and store noisy signal
            snr_db = self.snr_slider.value()
            self.noisy_signal = self.add_noise(self.signalData, snr_db)
            
            # Load existing signals
            signals_co, props_co = load_signals_from_json()
            for i, signal in enumerate(signals_co):
                self.signals.append(signal)
                self.signal_properties.append(props_co[i])
            
            # Add components to signals list
            for idx in significant_idx:
                if frequencies[idx] >= 0:  # Only positive frequencies
                    amplitude = 2 * magnitudes[idx] / n_samples
                    freq = abs(frequencies[idx])
                    phase = np.angle(fft_result[idx])
                    
                    # Debug prints for each component
                    print(f"Component Frequency: {freq}")
                    print(f"Component Amplitude: {amplitude}")
                    print(f"Component Phase: {phase}")
                    
                    # Create component signal
                    component = amplitude * np.sin(2 * np.pi * freq * self.t_orig + phase)
                    self.signals.append(component)
                    
                    # Add component properties
                    self.signal_properties.append({
                        'name': f"Component {len(self.signals)} ({freq:.2f} Hz)",
                        'amplitude': amplitude,
                        'frequency': freq,
                        'phase_shift': phase,
                        'type': 'sine'
                    })
            
            # Update UI list
            self.listWidget.clear()
            for signal in self.signal_properties:
                self.listWidget.addItem(signal['name'])

            # Ensure the signal data is properly set and UI is updated
            self.signalViewer.plot(self.t_orig, self.signalData, pen='w', name='Original Signal')
            self.startSampling(self.t_orig, self.signalData)

            for i in range(len(self.signal_properties)):
                print(f"Item {i} selected")
                self.listWidget.setCurrentRow(i)
                select_signal(self, True)

            # then exit edit mode
            self.listWidget.setCurrentRow(-1)
            select_signal(self, False)
            


        except Exception as e:
            print(f"Error loading signal from file: {e}")



    def signal_interpolation(self, interpolation_method,t, t_sampled, sampled_signal):
        if interpolation_method == "Whittaker":
            reconstructed_signal = np.zeros_like(t)
            # Perform Whittaker-Shannon Equation (sinc interpolation)
            for i, t_i in enumerate(t):
                sinc_values = np.sinc((t_i - t_sampled) / (t_sampled[1] - t_sampled[0]))
                reconstructed_signal[i] = np.sum(sinc_values * sampled_signal)

            return reconstructed_signal
        
        elif interpolation_method == "Cubic Spline":
            cs = CubicSpline(t_sampled, sampled_signal)
            reconstructed_signal = cs(t)
            return reconstructed_signal
        
        else:
            reconstructed_signal = np.zeros_like(self.signalData)
            # Zero-order hold (ZOH) reconstruction
            for i in range(len(sampled_signal)):
                start_index = int(t_sampled[i] / self.t_orig[-1] * len(self.t_orig))  # Calculate start index for ZOH
                if i == len(sampled_signal) - 1:
                    reconstructed_signal[start_index:] = sampled_signal[i]  # Last segment
                else:
                    end_index = int(t_sampled[i + 1] / self.t_orig[-1] * len(self.t_orig))  # Calculate end index
                    reconstructed_signal[start_index:end_index] = sampled_signal[i]  # Hold the sampled value

            return reconstructed_signal



    def startSampling(self, original_time, original_signal, sampling_frequency=None):
        # Clear previous graphs
        self.samplingGraph.clear()
        self.differenceGraph.clear()
        self.frequencyDomainGraph.clear()

        # Calculate maximum frequency
        f_min, f_max, max_amplitude = self.plotSignificantFrequencies(self.signalData)
        self.sampling_frequency.setMaximum(int(5*f_max))          

        print(f"Max Frequency: {f_max} Hz")

        # Set sampling frequency 
        if sampling_frequency is not None:
            f_s = sampling_frequency
        else:
            f_s = (self.samplingFactor) * f_max
        
        self.samplingFrequency = f"{f_s:.2f}"
        T = original_time[-1]

        # Calculate number of samples 
        num_samples = max(2,int(f_s * T))   
        
        # Get SNR value from slider
        snr_db = self.snr_slider.value()

        # Sample the signal at regular intervals first
        t_sampled = np.linspace(0, T, num_samples)
        sampled_signal = np.interp(t_sampled, original_time, original_signal)

        if len(t_sampled) < 2:
            print("Error: Not enough sampled points to perform interpolation.")
            return
        # Add noise only to the sampled points
        if snr_db < 50:  # Only add noise if SNR is less than maximum
            signal_power = np.mean(sampled_signal ** 2)
            snr_linear = 10 ** (snr_db / 10)
            noise_power = signal_power / snr_linear
            noise = np.sqrt(noise_power) * np.random.normal(size=sampled_signal.shape)
            sampled_signal = sampled_signal + noise

        # Store values for later use
        self.f_max = f_max
        self.original_time = original_time
        self.original_signal = original_signal
        self.t_sampled = t_sampled
        self.sampled_signal = sampled_signal

        # Choose interpolation method and reconstruct
        if self.samplingType.currentText() == "Whittaker":
            reconstructed_signal = self.signal_interpolation("Whittaker", self.t_orig, t_sampled, sampled_signal)
        elif self.samplingType.currentText() == "Cubic Spline":
            reconstructed_signal = self.signal_interpolation("Cubic Spline", self.t_orig, t_sampled, sampled_signal)
        else:
            reconstructed_signal = self.signal_interpolation("Zero Order", self.t_orig, t_sampled, sampled_signal)

        # Plot signals
        self.samplingGraph.plot(original_time, reconstructed_signal, pen='r', name='Reconstructed Signal')
        self.samplingGraph.setXRange(0, 0.05)
        self.signalViewer.setXRange(0, 0.05)
        self.differenceGraph.setXRange(0, 0.05)
        self.differenceGraph.setYRange(min(self.signalData), max(self.signalData))

        # Plot sample points with noise
        scatter = pg.ScatterPlotItem(t_sampled, sampled_signal, size=4, pen=pg.mkPen(None), 
                                    brush=pg.mkBrush(255, 255, 255, 120))
        self.samplingGraph.addItem(scatter)

        # Calculate and plot difference
        if self.copyData is None:
            self.copyData = original_signal

        difference_signal = self.copyData - reconstructed_signal
        self.differenceGraph.plot(original_time, difference_signal, pen='y', name='Difference Signal')

        # Set plot limits
        self.signalViewer.setLimits(xMin=0, xMax=T, yMin=min(original_signal), yMax=max(original_signal))
        self.differenceGraph.setLimits(xMin=0, xMax=T, yMin=min(original_signal), yMax=max(original_signal))
        self.samplingGraph.setLimits(xMin=0, xMax=T, yMin=min(original_signal), yMax=max(original_signal))

        # Validate reconstruction
        metrics = self.calculate_reconstruction_metrics(original_signal, reconstructed_signal)
        
        # Add metrics text to difference plot
        metrics_text = (f"MSE: {metrics['MSE']:.2e}\n")

        text_item = pg.TextItem(
            text=metrics_text,
            color='w',
            anchor=(0, 0)
        )

        # Set the font size
        font = QFont()
        font.setPointSize(18)  # Adjust the size as needed
        text_item.setFont(font)

        self.differenceGraph.addItem(text_item)
        text_item.setPos(0, max(difference_signal))

        # Validate if reconstruction meets quality threshold
        if metrics['SNR'] < 20:  # SNR threshold of 20dB
            print("Warning: Poor reconstruction quality detected")
            # Add visual indicator
            warning_text = pg.TextItem(
                text="⚠️ Poor reconstruction",
                color='y',
                anchor=(1, 0)
            )
            self.samplingGraph.addItem(warning_text)
            warning_text.setPos(T, max(reconstructed_signal))


    def plotSignificantFrequencies(self, signal):
        fft_result = np.fft.fft(signal)  # Return Complex Numbers (Real -> Amplitude, Imaginary -> Phase)
        freqs = np.fft.fftfreq(len(signal), d=(self.t_orig[1] - self.t_orig[0]))  # Frequency bins
        magnitudes = np.abs(fft_result) / len(signal)  # Amplitudes

        # Set a dynamic threshold to detect significant peaks
        threshold = np.mean(magnitudes) + 1.5 * np.std(magnitudes)
        significant_peaks, properties = find_peaks(magnitudes, height=threshold)
        positive_peaks = freqs[significant_peaks]
        positive_peaks = positive_peaks[positive_peaks > 0]

        if significant_peaks.size > 0:
            min_freq = positive_peaks[0]
            max_freq = positive_peaks[-1]
            self.f_max = max_freq
            max_amplitude = properties['peak_heights'].max()

            print(f"Min Frequency: {min_freq} Hz")
            print(f"Max Frequency: {max_freq} Hz")
            print(f"Max Amplitude: {max_amplitude}")

            # Clear the frequency domain graph and plot the original frequencies
            self.frequencyDomainGraph.clear()
                    
            # Call the repeat function with the calculated sampling frequency
            f_sampling = self.samplingFactor * max_freq
            if self.frequencyShape == "Pulses":
                self.frequencyDomainGraph.clear()
                self.frequencyDomainGraph.plot(freqs, magnitudes, pen='r', name='Original Frequency Domain')
                self.frequencyDomainGraph.setXRange(-6, 6 )
                self.repeatFrequencyPulses(freqs, magnitudes, f_sampling)
            else:
                aliasing = f_sampling < 2 * max_freq
                self.frequencyDomainGraph.clear()
                self.repeatFrequencyBlocks(min_freq, max_freq, max_amplitude, f_sampling, aliasing)

        else:
            print("No significant peaks found")
            return None, None, None

        # Set the x-axis range symmetrically around the origin
        freq_range = max(abs(min(freqs)), abs(max(freqs)))
        self.frequencyDomainGraph.setYRange(0, max(magnitudes))
                                
        return min_freq, max_freq, max_amplitude


    def repeatFrequencyPulses(self, freqs, magnitudes, f_sampling, repeats=5):
        # Plot the Positive Range
        for i in range(1, repeats + 1):
            shifted_freqs_pos = freqs + i * f_sampling
            positive_indices = shifted_freqs_pos > 0  # Only plot positive frequencies
            self.frequencyDomainGraph.plot(shifted_freqs_pos[positive_indices], magnitudes[positive_indices], 
                                        pen='b', name=f'Repeat {i} (Positive)')

        # Plot the negative Range
        for i in range(1, repeats + 1):
            shifted_freqs_neg = freqs - i * f_sampling
            negative_indices = shifted_freqs_neg < 0  
            self.frequencyDomainGraph.plot(shifted_freqs_neg[negative_indices], magnitudes[negative_indices], 
                                        pen='b', name=f'Repeat {i} (Negative)')

        #max_x_range = repeats * f_sampling 
        self.frequencyDomainGraph.setXRange(-10 * self.f_max , 10 * self.f_max)







    def repeatFrequencyBlocks(self, min_freq, max_freq, max_amplitude, f_sampling, aliasing):
        if min_freq is None or max_freq is None:
            print("No significant frequencies to repeat.")
            return

        rect_width = 2 * max_freq 
        center_freq = 0

        n_repeats = 5 

        for i in range(-n_repeats, n_repeats + 1): 
            pos_freq = center_freq + (i * f_sampling)

            rect_start = pos_freq - (rect_width / 2)
            rect_end = pos_freq + (rect_width / 2)

            if aliasing:
                rect = QGraphicsRectItem(rect_start, 0, rect_width, max_amplitude)
                rect.setPen(pg.mkPen('r', width=2)) 
                rect.setBrush(pg.mkBrush(0, 0, 255, 50))  
                self.frequencyDomainGraph.addItem(rect)

            else:
                rect = QGraphicsRectItem(rect_start, 0, rect_width, max_amplitude)
                rect.setPen(pg.mkPen('b', width=2))  
                rect.setBrush(pg.mkBrush(0, 0, 255, 10)) 
                self.frequencyDomainGraph.addItem(rect)

        self.frequencyDomainGraph.setXRange(-3 * self.f_max , 3 * self.f_max)
        self.frequencyDomainGraph.setYRange(0, max_amplitude)


    # left panel

    def leftPanelbuttons(self):
        self.addComponent.clicked.connect(lambda: handle_component_button(self,True))
        self.deleteComponent.clicked.connect(lambda: delete_signal(self,False))
        self.listWidget.itemClicked.connect(lambda: select_signal(self,True))
        
        self.lineEdit.textChanged.connect(lambda: update_signal_real_time(self,1))
        self.lineEdit_2.textChanged.connect(lambda: update_signal_real_time(self,2))
        self.lineEdit_4.textChanged.connect(lambda: update_signal_real_time(self,3))
        self.comboBox.currentTextChanged.connect(lambda: update_signal_real_time(self,4))
        



    def createLabel(self, text):
        label = QtWidgets.QLabel(text)
        label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 14px;
            font-weight: bold;
        """)
        return label

    def createLineEdit(self, default_text, validator=None):
        lineEdit = QtWidgets.QLineEdit()
        lineEdit.setText(default_text)
        if validator:
            lineEdit.setValidator(validator)
        lineEdit.setStyleSheet(LINE_EDIT_STYLE)
        return lineEdit

    def createComboBox(self, items):
        comboBox = QtWidgets.QComboBox()
        comboBox.addItems(items)
        comboBox.setStyleSheet(COMBO_STYLE)
        return comboBox

    def createButton(self, text):
        button = QtWidgets.QPushButton(text)
        button.setStyleSheet(BUTTON_STYLE)
        return button
    

    def openEvent(self, event):
        with open('signals.json', 'w') as file:
            file.write('{"signals":[],"properties":[]}')

        # close the window
        event.accept()

    def calculate_reconstruction_metrics(self, original_signal, reconstructed_signal):
        """Calculate error metrics between original and reconstructed signals"""
        if len(original_signal) != len(reconstructed_signal):
            reconstructed_signal = np.interp(
                np.linspace(0, len(original_signal), len(original_signal)),
                np.linspace(0, len(reconstructed_signal), len(reconstructed_signal)),
                reconstructed_signal
            )
        
        # Mean Squared Error
        mse = np.mean((original_signal - reconstructed_signal) ** 2)
        
        # Root Mean Squared Error
        rmse = np.sqrt(mse)
        
        # Signal-to-Noise Ratio
        signal_power = np.mean(original_signal ** 2)
        noise_power = mse
        snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else float('inf')
        
        # Maximum Absolute Error
        max_error = np.max(np.abs(original_signal - reconstructed_signal))
        
        return {
            'MSE': mse,
            'RMSE': rmse,
            'SNR': snr,
            'MAX_ERROR': max_error
        }

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
