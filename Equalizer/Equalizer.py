from math import ceil
from PyQt5 import QtCore, QtGui, QtWidgets
import librosa
import  pyqtgraph as pg
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QLayout , QVBoxLayout , QHBoxLayout, QGridLayout ,QWidget, QFileDialog, QPushButton, QColorDialog, QInputDialog, QComboBox, QDialog, QRadioButton
from scipy.io import wavfile
import numpy as np
import pandas as pd
import sounddevice as sd
from equalizer_functions import updateEqualization, toggleFrequencyScale, playOriginalAudio, playFilteredAudio, toggleVisibility, togglePlaying, resetSignal, stopAudio, signalPlotting , zoomingIn , zoomingOut , speedingUp , speedingDown , toggleFreqDomain , plotSpectrogram, export_signal , deleteSignal
from audiogram import Audiogram
import sys
import os
from style import COLORS, STYLES, FONT_STYLES, GRAPH_STYLES
from ui_helper_functions import apply_fonts, show_loading, hide_loading, show_status, setup_sidebar,setup_tooltips , setup_shortcuts




class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_mode = "Music and Animals"  # Updated default mode
        self.frequency_scale = "Linear"
        self.signalData = ""
        self.signalTime = ""
        self.modifiedData = self.signalData
        self.signalTimer = QTimer()
        self.signalTimeIndex = 0
        self.domain = "Time Domain"
        self.cached = False
        
        # Combined music and animal ranges
        self.music_animal_ranges = {
            "Music": {
                "Bass": [(20, 300)],
                "Piano": [(300, 3000)],
                "Strings": [(3000, 8000)]
            },
            "Animals": {
                "Dogs": [(100, 2000)],
                "Birds": [(2000, 8000)],
                "Bats": [(8000, 20000)]
            }
        }

        # Vocals and Phonemes mode ranges
        self.vocal_ranges = {
            "Instruments": {
                "Background": [(50, 500)],
                "Mid-range": [(500, 2000)],
                "High-range": [(2000, 8000)]
            },
            "Phonemes": {
                "S_sounds": [(4000, 8000)],
                "F_sounds": [(2500, 6000)],
                "Sh_sounds": [(1500, 4000)]
            }
        }

        self.music_animal_ranges = {
            "Music": {
                "Bass Instruments": [(20, 300)],      # For removing bass/drums
                "Mid-Range Instruments": [(300, 2000)], # For removing piano/guitar
                "High-Range Instruments": [(2000, 8000)] # For removing cymbals/high notes
            },
            "Animals": {
                "Low-Frequency Animals": [(50, 500)],   # For removing deep growls/roars
                "Mid-Frequency Animals": [(500, 3000)], # For removing barks/calls
                "High-Frequency Animals": [(3000, 20000)] # For removing chirps/squeaks
            }
        }

        # Update vocal and phoneme ranges for singing
        self.vocal_ranges = {
            "Instruments": {
                "Backing Track": [(50, 500)],     # Remove background music
                "Mid Instruments": [(500, 2000)], # Remove mid-range instruments
                "High Instruments": [(2000, 8000)] # Remove high-range instruments
            },
            "Phonemes": {
                "S-sounds": [(4000, 8000)],   # Remove sibilant sounds
                "F-sounds": [(2500, 6000)],   # Remove fricative sounds
                "Sh-sounds": [(1500, 4000)]   # Remove shushing sounds
            }
        }
        
        # self.instrument_ranges = {
        #     "Trumpet": [(0, 500)],      # Low frequency range
        #     "Xylophone": [(500, 1200)],     # Mid frequency range
        #     "Brass": [(1200, 6400)], # Upper mid range
        #     "Celesta": [(4000, 13000)] # High frequency range
        # }

        # # Animal sounds matching dataset ranges
        # self.animal_ranges = {
        #     "Dogs": [(0, 450)],        # Low frequency range
        #     "Wolves": [(450, 1100)],   # Mid frequency range
        #     "Crow": [(1100, 3000)],    # High frequency range
        #     "Bat": [(3000, 9000)]      # Ultrasonic range
        # }

        # # ECG ranges matching dataset
        

        # self.ecg_ranges = {
        #     "Normal": [(0, 1000)],  # Normal ECG range
        #     "Atrial Fibrillation": [(15, 20)],  # Atrial Fibrillation range
        #     "Atrial Flutter": [(2, 8)],  # Atrial Flutter range
        #     "Ventricular fibrillation": [(0, 5)]  # Ventricular fibrillation range
        # }

        self.sliders = []   
        self.sliderLabels = []

        self.lastLoadedSignal = None
        self.lastModifiedSignal = None

        
    def select_noise_sample(self, start_idx, end_idx):
        """Select noise sample from silent part of signal"""
        if self.signalData is not None:
            self.wiener_settings["Noise_Sample"] = self.signalData[start_idx:end_idx]

    # Apply styles to main components
    def apply_modern_styles(self):
        # Buttons
        for button in [self.browseFile, self.playPause, self.resetButton, 
                    self.zoomIn, self.zoomOut, self.speedUp, self.speedDown]:
            button.setStyleSheet(STYLES['BUTTON'])
        
        # ComboBox
        self.modeList.setStyleSheet(STYLES['COMBOBOX'])
        
        # Graphs
        self.graph1.setStyleSheet(STYLES['GRAPH'])
        self.graph2.setStyleSheet(STYLES['GRAPH'])
        
        # Spectrograms
        # Style spectrograms
        for canvas in [self.firstGraphCanvas, self.secondGraphCanvas]:
            canvas.setStyleSheet(STYLES['SPECTROGRAM'])
        
        for canvas in [self.firstGraphCanvas, self.secondGraphCanvas]:
            canvas.setStyleSheet("""
                background-color: transparent;
                border: none;
            """)
        
        
        # Checkbox
        self.spectogramCheck.setStyleSheet(STYLES['CHECKBOX'])
        
        # Main frame
        self.mainBodyframe.setStyleSheet(STYLES['PANEL'])
        self.sideBarScroll.setStyleSheet(STYLES['PANEL'])

        self.verticalGraphs.setSpacing(20)
        self.horizontalLayout.setSpacing(15)
        self.mainbody.setContentsMargins(20, 20, 20, 20)

        # Add smooth animations
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    # Add these methods to the Ui_MainWindow class
    def setup_graphs(self):
        """Configure graph styling and behavior"""
        
        # Style both graphs
        for graph in [self.graph1, self.graph2]:
            # Background and border
            graph.setBackground(GRAPH_STYLES['BACKGROUND'])
            graph.setStyleSheet(f"""
                border: 1px solid {COLORS['accent']};
                border-radius: 10px;
                padding: 10px;
                background: rgba(26, 27, 30, 0.8);
            """)
            
            # Configure axis appearance
            axis_pen = pg.mkPen(color=GRAPH_STYLES['AXIS']['color'], 
                            width=GRAPH_STYLES['AXIS']['width'])
            graph.getAxis('bottom').setPen(axis_pen)
            graph.getAxis('left').setPen(axis_pen)
            
            # Configure grid appearance
            graph.showGrid(x=True, y=True)
            grid_pen = pg.mkPen(color=GRAPH_STYLES['GRID']['color'], 
                            width=GRAPH_STYLES['GRID']['width'])
            graph.getAxis('bottom').setGrid(True)
            graph.getAxis('left').setGrid(True)
            
            # Style axis labels
            graph.getAxis('bottom').setLabel('Time (s)', 
                                        color=GRAPH_STYLES['LABELS']['color'], 
                                        size=GRAPH_STYLES['LABELS']['size'])
            graph.getAxis('left').setLabel('Amplitude', 
                                        color=GRAPH_STYLES['LABELS']['color'], 
                                        size=GRAPH_STYLES['LABELS']['size'])
            
            # Add zoom region
            self.region = pg.LinearRegionItem()
            self.region.setZValue(10)
            graph.addItem(self.region, ignoreBounds=True)
            
            # Add mouse interactions
            graph.scene().sigMouseMoved.connect(self.mouse_moved)
            
        # Link x-axis between graphs
        self.graph1.setXLink(self.graph2)
        
        # Add crosshair cursor
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.graph1.addItem(self.vLine, ignoreBounds=True)
        self.graph1.addItem(self.hLine, ignoreBounds=True)

    def mouse_moved(self, evt):
        """Update crosshair position on mouse move"""
        if self.graph1.sceneBoundingRect().contains(evt):
            mouse_point = self.graph1.plotItem.vb.mapSceneToView(evt)
            self.vLine.setPos(mouse_point.x())
            self.hLine.setPos(mouse_point.y())
            
            # Show coordinates in status bar
            show_status(self,f"Time: {mouse_point.x():.3f}s, Amplitude: {mouse_point.y():.3f}")

    def plot_signals(self):
        """Plot signals with enhanced styling"""
        # Clear previous plots
        self.graph1.clear()
        self.graph2.clear()
        
        # Plot original signal
        original_pen = pg.mkPen(color=GRAPH_STYLES['CURVE']['original']['color'],
                            width=GRAPH_STYLES['CURVE']['original']['width'])
        self.graph1.plot(self.signalTime, self.signalData, pen=original_pen)
        
        # Plot modified signal
        modified_pen = pg.mkPen(color=GRAPH_STYLES['CURVE']['modified']['color'],
                            width=GRAPH_STYLES['CURVE']['modified']['width'])
        self.graph2.plot(self.signalTime, self.modifiedData, pen=modified_pen)
        
        # Add legend
        self.graph1.addLegend()
        self.graph1.plot(name='Original Signal', pen=original_pen)
        self.graph2.addLegend()
        self.graph2.plot(name='Modified Signal', pen=modified_pen)

    # Add this to setupUi() after creating graphs
    def enhance_graphs(self):
        """Apply graph enhancements"""
        self.setup_graphs()
        
        # Add to existing setupUi method:
        self.setup_graphs()
        
        # Update the signalPlotting function call
        def update_plots(self):
            self.plot_signals()



    def LoadSignalFile(self):
        print("Lets Choose a file")
        
        file_path = ""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Signal File", "", 
                                                "File Extension (*.wav *.mp3 *.csv)", 
                                                options=options)
        
        if file_path:
            try:
                show_loading(self,"Loading signal file...")
                deleteSignal(self)
                self.cached = False  
                # Stop any playing audio and timers
                sd.stop()
                if hasattr(self, 'signalTimer'):
                    self.signalTimer.stop()
                
                # Reset all audio states
                self._playing_original = False
                self._playing_filtered = False
                self.signalTimeIndex = 0
                
                # Reset play button states
                self.playOriginalSignal.setIcon(self.playIcon)
                self.playOriginalSignal.setText("Play Original Audio")
                self.playFilteredSignal.setIcon(self.playIcon)
                self.playFilteredSignal.setText("Play Filtered Audio")
                
                # Show loading spinner
                self.loadingSpinner.show()
                QtWidgets.QApplication.processEvents()
                
                # Load new file
                extension = file_path.split(".")[-1]
                self.samplingRate = 0
                
                if extension == "wav" or extension == "mp3":
                    self.signalData, self.samplingRate = librosa.load(file_path)
                    self.modifiedData = self.signalData
                    
                    duration = librosa.get_duration(y=self.signalData, sr=self.samplingRate)
                    self.signalTime = np.linspace(0, duration, len(self.signalData))
                elif extension == "csv":
                    if not self.load_csv_data(file_path):
                        return

                # Create fresh copies of signal data
                
                # Clean up old audiogram
                if hasattr(self, 'audiogramWidget'):
                    self.audiogramWidget.deleteLater()

                # Create new audiogram
                self.audiogramWidget = Audiogram(
                    self.signalTime, 
                    self.signalData, 
                    self.modifiedData
                )
                self.audiogramLayout.addWidget(self.audiogramWidget)

                # Clear existing spectrograms
                self.firstGraphAxis.clear()
                self.secondGraphAxis.clear()
                
                # Update UI with new data
                if len(self.signalData) > 1:  # Only plot if we have valid data
                    signalPlotting(self)
                    
                    # Force spectrogram update
                    plotSpectrogram(self)
                    self.firstGraphCanvas.draw()
                    self.secondGraphCanvas.draw()
                    
                    updateEqualization(self)
                    change_mode(self, self.current_mode)
                    
                
                # Store references
                self.lastLoadedSignal = np.copy(self.signalData)
                self.lastModifiedSignal = np.copy(self.modifiedData)
                show_status(self,"File loaded successfully")
                
            except Exception as e:
                show_status(self,f"Error: {str(e)}", 5000)
            
            finally:
                hide_loading(self)

            

    def setup_wiener_controls(self):
        """Setup Wiener filter interface controls"""
        # Create container for Wiener filter controls
        self.wienerContainer = QtWidgets.QWidget(self.sideBarScroll)
        wienerLayout = QtWidgets.QVBoxLayout(self.wienerContainer)
        wienerLayout.setSpacing(15)
        wienerLayout.setContentsMargins(10, 10, 10, 10)

        # Title label
        titleLabel = QtWidgets.QLabel("Wiener Filter Controls")
        titleLabel.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 16px;
            font-weight: bold;
            padding: 5px;
            background: rgba(114, 137, 218, 0.1);
            border-radius: 5px;
        """)
        wienerLayout.addWidget(titleLabel)

        # Signal selection group
        signalGroup = QtWidgets.QGroupBox("Signal Selection")
        signalGroup.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {COLORS['accent']};
                border-radius: 6px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                color: {COLORS['text']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        signalLayout = QtWidgets.QVBoxLayout(signalGroup)

        # Signal buttons
        self.signalButtons = []
        for i in range(3):
            btn = QtWidgets.QPushButton(f"Load Signal {i+1}")
            btn.setStyleSheet(STYLES['BUTTON'])
            btn.setIcon(self.uploadIcon)
            btn.setIconSize(QtCore.QSize(20, 20))
            self.signalButtons.append(btn)
            signalLayout.addWidget(btn)

        wienerLayout.addWidget(signalGroup)

        # Noise sample controls
        noiseGroup = QtWidgets.QGroupBox("Noise Sample")
        noiseGroup.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {COLORS['accent']};
                border-radius: 6px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                color: {COLORS['text']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        noiseLayout = QtWidgets.QVBoxLayout(noiseGroup)

        # Add noise selection instructions
        instructionLabel = QtWidgets.QLabel("Select a region of silence to use as noise sample:")
        instructionLabel.setStyleSheet(f"color: {COLORS['text']};")
        instructionLabel.setWordWrap(True)
        noiseLayout.addWidget(instructionLabel)

        # Noise selection button
        self.selectNoiseButton = QtWidgets.QPushButton("Select Noise Region")
        self.selectNoiseButton.setStyleSheet(STYLES['BUTTON'])
        self.selectNoiseButton.setIcon(QtGui.QIcon("images/selection.png"))
        self.selectNoiseButton.setIconSize(QtCore.QSize(20, 20))
        noiseLayout.addWidget(self.selectNoiseButton)

        # Selection status
        self.noiseStatusLabel = QtWidgets.QLabel("No noise sample selected")
        self.noiseStatusLabel.setStyleSheet(f"""
            color: {COLORS['text']};
            padding: 5px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 3px;
        """)
        noiseLayout.addWidget(self.noiseStatusLabel)

        wienerLayout.addWidget(noiseGroup)

        # Filter controls
        filterGroup = QtWidgets.QGroupBox("Filter Controls")
        filterGroup.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {COLORS['accent']};
                border-radius: 6px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                color: {COLORS['text']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        filterLayout = QtWidgets.QVBoxLayout(filterGroup)

        # Apply filter button
        self.applyWienerButton = QtWidgets.QPushButton("Apply Wiener Filter")
        self.applyWienerButton.setStyleSheet(STYLES['BUTTON'])
        self.applyWienerButton.setIcon(QtGui.QIcon("images/filter.png"))
        self.applyWienerButton.setIconSize(QtCore.QSize(20, 20))
        filterLayout.addWidget(self.applyWienerButton)

        # Filter status
        self.filterStatusLabel = QtWidgets.QLabel("Ready to filter")
        self.filterStatusLabel.setStyleSheet(f"""
            color: {COLORS['text']};
            padding: 5px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 3px;
        """)
        filterLayout.addWidget(self.filterStatusLabel)

        wienerLayout.addWidget(filterGroup)

        # Add stretch to push everything to the top
        wienerLayout.addStretch()

        # Hide container by default
        self.wienerContainer.hide()
        
        # Add to sidebar
        self.verticalLayout_2.addWidget(self.wienerContainer)

    def show_wiener_controls(self):
        """Show Wiener filter controls and hide other mode controls"""
        self.slidersContainer.hide()
        self.wienerContainer.show()

    def hide_wiener_controls(self):
        """Hide Wiener filter controls and show normal mode controls"""
        self.wienerContainer.hide()
        self.slidersContainer.show()

    def load_csv_data(self, file_path):
        try:
            deleteSignal(self)
            # First try to read the header to detect format
            with open(file_path, 'r') as f:
                first_line = f.readline().strip()
            
            if ',' in first_line:  # x,y paired format
                fileData = pd.read_csv(file_path, delimiter=',', skiprows=1)
                self.signalTime = np.array(fileData.iloc[:, 0].astype(float).tolist())
                self.signalData = np.array(fileData.iloc[:, 1].astype(float).tolist())
                
                # Validate time data
                if len(self.signalTime) < 2:
                    raise ValueError("CSV file must contain at least 2 data points")
                
                # Calculate and validate sampling rate
                time_diff = np.diff(self.signalTime)
                if not np.all(time_diff > 0):
                    raise ValueError("Time values must be strictly increasing")
                self.samplingRate = 1 / np.mean(time_diff)
                
            else:  # Single column format
                try:
                    fileData = pd.read_csv(file_path, header=None, skiprows=1)
                except:
                    fileData = pd.read_csv(file_path, header=None)
                
                self.signalData = np.array(fileData.iloc[:, 0].astype(float).tolist())
                
                # Validate data
                if len(self.signalData) < 2:
                    raise ValueError("CSV file must contain at least 2 data points")
                
                # Generate time values
                self.samplingRate = 1000  # Default sampling rate
                duration = len(self.signalData) / self.samplingRate
                self.signalTime = np.linspace(0, duration, len(self.signalData))
            
            # Initialize modified data
            self.modifiedData = np.copy(self.signalData)
            self.speed = 3
            
            # Reset cache
            self.cached = False
            if hasattr(self, '_cached_fft'):
                del self._cached_fft
            if hasattr(self, '_cached_freqs'):
                del self._cached_freqs
                

            return True

        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, 
                "Error", 
                f"Error loading CSV file: {str(e)}\nExpected format: either 'time,amplitude' pairs or single column of amplitudes"
            )
            # Initialize with safe defaults on error
            self.signalData = np.zeros(2)
            self.modifiedData = np.zeros(2)
            self.signalTime = np.linspace(0, 1/1000, 2)
            self.samplingRate = 1000
            return False
        
    def setup_connections(self):
        """Connect UI signals to functions"""
        self.browseFile.clicked.connect(self.LoadSignalFile)
        self.frequencyDomainButton.clicked.connect(lambda: toggleFreqDomain(self))
        self.playOriginalSignal.clicked.connect(lambda: playOriginalAudio(self))
        self.playFilteredSignal.clicked.connect(lambda: playFilteredAudio(self))
        self.exportButton.clicked.connect(lambda: export_signal(self))
        self.playPause.clicked.connect(lambda: togglePlaying(self))
        self.resetButton.clicked.connect(lambda: resetSignal(self))
        self.zoomIn.clicked.connect(lambda: zoomingIn(self))
        self.zoomOut.clicked.connect(lambda: zoomingOut(self))
        self.speedUp.clicked.connect(lambda: speedingUp(self))
        self.speedDown.clicked.connect(lambda: speedingDown(self))
        self.deleteButton.clicked.connect(lambda: deleteSignal(self))
        self.spectogramCheck.clicked.connect(lambda: toggleVisibility(self))
        self.modeList.currentTextChanged.connect(lambda text: change_mode(self, text))
        # self.modeList.currentTextChanged.connect(self.change_mode)
        self.frequencyDomainButton.clicked.connect(lambda : self.audiogramWidget.toggleShape())
        self.exportButton.clicked.connect(lambda : stopAudio(self))

        viewbox1 = self.graph1.getViewBox()
        viewbox2 = self.graph2.getViewBox()

        # Connect the ViewBox signals in both directions
        viewbox1.sigRangeChanged.connect(lambda window, viewRange: self.sync_pan(viewbox1, viewbox2))
        viewbox2.sigRangeChanged.connect(lambda window, viewRange: self.sync_pan(viewbox2, viewbox1))

        self.apply_modern_styles()
        apply_fonts(self)
        setup_tooltips(self)
        setup_shortcuts(self)
        setup_sidebar(self)
    
    def setupUi(self, MainWindow):
        # 1. Basic window setup
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1329, 911)
        MainWindow.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}
        """)

        # Create central widget and main layouts
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout = QtWidgets.QGridLayout()
        self.mainBodyframe = QtWidgets.QFrame(self.centralwidget)
        self.mainbody = QtWidgets.QVBoxLayout()
        self.verticalGraphs = QtWidgets.QVBoxLayout()

        # ------------------------------ Icons ---------------------------- #
        
        # Icons setup
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.uploadIcon = QtGui.QIcon(os.path.join(base_dir, "images", "upload.png"))
        self.playIcon = QtGui.QIcon(os.path.join(base_dir, "images", "play.png"))
        self.stopIcon = QtGui.QIcon(os.path.join(base_dir, "images", "pause.png"))
        self.signalIcon = QtGui.QIcon(os.path.join(base_dir, "images", "signal.png"))
        self.replayIcon = QtGui.QIcon(os.path.join(base_dir, "images", "replay.png"))
        self.speedUpIcon = QtGui.QIcon(os.path.join(base_dir, "images", "up.png"))
        self.speedDownIcon = QtGui.QIcon(os.path.join(base_dir, "images", "down.png"))
        self.zoomInIcon = QtGui.QIcon(os.path.join(base_dir, "images", "zoom_in.png"))
        self.zoomOutIcon = QtGui.QIcon(os.path.join(base_dir, "images", "zoom_out.png"))
        self.exportIcon = QtGui.QIcon(os.path.join(base_dir, "images", "file.png"))
        self.deleteIcon = QtGui.QIcon(os.path.join(base_dir, "images", "bin.png"))


        # Main layout setup
        self.mainBodyframe = QtWidgets.QFrame(self.centralwidget)
        self.mainBodyframe.setStyleSheet(f"""
            background-color: {COLORS['background']};
            border-radius: 15px;
            margin: 10px;
        """)
        self.mainBodyframe.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.mainBodyframe.setFrameShadow(QtWidgets.QFrame.Raised)
        
        # Create vertical layout for graphs and controls
        self.verticalGraphs = QtWidgets.QVBoxLayout()
        self.verticalGraphs.setSpacing(20)

        # Create horizontal layout for time domain graphs
        self.horizontalLayout = QtWidgets.QHBoxLayout()



        # --------------------------- Important Attributes --------------------------- #
        self.equalizerMode= "Musical Instruments"
    



        # ---------------------- Setup the side bar ---------------------- #
        self.sideBarScroll = QtWidgets.QScrollArea(self.centralwidget)
        self.sideBarScroll.setWidgetResizable(True)
        self.sideBarScroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sideBarScroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {COLORS['secondary']};
                border: none;
                border-radius: 15px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {COLORS['secondary']};
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['accent']};
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['button_hover']};
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        # Create container widget for sidebar content
        self.sideBarContent = QtWidgets.QWidget()
        self.sideBarContent.setStyleSheet(f"""
            background-color: {COLORS['secondary']};
            border-radius: 15px;
            margin: 5px;
            padding: 10px;
        """)

        # Move existing sidebar layout to container
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.sideBarContent)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)

        # Add all your existing sidebar widgets to verticalLayout_2
        # ...existing sidebar widget code...

        # Set the container as the scroll area widget
        self.sideBarScroll.setWidget(self.sideBarContent)

        # Add scroll area to main layout instead of sideBarScroll
        self.gridLayout.addWidget(self.sideBarScroll, 0, 0, 1, 1)
        self.sideBarScroll.setMinimumWidth(350)
        
        # 1. File Section
        self.browseFile = QtWidgets.QPushButton(self.sideBarScroll)
        self.browseFile.setIcon(self.uploadIcon)
        self.browseFile.setIconSize(QtCore.QSize(25, 25))

        # 2. View Controls Section
        self.frequencyDomainButton = QtWidgets.QPushButton(self.sideBarScroll)
        self.frequencyDomainButton.setStyleSheet(STYLES['TOGGLE_BUTTON'])
        self.frequencyDomainButton.setCheckable(True)
        self.frequencyDomainButton.setIcon(self.signalIcon)
        self.frequencyDomainButton.setIconSize(QtCore.QSize(25, 25))
        self.spectogramCheck = QtWidgets.QCheckBox(self.sideBarScroll)
        
        # 3. Mode Selection Section
        self.setup_mode_selection()
        
        # 4. Sliders Section
        self.slidersContainer = QtWidgets.QWidget(self.sideBarScroll)
        self.slidersContainer.setStyleSheet(STYLES['SLIDERS_CONTAINER'])
        self.slidersLayout = QtWidgets.QVBoxLayout(self.slidersContainer)
        self.slidersLayout.setSpacing(5)  # Reduce spacing
        self.slidersLayout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Add to sidebar
        self.verticalLayout_2.addWidget(self.slidersContainer)
        
        

        # Create scroll area
        self.scrollArea = QtWidgets.QScrollArea(self.sideBarScroll)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background: {COLORS['secondary']};
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {COLORS['accent']};
                min-height: 20px;
                border-radius: 4px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['button_hover']};
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        # Create inner widget to hold sliders
        self.slidersInnerContainer = QtWidgets.QWidget()
        self.slidersInnerContainer.setObjectName("scrollAreaWidgetContents")
        self.slidersInnerLayout = QtWidgets.QVBoxLayout(self.slidersInnerContainer)
        self.slidersInnerLayout.setSpacing(5)  # Reduce spacing
        self.slidersInnerLayout.setContentsMargins(5, 5, 5, 5)  # Minimal margins

        self.scrollArea.setWidget(self.slidersInnerContainer)
        self.slidersLayout.addWidget(self.scrollArea)

        # Add Wiener Filter Container
        self.wienerContainer = QtWidgets.QWidget(self.sideBarScroll)
        wienerLayout = QtWidgets.QVBoxLayout(self.wienerContainer)
        wienerLayout.setSpacing(15)
        wienerLayout.setContentsMargins(10, 10, 10, 10)

        # Title label
        titleLabel = QtWidgets.QLabel("Wiener Filter Controls")
        titleLabel.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 16px;
            font-weight: bold;
            padding: 5px;
            background: rgba(114, 137, 218, 0.1);
            border-radius: 5px;
        """)
        wienerLayout.addWidget(titleLabel)

        # Signal selection group
        signalGroup = QtWidgets.QGroupBox("Signal Selection")
        signalGroup.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {COLORS['accent']};
                border-radius: 6px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                color: {COLORS['text']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        signalLayout = QtWidgets.QVBoxLayout(signalGroup)

        # Signal buttons
        self.signalButtons = []
        for i in range(3):
            btn = QtWidgets.QPushButton(f"Load Signal {i+1}")
            btn.setStyleSheet(STYLES['BUTTON'])
            btn.setIcon(self.uploadIcon)
            btn.setIconSize(QtCore.QSize(20, 20))
            self.signalButtons.append(btn)
            signalLayout.addWidget(btn)

        wienerLayout.addWidget(signalGroup)

        # Noise sample controls
        noiseGroup = QtWidgets.QGroupBox("Noise Sample")
        noiseGroup.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {COLORS['accent']};
                border-radius: 6px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                color: {COLORS['text']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        noiseLayout = QtWidgets.QVBoxLayout(noiseGroup)

        # Add noise selection instructions
        instructionLabel = QtWidgets.QLabel("Select a region of silence to use as noise sample:")
        instructionLabel.setStyleSheet(f"color: {COLORS['text']};")
        instructionLabel.setWordWrap(True)
        noiseLayout.addWidget(instructionLabel)

        # Noise selection button
        self.selectNoiseButton = QtWidgets.QPushButton("Select Noise Region")
        self.selectNoiseButton.setStyleSheet(STYLES['BUTTON'])
        self.selectNoiseButton.setIcon(QtGui.QIcon("images/selection.png"))
        self.selectNoiseButton.setIconSize(QtCore.QSize(20, 20))
        noiseLayout.addWidget(self.selectNoiseButton)

        # Selection status
        self.noiseStatusLabel = QtWidgets.QLabel("No noise sample selected")
        self.noiseStatusLabel.setStyleSheet(f"""
            color: {COLORS['text']};
            padding: 5px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 3px;
        """)
        noiseLayout.addWidget(self.noiseStatusLabel)

        wienerLayout.addWidget(noiseGroup)

        # Filter controls
        filterGroup = QtWidgets.QGroupBox("Filter Controls")
        filterGroup.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {COLORS['accent']};
                border-radius: 6px;
                margin-top: 12px;
                padding: 10px;
            }}
            QGroupBox::title {{
                color: {COLORS['text']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """)
        filterLayout = QtWidgets.QVBoxLayout(filterGroup)

        # Apply filter button
        self.applyWienerButton = QtWidgets.QPushButton("Apply Wiener Filter")
        self.applyWienerButton.setStyleSheet(STYLES['BUTTON'])
        self.applyWienerButton.setIcon(QtGui.QIcon("images/filter.png"))
        self.applyWienerButton.setIconSize(QtCore.QSize(20, 20))
        filterLayout.addWidget(self.applyWienerButton)

        # Filter status
        self.filterStatusLabel = QtWidgets.QLabel("Ready to filter")
        self.filterStatusLabel.setStyleSheet(f"""
            color: {COLORS['text']};
            padding: 5px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 3px;
        """)
        filterLayout.addWidget(self.filterStatusLabel)

        wienerLayout.addWidget(filterGroup)
        wienerLayout.addStretch()

        # Hide container by default and add to sidebar
        self.wienerContainer.hide()
        self.verticalLayout_2.addWidget(self.wienerContainer)

        # 5. Audio Controls Section
        self.playOriginalSignal = QtWidgets.QPushButton(self.sideBarScroll)
        self.playOriginalSignal.setIcon(self.playIcon)
        self.playOriginalSignal.setIconSize(QtCore.QSize(25, 25))
        self.playFilteredSignal = QtWidgets.QPushButton(self.sideBarScroll)
        self.playFilteredSignal.setIcon(self.playIcon)
        self.playFilteredSignal.setIconSize(QtCore.QSize(25, 25))
        self.exportButton = QtWidgets.QPushButton(self.sideBarScroll)
        self.exportButton.setIcon(self.exportIcon)
        self.exportButton.setIconSize(QtCore.QSize(25, 25))
        self.gridLayout.addWidget(self.sideBarScroll, 0, 0, 1, 1)

        #---------------------------------- end of side bar ----------------------------------#
    
        
        # Time domain graphs layout
        self.graph1 = pg.PlotWidget(self.mainBodyframe)
        self.graph1.setBackground("transparent")
        self.graph1.setObjectName("graph1")
        self.graph1.showGrid(x=True, y=True)
        self.graph1.setStyleSheet("border-radius: 6px;border: 2px solid white;")
        self.graph1.setMinimumHeight(200)

        self.graph2 = pg.PlotWidget(self.mainBodyframe)
        self.graph2.setBackground("transparent") 
        self.graph2.showGrid(x=True, y=True)
        self.graph2.setObjectName("graph2")
        self.graph2.setStyleSheet("border-radius: 6px;border: 2px solid white;")
        self.graph2.setMinimumHeight(200)


        self.graphSectionLayout = QtWidgets.QVBoxLayout()
        self.graphsLayout = QtWidgets.QHBoxLayout()
        self.graphsLayout.addWidget(self.graph1)
        self.graphsLayout.addWidget(self.graph2)
        

    

        #---------------------------------- Control Buttons ----------------------------------#
        self.controlButtonsLayout = QtWidgets.QHBoxLayout()
        self.controlButtonsLayout.setAlignment(QtCore.Qt.AlignCenter)  # Center alignment

        self.playPause = QtWidgets.QPushButton(self.mainBodyframe)
        self.playPause.setStyleSheet(STYLES['BUTTON'])
        self.playPause.setIcon(self.stopIcon)
        self.playPause.setIconSize(QtCore.QSize(15, 15))
        self.playPause.setObjectName("playPause")

        self.resetButton = QtWidgets.QPushButton(self.mainBodyframe)
        self.resetButton.setStyleSheet(STYLES['BUTTON'])
        self.resetButton.setIcon(self.replayIcon)
        self.resetButton.setIconSize(QtCore.QSize(15, 15))

        self.zoomIn = QtWidgets.QPushButton(self.mainBodyframe)
        self.zoomIn.setStyleSheet(STYLES['BUTTON'])
        self.zoomIn.setIcon(self.zoomInIcon)
        self.zoomIn.setIconSize(QtCore.QSize(15, 15))

        self.zoomOut = QtWidgets.QPushButton(self.mainBodyframe)
        self.zoomOut.setStyleSheet(STYLES['BUTTON'])
        self.zoomOut.setIcon(self.zoomOutIcon)
        self.zoomOut.setIconSize(QtCore.QSize(15, 15))

        self.speedUp = QtWidgets.QPushButton(self.mainBodyframe)
        self.speedUp.setStyleSheet(STYLES['BUTTON'])
        self.speedUp.setIcon(self.speedUpIcon)
        self.speedUp.setIconSize(QtCore.QSize(15, 15))

        self.speedDown = QtWidgets.QPushButton(self.mainBodyframe)
        self.speedDown.setStyleSheet(STYLES['BUTTON'])
        self.speedDown.setIcon(self.speedDownIcon)
        self.speedDown.setIconSize(QtCore.QSize(15, 15))

        self.deleteButton = QtWidgets.QPushButton(self.mainBodyframe)
        self.deleteButton.setStyleSheet(STYLES['BUTTON'])
        self.deleteButton.setIcon(self.deleteIcon)
        self.deleteButton.setIconSize(QtCore.QSize(15, 15))

        self.controlButtonsLayout.addWidget(self.playPause)
        self.controlButtonsLayout.addWidget(self.resetButton)
        self.controlButtonsLayout.addWidget(self.zoomIn)
        self.controlButtonsLayout.addWidget(self.zoomOut)
        self.controlButtonsLayout.addWidget(self.speedUp)
        self.controlButtonsLayout.addWidget(self.speedDown)
        self.controlButtonsLayout.addWidget(self.deleteButton)
        
        # Add stretch to push buttons to top
        self.controlButtonsLayout.addStretch()
        
        # Add layouts to main horizontal layout
        self.graphSectionLayout.addLayout(self.graphsLayout)
        self.graphSectionLayout.addLayout(self.controlButtonsLayout)
        
        # Add graph section to main vertical layout
        self.verticalGraphs.addLayout(self.graphSectionLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()

        # Add separator line
        self.line_8 = QtWidgets.QFrame(self.mainBodyframe)
        self.line_8.setStyleSheet("""
            width: 20px;
            height: 5px;
            background-color: #3a3b3c;
            border: 10px;
            border-radius: 5px;
        """)
        self.line_8.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalGraphs.addWidget(self.line_8)



        #---------------------------------- Spectrogram Section ----------------------------------#
        self.spectrogramLayout = QtWidgets.QHBoxLayout()
        self.spectrogramLayout.setObjectName("spectrogramLayout")
        self.spectrogramLayout.setSpacing(20)
        self.spectrogramLayout.setContentsMargins(10, 10, 10, 10)

        # Create containers for each spectrogram group
        self.firstSpectrogramContainer = QtWidgets.QWidget()
        self.secondSpectrogramContainer = QtWidgets.QWidget()
        self.firstSpectrogramLayout = QtWidgets.QHBoxLayout(self.firstSpectrogramContainer)
        self.secondSpectrogramLayout = QtWidgets.QHBoxLayout(self.secondSpectrogramContainer)

        # Initialize spectrograms with proper dimensions and settings
        self.firstSpectrogramFig = Figure(figsize=(8, 4), constrained_layout=True)
        self.firstSpectrogramFig.patch.set_alpha(0.0)
        self.firstGraphCanvas = FigureCanvas(self.firstSpectrogramFig)
        # Add more space on right for colorbar
        self.firstGraphAxis = self.firstSpectrogramFig.add_subplot(111)
        self.firstGraphAxis.set_facecolor('none')

        self.secondSpectrogramFig = Figure(figsize=(8, 4), constrained_layout=True)
        self.secondSpectrogramFig.patch.set_alpha(0.0)
        self.secondGraphCanvas = FigureCanvas(self.secondSpectrogramFig)
        self.secondGraphAxis = self.secondSpectrogramFig.add_subplot(111)
        self.secondGraphAxis.set_facecolor('none')

        # Add tight layout to both figures
        self.firstSpectrogramFig.tight_layout()
        self.secondSpectrogramFig.tight_layout()

        self.firstGraphAxis.text(0.5, 0.5, 'Load a signal to view spectrogram', 
            horizontalalignment='center', verticalalignment='center',
            color=COLORS['text'])
        self.secondGraphAxis.text(0.5, 0.5, 'Load a signal to view spectrogram',
            horizontalalignment='center', verticalalignment='center',
            color=COLORS['text'])

        # Create spectrogram layout with fixed size
        self.spectrogramLayout = QtWidgets.QHBoxLayout()
        self.spectrogramLayout.addWidget(self.firstGraphCanvas, stretch=1)
        self.spectrogramLayout.addWidget(self.secondGraphCanvas, stretch=1)
        self.spectrogramLayout.setSpacing(20)
        self.spectrogramLayout.setContentsMargins(20, 20, 20, 20)
        
        # Create container with fixed size
        self.spectrogramContainer = QtWidgets.QWidget(self.mainBodyframe)
        self.spectrogramContainer.setFixedHeight(250)
        self.spectrogramContainer.setStyleSheet(STYLES['SPECTROGRAM'])
        self.spectrogramContainer.setLayout(self.spectrogramLayout)

        # Add to main layout
        self.verticalGraphs.addWidget(self.spectrogramContainer)

        #---------------------------------- End of Spectrogram Section ----------------------------------#

        self.line_9 = QtWidgets.QFrame(self.mainBodyframe)
        self.line_9.setStyleSheet("""
            width: 20px;
            height: 5px;
            background-color: #3a3b3c;
            border: 10px;
            border-radius: 5px;
        """)
        self.line_9.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_9.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.verticalGraphs.addWidget(self.line_9)

        #---------------------------------- Audiogram Section ----------------------------------#

        self.audiogramContainer = QtWidgets.QWidget(self.mainBodyframe)
        self.audiogramContainer.setStyleSheet(STYLES['AUDIOGRAM'])
        self.audiogramContainer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Expanding
        )
        self.audiogramContainer.setMinimumSize(800, 300)
        self.audiogramLayout = QVBoxLayout(self.audiogramContainer)
        self.audiogramLayout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        self.audiogramLayout.setSpacing(0)  # Remove spacing between widgets
        
        self.audiogramLayout.setSpacing(15)
        self.audiogramLayout.setContentsMargins(0, 20, 0, 0)
        self.verticalGraphs.addWidget(self.audiogramContainer)



        # Configure main layout
        self.gridLayout_3 = QtWidgets.QGridLayout(self.mainBodyframe)

        # Then modify the layout configuration:
        self.mainbody.addLayout(self.verticalGraphs)
        self.mainbody.setStretch(0, 4)
        self.mainbody.setStretch(1, 1)

        self.gridLayout_3.addLayout(self.mainbody, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.mainBodyframe, 0, 1, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 6)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        # Set up central widget and menu bar
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1329, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        # Connect signals and apply styles
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.apply_modern_styles()
        apply_fonts(self)

        # Add loading spinner
        self.loadingSpinner = QtWidgets.QProgressBar(self.sideBarScroll)
        self.loadingSpinner.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {COLORS['accent']};
                border-radius: 5px;
                text-align: center;
                color: {COLORS['text']};
                background-color: {COLORS['secondary']};
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['accent']};
                width: 10px;
                margin: 0.5px;
            }}
        """)
        self.loadingSpinner.setMaximum(0)  # Makes it an infinite spinner
        self.loadingSpinner.setMinimum(0)
        self.loadingSpinner.hide()  # Hidden by default
        self.verticalLayout_2.addWidget(self.loadingSpinner)

        
        self.setup_connections()
        self.enhance_graphs()

        # Create initial sliders for default mode
        self.create_music_animal_sliders()


        
    # Update the mode selection section styling
    def setup_mode_selection(self):
        # Mode selection container
        self.modeSelectionContainer = QtWidgets.QWidget(self.sideBarScroll)
        self.modeSelectionLayout = QtWidgets.QVBoxLayout(self.modeSelectionContainer)
        self.modeSelectionLayout.setSpacing(10)
        self.modeSelectionLayout.setContentsMargins(15, 15, 15, 15)

        # Mode Label
        self.modeLabel = QtWidgets.QLabel("Choose Mode")
        self.modeLabel.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
                background: rgba(114, 137, 218, 0.1);
                border-radius: 5px;
            }}
        """)
        self.modeLabel.setAlignment(QtCore.Qt.AlignLeft)
        
        # Mode ComboBox with modern styling
        self.modeList = QtWidgets.QComboBox()
        self.modeList.setFixedHeight(45)
        self.modeList.addItems([
            "Music and Animals", 
            "Vocals and Phonemes",  # For singing mode
            "Wiener Filter"      # For noise removal
        ])
        
        # Update mode icons
        mode_icons = {
            0: "music.png",  # Music + Animals
            1: "mic.png",    # Vocals + Phonemes
            2: "filter.png"  # Wiener Filter
        }
        
        # Enhanced ComboBox styling
        self.modeList.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['secondary']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['accent']};
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: 600;
            }}
            
            QComboBox:hover {{
                border-color: {COLORS['button_hover']};
                background-color: {COLORS['button']};
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            
            QComboBox::down-arrow {{
                image: url(images/dropdown.png);
                width: 16px;
                height: 16px;
            }}
            
            QComboBox:on {{
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {COLORS['secondary']};
                color: {COLORS['text']};
                selection-background-color: {COLORS['accent']};
                selection-color: {COLORS['text']};
                border: 1px solid {COLORS['accent']};
                border-radius: 0 0 8px 8px;
                padding: 4px;
            }}
            
            QComboBox QAbstractItemView::item {{
                height: 35px;
                padding: 8px;
                margin: 2px;
                border-radius: 4px;
            }}
            
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['button']};
            }}
            
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['accent']};
            }}
        """)

        # Add icons to ComboBox items
        self.modeList.setIconSize(QtCore.QSize(20, 20))
        mode_icons = {
            0: "music.png",
            1: "animal.png", 
            2: "wave.png",
            3: "heart.png"
        }
        
        for index, icon_file in mode_icons.items():
            self.modeList.setItemIcon(index, QtGui.QIcon(f"images/{icon_file}"))

        # Add to layout with proper spacing
        self.modeSelectionLayout.addWidget(self.modeLabel)
        self.modeSelectionLayout.addWidget(self.modeList)
        
        # Add to main sidebar layout
        #self.verticalLayout_2.addWidget(self.modeSelectionContainer)

        # Connect signal
        self.modeList.currentTextChanged.connect(lambda text: change_mode(self, text))

    # Then modify sync_pan function:
    def sync_pan(self, viewbox, viewrect):
        """
        Synchronize panning between two viewboxes
        Args:
            viewbox: Source viewbox that triggered the pan
            viewrect: Target viewbox to be synchronized
        """
        if viewbox is None or viewrect is None:
            return
            
        # Get the current x-axis range from source viewbox state
        view_state = viewbox.state
        x_min = view_state['viewRange'][0][0]
        x_max = view_state['viewRange'][0][1]

        y_min = view_state['viewRange'][1][0]
        y_max = view_state['viewRange'][1][1]


        
        # Block signals temporarily to prevent recursive updates
        viewrect.blockSignals(True)
        viewrect.setRange(xRange=(x_min, x_max), padding=0)
        viewrect.setYRange(y_min, y_max, padding=0)

        viewrect.blockSignals(False)


    


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.browseFile.setText(_translate("MainWindow", "Browse File"))
        #self.frequencyDomainButton.setText(_translate("MainWindow", "Frequency Domain"))
        self.modeLabel.setText(_translate("MainWindow", "Choose The Mode"))
        self.spectogramCheck.setText(_translate("MainWindow", "Hide The Spectograms"))
        
        self.playOriginalSignal.setText(_translate("MainWindow", "Play Original Audio"))
        self.playFilteredSignal.setText(_translate("MainWindow", "Play Filtered Audio"))
        self.exportButton.setText(_translate("MainWindow", "Export Signal"))
    
    

    def create_music_animal_sliders(self):
        """Create sliders for music and animal sounds"""
        self.clear_sliders()
        
        # Add music sliders
        for name, ranges in self.music_animal_ranges["Music"].items():
            self.add_slider(name, ranges[0][0], ranges[0][1])
            
        # Add animal sliders
        for name, ranges in self.music_animal_ranges["Animals"].items():
            self.add_slider(name, ranges[0][0], ranges[0][1])

    def create_vocal_phoneme_sliders(self):
        """Create sliders for vocals and phonemes"""
        self.clear_sliders()
        
        # Add instrument sliders
        for name, ranges in self.vocal_ranges["Instruments"].items():
            self.add_slider(name, ranges[0][0], ranges[0][1])
            
        # Add phoneme sliders
        for name, ranges in self.vocal_ranges["Phonemes"].items():
            self.add_slider(name, ranges[0][0], ranges[0][1])

    def clear_sliders(self):
        """Clear all existing sliders"""
        # Delete existing widgets
        for slider in self.sliders:
            slider.deleteLater()
        for label in self.sliderLabels:
            label.deleteLater()
        
        # Clear lists
        self.sliders = []
        self.sliderLabels = []
        
        # Reset layout
        while self.slidersInnerLayout.count():
            item = self.slidersInnerLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
    def add_slider(self, name, min_freq, max_freq):
        """Add a slider with frequency range label"""
        # Create container for slider group
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 10)
        
        # Add label with name and frequency range
        label = QtWidgets.QLabel(f"{name} ({min_freq}-{max_freq} Hz)")
        label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 2px;
        """)
        layout.addWidget(label)
        
        # Create slider
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(0)
        slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {COLORS['accent']};
                height: 8px;
                background: {COLORS['secondary']};
                margin: 2px 0;
                border-radius: 4px;
            }}

            QSlider::handle:horizontal {{
                background: {COLORS['accent']};
                border: none;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}

            QSlider::handle:horizontal:hover {{
                background: {COLORS['button_hover']};
            }}
        """)
        
        # Connect slider value changed signal
        slider.valueChanged.connect(self.on_slider_changed)
        
        layout.addWidget(slider)
        self.slidersInnerLayout.addWidget(container)
        self.slidersInnerLayout.addSpacing(2)  # Small space between slider groups
        
        # Store references
        self.sliders.append(slider)
        self.sliderLabels.append(label)
        
    def on_slider_changed(self):
        """Handle slider value changes"""
        if self.current_mode == "Music and Animals":
            self.apply_music_animal_equalization()
        elif self.current_mode == "Vocals and Phonemes":
            self.apply_vocal_phoneme_equalization()

    def apply_music_animal_equalization(self):
        """Apply equalization for music and animal mode"""
        if self.signalData is None or len(self.sliders) != 6:
            return

        # Get FFT of signal
        if not self.cached:
            self._cached_fft = np.fft.fft(self.signalData)
            self._cached_freqs = np.fft.fftfreq(len(self.signalData), 1/self.samplingRate)
            self.cached = True

        # Create a copy of the FFT data
        modified_fft = self._cached_fft.copy()
        
        # Apply each slider's equalization
        for i, (name, ranges) in enumerate(list(self.music_animal_ranges["Music"].items()) + 
                                        list(self.music_animal_ranges["Animals"].items())):
            # Get slider value (0-100)
            slider_value = self.sliders[i].value()
            
            # Convert to attenuation factor (0-1)
            attenuation = (slider_value / 100)
            
            # Get frequency range
            freq_range = ranges[0]
            freq_min, freq_max = freq_range
            
            # Find frequency indices
            freq_mask = (abs(self._cached_freqs) >= freq_min) & (abs(self._cached_freqs) <= freq_max)
            
            # Apply attenuation to frequency range
            modified_fft[freq_mask] *= attenuation
            
        # Apply inverse FFT
        self.modifiedData = np.real(np.fft.ifft(modified_fft))
        
        # Update plots
        signalPlotting(self)
        plotSpectrogram(self)

        if hasattr(self, 'audiogramWidget'):
            self.audiogramWidget.updateData(
                self.signalTime,
                self.signalData,
                self.modifiedData
            )

    def apply_vocal_phoneme_equalization(self):
        """Apply equalization for vocals and phonemes mode"""
        if self.signalData is None or len(self.sliders) != 6:
            return

        # Get FFT of signal
        if not self.cached:
            self._cached_fft = np.fft.fft(self.signalData)
            self._cached_freqs = np.fft.fftfreq(len(self.signalData), 1/self.samplingRate)
            self.cached = True

        # Create a copy of the FFT data
        modified_fft = self._cached_fft.copy()
        
        # Apply each slider's equalization
        for i, (name, ranges) in enumerate(list(self.vocal_ranges["Instruments"].items()) + 
                                        list(self.vocal_ranges["Phonemes"].items())):
            # Get slider value (0-100)
            slider_value = self.sliders[i].value()
            
            # Convert to attenuation factor (0-1)
            attenuation = (slider_value / 100)
            
            # Get frequency range
            freq_range = ranges[0]
            freq_min, freq_max = freq_range
            
            # Find frequency indices
            freq_mask = (abs(self._cached_freqs) >= freq_min) & (abs(self._cached_freqs) <= freq_max)
            
            # Apply attenuation to frequency range with smoother transition for phonemes
            if i >= 3:  # Phoneme sliders
                # Create smooth transition at frequency boundaries
                transition_width = (freq_max - freq_min) * 0.1
                lower_transition = np.logical_and(
                    abs(self._cached_freqs) >= freq_min - transition_width,
                    abs(self._cached_freqs) < freq_min
                )
                upper_transition = np.logical_and(
                    abs(self._cached_freqs) > freq_max,
                    abs(self._cached_freqs) <= freq_max + transition_width
                )
                
                # Apply gradual attenuation in transition regions
                modified_fft[lower_transition] *= (1 - (1-attenuation) * 
                    (abs(self._cached_freqs[lower_transition]) - (freq_min-transition_width)) / transition_width)
                modified_fft[upper_transition] *= (1 - (1-attenuation) * 
                    (1 - (abs(self._cached_freqs[upper_transition]) - freq_max) / transition_width))
                
            modified_fft[freq_mask] *= attenuation
            
        # Apply inverse FFT
        self.modifiedData = np.real(np.fft.ifft(modified_fft))
        
        # Update plots
        signalPlotting(self)
        plotSpectrogram(self)

        if hasattr(self, 'audiogramWidget'):
            self.audiogramWidget.updateData(
                self.signalTime,
                self.signalData,
                self.modifiedData
            )

if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    from equalizer_functions import change_mode, updateEqualization, signalPlotting, plotSpectrogram
    import numpy as np

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    # Initialize with minimal valid data
    ui.signalData = np.array([0])
    ui.modifiedData = np.array([0])
    ui.signalTime = np.array([0])
    ui.samplingRate = 44100
    ui.cached = False
    ui.current_mode = "Music and Animals"
    
    
    # Initialize audiogram
    ui.audiogramWidget = Audiogram(
        ui.signalTime, 
        ui.signalData, 
        ui.modifiedData
    )
    ui.audiogramLayout.addWidget(ui.audiogramWidget)

    # Create initial sliders
    change_mode(ui, ui.current_mode)

    MainWindow.show()
    sys.exit(app.exec_())

