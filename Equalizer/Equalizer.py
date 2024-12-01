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
from equalizer_functions import changeMode, createSliders, updateEqualization, toggleFrequencyScale, playOriginalAudio, playFilteredAudio, toggleVisibility, togglePlaying, resetSignal, stopAudio, signalPlotting , zoomingIn , zoomingOut , speedingUp , speedingDown , toggleFreqDomain , plotSpectrogram, export_signal , deleteSignal
from audiogram import Audiogram
import sys
import os


# Add theme switching capability
THEMES = {
    'DARK': {
        'background': '#1E1E2E',
        'secondary': '#252535',
        'accent': '#7AA2F7',
        'text': '#CDD6F4'
    },
    'LIGHT': {
        'background': '#FFFFFF',
        'secondary': '#F0F0F0', 
        'accent': '#2962FF',
        'text': '#000000'
    }
}

# Add these color constants at the start of setupUi
COLORS = {
    'background': '#1E1E2E', 
    'secondary': '#252535',  
    'accent': '#7AA2F7',   
    'text': '#CDD6F4',      
    'button': '#394168',   
    'button_hover': '#4A5178'
}

# Add these style constants
STYLES = {
    'BUTTON': f"""
        QPushButton {{
            background-color: {COLORS['button']};
            color: {COLORS['text']};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 500;
            transition: background-color 0.3s;
        }}
        QPushButton:hover {{
            background-color: {COLORS['button_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['accent']};
        }}
    """,
    
    'COMBOBOX': f"""
        QComboBox {{
            background-color: {COLORS['secondary']};
            color: {COLORS['text']};
            border: 2px solid {COLORS['accent']};
            border-radius: 6px;
            padding: 5px 10px;
            min-width: 150px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox::down-arrow {{
            image: url(images/dropdown.png);
            width: 12px;
            height: 12px;
        }}
    """,
    
    'SLIDER': f"""
        QSlider::groove:horizontal {{
            border: none;
            height: 6px;
            background: {COLORS['secondary']};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {COLORS['accent']};
            border: none;
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {COLORS['button_hover']};
        }}
    """,
    
    'GRAPH': f"""
        border: 2px solid {COLORS['accent']};
        border-radius: 10px;
        padding: 10px;
        background-color: {COLORS['background']};
    """,
    
    'CHECKBOX': f"""
        QCheckBox {{
            color: {COLORS['text']};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {COLORS['accent']};
            border-radius: 4px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLORS['accent']};
        }}
    """
}


STYLES['COMBOBOX'] = f"""
    QComboBox {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['accent']};
        border-radius: 6px;
        padding: 5px 10px;
        min-width: 150px;
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox::down-arrow {{
        image: url(images/dropdown.png);
        width: 12px;
        height: 12px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        selection-background-color: {COLORS['accent']};
        selection-color: {COLORS['text']};
        border: 1px solid {COLORS['accent']};
        border-radius: 4px;
    }}
"""
STYLES['COMBOBOX'] = f"""
    QComboBox {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['accent']};
        border-radius: 6px;
        padding: 5px 10px;
        min-width: 150px;
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox::down-arrow {{
        image: url(images/dropdown.png);
        width: 12px;
        height: 12px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        selection-background-color: {COLORS['accent']};
        selection-color: {COLORS['text']};
        border: 1px solid {COLORS['accent']};
        border-radius: 4px;
    }}
"""

STYLES['SPECTROGRAM'] = f"""
    border: 2px solid {COLORS['accent']};
    border-radius: 10px;
    padding: 5px;
    background-color: {COLORS['secondary']};
"""

# First, update the STYLES and COLORS constants at the top of the file

# Update font constants
FONT_STYLES = {
    'REGULAR': {
        'family': 'Segoe UI',
        'size': 10,
        'weight': 'normal'
    },
    'HEADING': {
        'family': 'Segoe UI',
        'size': 12,
        'weight': 'bold'
    },
    'BUTTON': {
        'family': 'Segoe UI',
        'size': 10,
        'weight': 'bold'
    }
}

# Update the ComboBox style
STYLES['COMBOBOX'] = f"""
    QComboBox {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['accent']};
        border-radius: 8px;
        padding: 8px 15px;
        min-width: 200px;
        min-height: 40px;
        font-family: {FONT_STYLES['REGULAR']['family']};
        font-size: 14px;
        font-weight: bold;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['button_hover']};
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
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        selection-background-color: {COLORS['accent']};
        selection-color: {COLORS['text']};
        border: 1px solid {COLORS['accent']};
        border-radius: 4px;
        padding: 4px;
        font-size: 14px;
    }}
"""

# Update FONT_STYLES with fallback fonts
FONT_STYLES = {
    'REGULAR': {
        'family': 'Segoe UI, Arial, Helvetica, sans-serif',
        'size': 10,
        'weight': 'normal'
    },
    'HEADING': {
        'family': 'Segoe UI, Arial, Helvetica, sans-serif', 
        'size': 12,
        'weight': 'bold'
    },
    'BUTTON': {
        'family': 'Segoe UI, Arial, Helvetica, sans-serif',
        'size': 10,
        'weight': 'bold'
    }
}

COLORS = {
    'background': '#1A1B1E',  # Darker background
    'secondary': '#2A2B2E',   # Slightly lighter than background
    'accent': '#7289DA',      # Discord-like blue accent
    'text': '#FFFFFF',        # Pure white text
    'button': '#404249',      # Button background
    'button_hover': '#5865F2', # Button hover state
    'success': '#43B581',     # Success/positive color
    'error': '#F04747'        # Error/negative color
}

# Update button styles with modern aesthetics
STYLES['BUTTON'] = f"""
    QPushButton {{
        background-color: {COLORS['button']};
        color: {COLORS['text']};
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }}
    QPushButton:hover {{
        background-color: {COLORS['button_hover']};
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }}
    QPushButton:pressed {{
        background-color: {COLORS['accent']};
        transform: translateY(1px);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }}
"""

# Enhanced ComboBox styling
STYLES['COMBOBOX'] = f"""
    QComboBox {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['accent']};
        border-radius: 8px;
        padding: 8px 16px;
        min-width: 200px;
        font-size: 14px;
        font-weight: 600;
    }}
    QComboBox:hover {{
        border-color: {COLORS['button_hover']};
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
    QComboBox QAbstractItemView {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        selection-background-color: {COLORS['accent']};
        selection-color: {COLORS['text']};
        border: 1px solid {COLORS['accent']};
        border-radius: 4px;
    }}
"""

# Add glass-morphism effect to main panels
STYLES['PANEL'] = f"""
    QFrame {{
        background-color: rgba(42, 43, 46, 0.7);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
    }}
"""

# Update graph styling
STYLES['GRAPH'] = f"""
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px;
    background-color: rgba(26, 27, 30, 0.8);
    backdrop-filter: blur(10px);
"""

# Add these new styles for spectrograms and audiogram
STYLES['SPECTROGRAM'] = f"""
    QWidget {{
        background-color: rgba(26, 27, 30, 0.8);
        border: 1px solid {COLORS['accent']};
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        background-color: rgba(26, 27, 30, 0.8);
        backdrop-filter: blur(10px);
    }}
"""

STYLES['AUDIOGRAM'] = f"""
    QWidget {{
        background-color: rgba(26, 27, 30, 0.9);
        border: 2px solid {COLORS['accent']};
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }}
"""

# Add modern toggle button style
STYLES['TOGGLE_BUTTON'] = f"""
    QPushButton {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['accent']};
        border-radius: 20px;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 600;
        min-width: 120px;
    }}
    QPushButton:checked {{
        background-color: {COLORS['accent']};
        color: {COLORS['text']};
    }}
    QPushButton:hover {{
        background-color: {COLORS['button_hover']};
        border-color: {COLORS['button_hover']};
    }}
"""

STYLES['CHECKBOX'] = f"""
    QCheckBox {{
        color: {COLORS['text']};
        font-size: 14px;
        font-weight: 600;
        spacing: 8px;
        padding: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 24px;
        height: 24px;
        border: 2px solid {COLORS['accent']};
        border-radius: 12px;
        background-color: transparent;
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['accent']};
        image: url(images/check.png);
    }}
    
    QCheckBox::indicator:unchecked:hover {{
        border-color: {COLORS['button_hover']};
    }}
    
    QCheckBox::indicator:checked:hover {{
        background-color: {COLORS['button_hover']};
    }}
"""

# Update spectrogram and audiogram styles with modern aesthetics
STYLES['SPECTROGRAM'] = f"""
    QWidget {{
        background-color: {COLORS['background']};
        border: 2px solid {COLORS['accent']};
        border-radius: 15px;
        padding: 15px;
    }}
"""

STYLES['SPECTROGRAM_PLOT'] = {
    'facecolor': COLORS['background'],
    'text_color': COLORS['text'],
    'grid_color': f"{COLORS['accent']}33",  # 20% opacity
    'spine_color': COLORS['accent'],
    'title_size': 12,
    'label_size': 10,
    'tick_size': 8
}

STYLES['AUDIOGRAM'] = f"""
    QWidget {{
        background: linear-gradient(135deg, 
            {COLORS['background']}, 
            {COLORS['secondary']});
        border: 2px solid {COLORS['accent']};
        border-radius: 20px;
        padding: 20px;
    }}
    
    QLabel {{
        color: {COLORS['text']};
        font-size: 14px;
        font-weight: bold;
    }}
    
    QPushButton {{
        background-color: {COLORS['button']};
        color: {COLORS['text']};
        border: none;
        border-radius: 10px;
        padding: 8px 15px;
        font-weight: bold;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['button_hover']};
    }}
"""

STYLES['SPECTROGRAM'] = f"""
    QWidget {{
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        background-color: rgba(26, 27, 30, 0.8);
        backdrop-filter: blur(10px);
    }}
"""

STYLES['SPECTROGRAM_PLOT'] = {
    'facecolor': 'none',  # Transparent background
    'text_color': COLORS['text'],
    'grid_color': f"{COLORS['accent']}33",  # 20% opacity
    'spine_color': COLORS['accent'],
    'title_size': 12,
    'label_size': 10,
    'tick_size': 8
}

# Update spectrogram style to ensure transparency
STYLES['SPECTROGRAM'] = f"""
    QWidget {{
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        background-color: rgba(26, 27, 30, 0.8);
        backdrop-filter: blur(10px);
    }}
"""

STYLES['AUDIOGRAM'] = f"""
    QWidget {{
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        background-color: rgba(26, 27, 30, 0.8);
        backdrop-filter: blur(10px);
    }}
"""

STYLES['SLIDERS_PANEL'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border-radius: 15px;
        border: 1px solid {COLORS['accent']};
        padding: 10px;
    }}
    QLabel {{
        color: {COLORS['text']};
        font-size: 12px;
        font-weight: bold;
        padding: 5px;
    }}
"""

STYLES['SLIDER'] = f"""
    QSlider {{
        margin: 10px;
    }}
    QSlider::groove:horizontal {{
        border: none;
        height: 6px;
        background: {COLORS['background']};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {COLORS['accent']};
        border: none;
        width: 18px;
        height: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {COLORS['button_hover']};
    }}
"""

STYLES['SLIDERS_CONTAINER'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border: 1px solid {COLORS['accent']};
        border-radius: 15px;
        padding: 10px;
        margin: 10px 0px;
    }}
    QLabel {{
        color: {COLORS['text']};
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 5px;
    }}
"""

def apply_fonts(self):
    """Apply consistent fonts throughout the application"""
    # Force font database update
    QtGui.QFontDatabase.addApplicationFont(":/fonts/segoe-ui.ttf")
    
    # Default application font - set it on the QApplication instance
    app = QtWidgets.QApplication.instance()
    default_font = QtGui.QFont(FONT_STYLES['REGULAR']['family'].split(',')[0])
    default_font.setPointSize(FONT_STYLES['REGULAR']['size'])
    app.setFont(default_font)
    
    # Headings
    heading_font = QtGui.QFont(FONT_STYLES['HEADING']['family'].split(',')[0])
    heading_font.setPointSize(FONT_STYLES['HEADING']['size'])
    heading_font.setBold(True)
    for label in [self.modeLabel, self.originalSignal, self.filteredSignal]:
        label.setFont(heading_font)
        label.style().unpolish(label)  # Force style refresh
        label.style().polish(label)
    
    # Buttons with bold font
    button_font = QtGui.QFont(FONT_STYLES['BUTTON']['family'].split(',')[0])
    button_font.setPointSize(FONT_STYLES['BUTTON']['size'])
    button_font.setBold(True)
    for button in [self.browseFile, self.playPause, self.resetButton, 
                  self.zoomIn, self.zoomOut, self.speedUp, self.speedDown,
                  self.playOriginalSignal, self.playFilteredSignal, self.exportButton]:
        button.setFont(button_font)
        button.style().unpolish(button)  # Force style refresh
        button.style().polish(button)

    # ComboBox with larger bold font
    combo_font = QtGui.QFont(FONT_STYLES['REGULAR']['family'].split(',')[0], 14)
    combo_font.setBold(True)
    self.modeList.setFont(combo_font)
    self.modeList.style().unpolish(self.modeList)
    self.modeList.style().polish(self.modeList)



class Ui_MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.current_mode = "Musical Instruments"
        self.frequency_scale = "Linear"
        self.signalData = ""
        self.signalTime = ""
        self.modifiedData = self.signalData
        self.signalTimer = QTimer()
        self.signalTimeIndex = 0
        self.domain="Time Domain"
        self.cached= False
        
        self.instrument_ranges = {
            "Trumpet": [(0, 500)],      # Low frequency range
            "Xylophone": [(500, 1200)],     # Mid frequency range
            "Brass": [(1200, 6400)], # Upper mid range
            "Celesta": [(4000, 13000)] # High frequency range
        }

        # Animal sounds matching dataset ranges
        self.animal_ranges = {
            "Dogs": [(0, 450)],        # Low frequency range
            "Wolves": [(450, 1100)],   # Mid frequency range
            "Crow": [(1100, 3000)],    # High frequency range
            "Bat": [(3000, 9000)]      # Ultrasonic range
        }

        # ECG ranges matching dataset
        

        self.ecg_ranges = {
            "Normal": [(0, 1000)],  # Normal ECG range
            "Atrial Fibrillation": [(15, 20)],  # Atrial Fibrillation range
            "Atrial Flutter": [(2, 8)],  # Atrial Flutter range
            "Ventricular fibrillation": [(0, 5)]  # Ventricular fibrillation range
        }

        self.sliders = []   
        self.sliderLabels = []

        self.lastLoadedSignal = None
        self.lastModifiedSignal = None

        


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
        self.sideBarFrame.setStyleSheet(STYLES['PANEL'])

        self.verticalGraphs.setSpacing(20)
        self.horizontalLayout.setSpacing(15)
        self.mainbody.setContentsMargins(20, 20, 20, 20)

        # Add smooth animations
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def LoadSignalFile(self):
        print("Lets Choose a file")
        file_path = ""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Signal File", "", 
                                                "File Extension (*.wav *.mp3 *.csv)", 
                                                options=options)
        
        if file_path:
            try:
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
                self.playOriginalSignal.setText("Play Audio")
                self.playFilteredSignal.setIcon(self.playIcon)
                self.playFilteredSignal.setText("Play Audio")
                
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

                # Update UI
                signalPlotting(self) 
                plotSpectrogram(self)
                updateEqualization(self)
                changeMode(self, self.current_mode)
                
                # Store references
                self.lastLoadedSignal = np.copy(self.signalData)
                self.lastModifiedSignal = np.copy(self.signalData)
                
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Error loading file: {str(e)}")
            
            finally:
                self.loadingSpinner.hide()

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
        self.sideBarFrame = QtWidgets.QFrame(self.centralwidget)
        self.sideBarFrame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['secondary']};
                border-radius: 15px;
                margin: 5px;
                padding: 10px;
            }}
        """)
        self.sideBarFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sideBarFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sideBarFrame.setObjectName("sideBarFrame")
        self.sideBarFrame.setMinimumWidth(350)
        
        # put it as layout
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.sideBarFrame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        
        
        self.browseFile = QtWidgets.QPushButton(self.sideBarFrame)
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.browseFile.setFont(font)
        self.browseFile.setStyleSheet("QPushButton{\n"
        "    background-color: transparent;\n"
        "    border-radius: 10px;\n"
        "    color:white;\n"
        "    border: 2px solid white;\n"
        "    font-size: 20px;\n"
        "padding: 10px;\n"
        "\n"
        "}\n"
        "\n"
        "")
        self.browseFile.setIcon(self.uploadIcon)
        self.browseFile.setIconSize(QtCore.QSize(25, 25))
        self.browseFile.setObjectName("browseFile")
        self.browseFile.clicked.connect(self.LoadSignalFile)
        self.verticalLayout_2.addWidget(self.browseFile)
        
        
        self.frequencyDomainButton = QtWidgets.QPushButton(self.sideBarFrame)
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.frequencyDomainButton.setFont(font)
        # Style frequency domain toggle button
        self.frequencyDomainButton.setStyleSheet(STYLES['TOGGLE_BUTTON'])
        self.frequencyDomainButton.setCheckable(True)
        self.frequencyDomainButton.setIcon(self.signalIcon)
        self.frequencyDomainButton.setIconSize(QtCore.QSize(25, 25))
        self.frequencyDomainButton.setObjectName("Toggle frequency domain")
        self.verticalLayout_2.addWidget(self.frequencyDomainButton)
        self.frequencyDomainButton.clicked.connect(lambda : self.audiogramWidget.toggleShape())



    
        
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        
        self.line_9 = QtWidgets.QFrame(self.sideBarFrame)
        self.line_9.setStyleSheet("/* Line style */\n"
        "  width: 20px;\n"
        "  height: 5px;\n"
        "  background-color: rgb(39, 44, 54);\n"
        "  border: 10px;\n"
        "  border-radius:5px;\n"
        "")
        self.line_9.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_9.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_9.setObjectName("line_9")
        self.verticalLayout_2.addWidget(self.line_9)
        
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        
        
        self.setup_mode_selection()

        # Check Box for Spectogram
        self.spectogramCheck = QtWidgets.QCheckBox(self.sideBarFrame)
        font = QtGui.QFont()
        font.setFamily("Overpass SemiBold")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.spectogramCheck.setFont(font)
        self.spectogramCheck.setStyleSheet("QCheckBox {\n"
        "    spacing: 10px;\n"
        "color:white;\n"
        "background: rgba(74, 74, 74, 0);\n"
        "margin-top: 12px;\n"
        "}\n"
        "\n"
        "QCheckBox::indicator {\n"
        "    width: 15px; /* Adjust the width of the checkbox indicator */\n"
        "    height: 15px; /* Adjust the height of the checkbox indicator */\n"
        "border-radius: 5px;\n"
        "}\n"
        "\n"
        "QCheckBox::indicator:unchecked {\n"
        "    border: 2px solid #555; /* Border color of the unchecked checkbox */\n"
        "    background-color: #fff; /* Background color of the unchecked checkbox */\n"
        "}\n"
        "\n"
        "QCheckBox::indicator:unchecked:hover {\n"
        "    border: 2px solid #777; /* Border color when the unchecked checkbox is hovered */\n"
        "}\n"
        "\n"
        "QCheckBox::indicator:checked {\n"
        "    border: 2px solid #192462; /* Border color of the checked checkbox */\n"
        "    background-color: #405cf5; /* Background color of the checked checkbox */\n"
        "}\n"
        "\n"
        "QCheckBox::indicator:checked:hover {\n"
        "    border: 2px solid #0C1231; /* Border color when the checked checkbox is hovered */\n"
        "    background-color: #2C40AB; /* Background color when the checked checkbox is hovered */\n"
        "}\n"
        "")
        self.spectogramCheck.setIconSize(QtCore.QSize(20, 20))
        self.spectogramCheck.setTristate(False)
        self.spectogramCheck.setObjectName("spectogramCheck")
        self.spectogramCheck.stateChanged.connect(lambda : toggleVisibility(self))
        self.verticalLayout_2.addWidget(self.spectogramCheck)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        
        
        
        self.line_10 = QtWidgets.QFrame(self.sideBarFrame)
        self.line_10.setStyleSheet("/* Line style */\n"
        "  width: 20px;\n"
        "  height: 5px;\n"
        "  background-color:rgb(39, 44, 54);\n"
        "  border: 10px;\n"
        "  border-radius:5px;\n"
        "")
        self.line_10.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_10.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_10.setObjectName("line_10")
        self.verticalLayout_2.addWidget(self.line_10)
        
        
        
        self.originalSignal = QtWidgets.QLabel(self.sideBarFrame)
        font = QtGui.QFont()
        font.setFamily("Overpass SemiBold")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.originalSignal.setFont(font)
        self.originalSignal.setStyleSheet("color:rgb(255, 255, 255);\n"
                "background: rgba(74, 74, 74, 0);\n"
                "margin-top: 10px;\n"
                "margin-bottom:0;")
        self.originalSignal.setObjectName("audioBefore")
        self.verticalLayout_2.addWidget(self.originalSignal)
        
        
        self.audio1 = QtWidgets.QWidget(self.sideBarFrame)
        self.audio1.setStyleSheet("margin:0 0;")
        self.audio1.setObjectName("audio1")
        self.verticalLayout_2.addWidget(self.audio1)
        self.playOriginalSignal = QtWidgets.QPushButton(self.sideBarFrame)
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.playOriginalSignal.setFont(font)
        self.playOriginalSignal.setStyleSheet("QPushButton{\n"
                "background-color: #062e51;\n"
                "border-radius: 6px;\n"
                "border: 2px solid white;\n"
                "color: #fff;\n"
                "cursor: pointer;\n"
                "font-family: -apple-system,system-ui,\"Segoe UI\",Roboto,\"Helvetica Neue\",Ubuntu,sans-serif;\n"
                "font-size: 100%;\n"
                "}\n"
                "QPushButton:hover{\n"
                "background-color: #283999;\n"
                "}\n"
                "QPushButton:pressed{\n"
                "background-color: #1c2973;\n"
                "}")

        self.playOriginalSignal.setStyleSheet(STYLES['BUTTON'])
        self.playOriginalSignal.setIcon(self.playIcon)
        self.playOriginalSignal.setIconSize(QtCore.QSize(25, 25))
        self.playOriginalSignal.setObjectName("playAudio1")
        self.verticalLayout_2.addWidget(self.playOriginalSignal)
        
        
        self.filteredSignal = QtWidgets.QLabel(self.sideBarFrame)

        font = QtGui.QFont()
        font.setFamily("Overpass SemiBold")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.filteredSignal.setFont(font)
        self.filteredSignal.setStyleSheet("color:rgb(255, 255, 255);\n"
                "background: rgba(74, 74, 74, 0);\n"
                "margin-top: 10px;"
        )
        self.filteredSignal.setObjectName("Filtered Signal")
        self.verticalLayout_2.addWidget(self.filteredSignal)
        self.audio2 = QtWidgets.QWidget(self.sideBarFrame)
        self.audio2.setStyleSheet("margin:0 0;")
        self.audio2.setObjectName("audio2")
        self.verticalLayout_2.addWidget(self.audio2)
        
        
        self.playFilteredSignal = QtWidgets.QPushButton(self.sideBarFrame)
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.playFilteredSignal.setFont(font)
        self.playFilteredSignal.setStyleSheet("QPushButton{\n"
                "background-color: #062e51;\n"
                "border-radius: 6px;\n"
                "color: #fff;\n"
                "border: 2px solid white;\n"
                "cursor: pointer;\n"
                "font-family: -apple-system,system-ui,\"Segoe UI\",Roboto,\"Helvetica Neue\",Ubuntu,sans-serif;\n"
                "font-size: 100%;\n"
                "}\n"
                "QPushButton:hover{\n"
                "background-color: #283999;\n"
                "}\n"
                "QPushButton:pressed{\n"
                "background-color: #1c2973;\n"
        "}")
        self.playFilteredSignal.setStyleSheet(STYLES['BUTTON'])
        self.playFilteredSignal.setIcon(self.playIcon)
        self.playFilteredSignal.setIconSize(QtCore.QSize(25, 25))
        self.playFilteredSignal.setObjectName("playAudio2")

        # Some Spacing to add margin effect
        self.verticalLayout_2.addWidget(self.playFilteredSignal)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem4)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem5)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem6)
        spacerItem7 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem7)
        
        
        # ----- Export Button ----- #
        self.exportButton = QtWidgets.QPushButton(self.sideBarFrame)
        self.exportButton.setStyleSheet("QPushButton{\n"
                "    background-color: transparent;\n"
                "    border-radius: 10px;\n"
                "    color:white;\n"
                "    border: 2px solid white;\n"
                "    font-size: 20px;\n"
                "padding: 10px;\n"
                "\n"
                "}\n"
        "")
        self.exportButton.setObjectName("Export Signal")
        self.exportButton.setIcon(self.exportIcon)
        self.exportButton.setIconSize(QtCore.QSize(25, 25))
        self.verticalLayout_2.addWidget(self.exportButton)
        self.exportButton.clicked.connect(lambda : export_signal(self))



        self.gridLayout.addWidget(self.sideBarFrame, 0, 0, 1, 1)
    
        
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
        

        # viewbox1 = self.graph1.getViewBox()
        # viewbox2 = self.graph2.getViewBox()

        # # Connect the ViewBox signals in both directions
        # viewbox1.sigRangeChanged.connect(lambda window, viewRange: self.sync_pan(viewbox1, viewbox2))
        # viewbox2.sigRangeChanged.connect(lambda window, viewRange: self.sync_pan(viewbox2, viewbox1))


        self.controlButtonsLayout = QtWidgets.QHBoxLayout()
        self.controlButtonsLayout.setAlignment(QtCore.Qt.AlignCenter)  # Center alignment

        self.playPause = QtWidgets.QPushButton(self.mainBodyframe)
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(14)
        font.setBold(True)
        self.playPause.setFont(font)
        self.playPause.setStyleSheet(STYLES['BUTTON'])
        self.playPause.setIcon(self.stopIcon)
        self.playPause.setIconSize(QtCore.QSize(15, 15))
        self.playPause.setObjectName("playPause")
        self.playPause.clicked.connect(lambda: togglePlaying(self))

        self.resetButton = QtWidgets.QPushButton(self.mainBodyframe)
        self.resetButton.setFont(font)
        self.resetButton.setStyleSheet(STYLES['BUTTON'])
        self.resetButton.setIcon(self.replayIcon)
        self.resetButton.setIconSize(QtCore.QSize(15, 15))
        self.resetButton.clicked.connect(lambda: resetSignal(self))

        # Zoom buttons
        self.zoomIn = QtWidgets.QPushButton(self.mainBodyframe)
        self.zoomIn.setStyleSheet(STYLES['BUTTON'])
        self.zoomIn.setIcon(self.zoomInIcon)
        self.zoomIn.setIconSize(QtCore.QSize(15, 15))
        self.zoomIn.clicked.connect(lambda: zoomingIn(self))

        self.zoomOut = QtWidgets.QPushButton(self.mainBodyframe)
        self.zoomOut.setStyleSheet(STYLES['BUTTON'])
        self.zoomOut.setIcon(self.zoomOutIcon)
        self.zoomOut.setIconSize(QtCore.QSize(15, 15))
        self.zoomOut.clicked.connect(lambda: zoomingOut(self))


        # Speed Up button
        self.speedUp = QtWidgets.QPushButton(self.mainBodyframe)
        self.speedUp.setStyleSheet(STYLES['BUTTON'])
        self.speedUp.setIcon(self.speedUpIcon)
        self.speedUp.setIconSize(QtCore.QSize(15, 15))
        self.speedUp.clicked.connect(lambda: speedingUp(self))

        # Speed Down button
        self.speedDown = QtWidgets.QPushButton(self.mainBodyframe)
        self.speedDown.setStyleSheet(STYLES['BUTTON'])
        self.speedDown.setIcon(self.speedDownIcon)
        self.speedDown.setIconSize(QtCore.QSize(15, 15))
        self.speedDown.clicked.connect(lambda: speedingDown(self))


        self.deleteButton = QtWidgets.QPushButton(self.mainBodyframe)
        self.deleteButton.setStyleSheet(STYLES['BUTTON'])
        self.deleteButton.setIcon(self.deleteIcon)
        self.deleteButton.setIconSize(QtCore.QSize(15, 15))
        self.deleteButton.clicked.connect(lambda: speedingDown(self))
        self.deleteButton.clicked.connect(lambda: deleteSignal(self))        

        # Add buttons vertically
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



        
        # Create Spectrogram Layout (can be toggled)
        self.spectrogramLayout = QtWidgets.QHBoxLayout()
        self.spectrogramLayout.setObjectName("spectrogramLayout")
        self.spectrogramLayout.setSpacing(20)
        self.spectrogramLayout.setContentsMargins(10, 10, 10, 10)




        # First Spectrogram
        self.firstSpectrogramFig = Figure(figsize=(10, 10))
        self.firstSpectrogramFig.patch.set_alpha(0.0)  # Make figure background transparent
        self.firstGraphCanvas = FigureCanvas(self.firstSpectrogramFig)
        self.firstGraphCanvas.setFixedHeight(200)
        self.firstGraphAxis = self.firstSpectrogramFig.add_subplot(111)
        self.firstGraphAxis.patch.set_alpha(0.0)  # Make plot background transparent
        self.firstGraphAxis.patch.set_facecolor('none')
        
        # Second Spectrogram
        self.secondSpectrogramFig = Figure(figsize=(10, 10))
        self.secondSpectrogramFig.patch.set_alpha(0.0)  # Make figure background transparent
        self.secondGraphCanvas = FigureCanvas(self.secondSpectrogramFig)
        self.secondGraphCanvas.setFixedHeight(200)
        self.secondGraphAxis = self.secondSpectrogramFig.add_subplot(111)
        self.secondGraphAxis.patch.set_alpha(0.0)  # Make plot background transparent
        self.secondGraphAxis.patch.set_facecolor('none')

        

        # Configure spectrogram plots with enhanced styling
        for ax in [self.firstGraphAxis, self.secondGraphAxis]:
            ax.set_facecolor('none')  # Transparent background
            ax.tick_params(
                colors=STYLES['SPECTROGRAM_PLOT']['text_color'],
                labelsize=STYLES['SPECTROGRAM_PLOT']['tick_size']
            )
            ax.grid(True, 
                    color=STYLES['SPECTROGRAM_PLOT']['grid_color'],
                    linestyle='--',
                    alpha=0.5)
            
            # Style labels and title
            ax.xaxis.label.set_color(STYLES['SPECTROGRAM_PLOT']['text_color'])
            ax.yaxis.label.set_color(STYLES['SPECTROGRAM_PLOT']['text_color'])
            ax.title.set_color(STYLES['SPECTROGRAM_PLOT']['text_color'])
            ax.title.set_size(STYLES['SPECTROGRAM_PLOT']['title_size'])
            
            # Style spines
            for spine in ax.spines.values():
                spine.set_color(STYLES['SPECTROGRAM_PLOT']['spine_color'])
                spine.set_linewidth(2)

        # Create container for spectrograms with matching background
        self.spectrogramContainer = QtWidgets.QWidget(self.mainBodyframe)
        self.spectrogramContainer.setFixedHeight(250)
        self.spectrogramContainer.setStyleSheet(STYLES['SPECTROGRAM'])
        self.spectrogramContainer.setContentsMargins(20, 20, 20, 20)
        self.spectrogramLayout.addWidget(self.firstGraphCanvas)
        self.spectrogramLayout.addWidget(self.secondGraphCanvas)
        self.spectrogramContainer.setLayout(self.spectrogramLayout)
        self.verticalGraphs.addWidget(self.spectrogramContainer)



        # Update stretch factors
        self.verticalGraphs.setStretch(0, 1)  # Time domain graphs
        self.verticalGraphs.setStretch(1, 1)  # First separator
        self.verticalGraphs.setStretch(2, 1)  # Audiogram
        self.verticalGraphs.setStretch(3, 1)  # Second separator
        self.verticalGraphs.setStretch(4, 1)  # Spectrograms

        # Style the first spectrogram
        self.firstGraphAxis.set_facecolor(COLORS['background'])
        self.firstSpectrogramFig.patch.set_facecolor(COLORS['secondary'])
        self.firstGraphAxis.tick_params(colors=COLORS['text'])
        self.firstGraphAxis.xaxis.label.set_color(COLORS['text'])
        self.firstGraphAxis.yaxis.label.set_color(COLORS['text'])
        for spine in self.firstGraphAxis.spines.values():
            spine.set_color(COLORS['accent'])

        # Style the second spectrogram
        self.secondGraphAxis.set_facecolor(COLORS['background'])
        self.secondSpectrogramFig.patch.set_facecolor(COLORS['secondary'])
        self.secondGraphAxis.tick_params(colors=COLORS['text'])
        self.secondGraphAxis.xaxis.label.set_color(COLORS['text'])
        self.secondGraphAxis.yaxis.label.set_color(COLORS['text'])
        for spine in self.secondGraphAxis.spines.values():
            spine.set_color(COLORS['accent'])




        # Add another line separator
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




        self.audiogramContainer = QtWidgets.QWidget(self.mainBodyframe)
        self.audiogramContainer.setStyleSheet(STYLES['AUDIOGRAM'])
        self.audiogramContainer.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, 
            QtWidgets.QSizePolicy.Expanding
        )
        self.audiogramContainer.setMinimumSize(800, 300)

        # Create layout with zero margins
        self.audiogramLayout = QVBoxLayout(self.audiogramContainer)
        self.audiogramLayout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        self.audiogramLayout.setSpacing(0)  # Remove spacing between widgets

        # Add to main layout
        self.verticalGraphs.addWidget(self.audiogramContainer)




        # Add sliders section
        # Create floating slider window
        self.sliderWindow = SliderWindow()
        self.sliderWindow.resize(300, 400)  # Set initial size

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
        self.modeList.currentTextChanged.connect(lambda text: changeMode(self, text))
        self.apply_modern_styles()
        apply_fonts(self)


        # Connect audio buttons
        self.playOriginalSignal.clicked.connect(lambda : playOriginalAudio(self))
        self.playFilteredSignal.clicked.connect(lambda : playFilteredAudio(self))
        
        # Add stop button functionality to export button (or add a new stop button)
        self.exportButton.clicked.connect(lambda : stopAudio(self))

        # Add loading spinner
        self.loadingSpinner = QtWidgets.QProgressBar(self.sideBarFrame)
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

        self.spectrogramLayout.setSpacing(20)
        self.spectrogramLayout.setContentsMargins(20, 20, 20, 20)
        self.audiogramLayout.setSpacing(15)
        self.audiogramLayout.setContentsMargins(0, 20, 0, 0)

        # Add button to show/hide slider window
        self.toggleSlidersButton = QtWidgets.QPushButton(self.sideBarFrame)
        self.toggleSlidersButton.setText("Show/Hide Equalizer")
        self.toggleSlidersButton.setStyleSheet(STYLES['BUTTON'])
        self.toggleSlidersButton.clicked.connect(lambda: self.sliderWindow.setVisible(
            not self.sliderWindow.isVisible()
        ))
        self.verticalLayout_2.addWidget(self.toggleSlidersButton)


        
    # Update the mode selection section styling
    def setup_mode_selection(self):
        # Mode selection container
        self.modeSelectionContainer = QtWidgets.QWidget(self.sideBarFrame)
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
            "Musical Instruments",
            "Animal Sounds", 
            "Uniform Range",
            "ECG Abnormalities"
        ])
        
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
        self.verticalLayout_2.addWidget(self.modeSelectionContainer)

        # Connect signal
        self.modeList.currentTextChanged.connect(lambda text: changeMode(self, text))

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
        self.originalSignal.setText(_translate("MainWindow", "Original Signal"))
        self.playOriginalSignal.setText(_translate("MainWindow", "Play Audio"))
        self.filteredSignal.setText(_translate("MainWindow", "Filtered Signal"))
        self.playFilteredSignal.setText(_translate("MainWindow", "Play Audio"))
        self.exportButton.setText(_translate("MainWindow", "Export Signal"))
    
    
class SliderWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        # Main layout with margins for shadow effect
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Main container with glass effect
        self.mainContainer = QtWidgets.QWidget()
        self.mainContainer.setObjectName("mainContainer")
        self.mainContainerLayout = QtWidgets.QVBoxLayout(self.mainContainer)
        self.mainContainerLayout.setSpacing(15)
        
        # Title bar
        self.titleBar = QtWidgets.QWidget()
        self.titleBar.setFixedHeight(50)
        self.titleBarLayout = QtWidgets.QHBoxLayout(self.titleBar)
        self.titleBarLayout.setContentsMargins(15, 5, 15, 5)
        
        # Title label with icon
        self.titleLabel = QtWidgets.QLabel("Equalizer")
        self.titleLabel.setStyleSheet(f"""
            color: {COLORS['text']};
            font-weight: bold;
            font-size: 16px;
            padding: 5px;
        """)
        
        # Add equalizer icon
        titleIcon = QtGui.QPixmap("images/equalizer.png")  # Add an equalizer icon
        titleIcon = titleIcon.scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.iconLabel = QtWidgets.QLabel()
        self.iconLabel.setPixmap(titleIcon)
        
        # Close button
        self.closeButton = QtWidgets.QPushButton("×")
        self.closeButton.setFixedSize(30, 30)
        self.closeButton.clicked.connect(self.hide)
        self.closeButton.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['error']};
                color: white;
                border-radius: 15px;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #ff6b6b;
                transform: scale(1.1);
            }}
        """)
        
        # Add widgets to title bar
        self.titleBarLayout.addWidget(self.iconLabel)
        self.titleBarLayout.addWidget(self.titleLabel)
        self.titleBarLayout.addStretch()
        self.titleBarLayout.addWidget(self.closeButton)
        
        # Separator line
        self.separator = QtWidgets.QFrame()
        self.separator.setFrameShape(QtWidgets.QFrame.HLine)
        self.separator.setStyleSheet(f"""
            background-color: {COLORS['accent']};
            border: none;
            height: 2px;
            margin: 0 10px;
        """)
        
        # Container for sliders
        self.slidersContainer = QtWidgets.QWidget()
        self.slidersLayout = QtWidgets.QVBoxLayout(self.slidersContainer)
        self.slidersLayout.setSpacing(15)
        self.slidersLayout.setContentsMargins(15, 15, 15, 15)
        
        # Add all widgets to main container
        self.mainContainerLayout.addWidget(self.titleBar)
        self.mainContainerLayout.addWidget(self.separator)
        self.mainContainerLayout.addWidget(self.slidersContainer)
        
        # Add main container to layout
        self.layout.addWidget(self.mainContainer)
        
        # Style the window
        self.setStyleSheet(f"""
            QWidget#mainContainer {{
                background-color: {COLORS['secondary']};
                border: 1px solid {COLORS['accent']};
                border-radius: 15px;
            }}
            
            QLabel {{
                color: {COLORS['text']};
                font-size: 14px;
            }}
            
            QSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background: {COLORS['background']};
                border-radius: 3px;
                margin: 0 5px;
            }}
            
            QSlider::handle:horizontal {{
                background: {COLORS['accent']};
                border: none;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            
            QSlider::handle:horizontal:hover {{
                background: {COLORS['button_hover']};
                transform: scale(1.1);
            }}
            
            QSlider {{
                height: 30px;
            }}
        """)
        
        self.oldPos = None
        self.setMinimumWidth(300)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.titleBar.rect().contains(event.pos()):
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos:
            delta = event.globalPos() - self.oldPos
            self.move(self.pos() + delta)
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.oldPos = None

    def addSlider(self, label, min_val, max_val, value):
        sliderWidget = QtWidgets.QWidget()
        sliderLayout = QtWidgets.QVBoxLayout(sliderWidget)
        sliderLayout.setSpacing(5)
        
        # Header layout for label and value
        headerLayout = QtWidgets.QHBoxLayout()
        
        # Label
        labelWidget = QtWidgets.QLabel(label)
        labelWidget.setStyleSheet(f"""
            color: {COLORS['text']};
            font-weight: bold;
        """)
        
        # Value label - Make this local instead of class member
        valueLabel = QtWidgets.QLabel(f"{value}")  # Changed from self.valueLabel
        valueLabel.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-weight: bold;
        """)
        
        headerLayout.addWidget(labelWidget)
        headerLayout.addStretch()
        headerLayout.addWidget(valueLabel)
        
        # Slider
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(value)
        
        # Update value label when slider moves - now updates correct label
        slider.valueChanged.connect(lambda v: valueLabel.setText(f"{v}"))
        
        sliderLayout.addLayout(headerLayout)
        sliderLayout.addWidget(slider)
        
        self.slidersLayout.addWidget(sliderWidget)
        return slider




if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    from equalizer_functions import changeMode, updateEqualization, signalPlotting, plotSpectrogram
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
    ui.current_mode = "Musical Instruments"
    
    # Initialize audiogram
    ui.audiogramWidget = Audiogram(
        ui.signalTime, 
        ui.signalData, 
        ui.modifiedData
    )
    ui.audiogramLayout.addWidget(ui.audiogramWidget)

    # Create initial sliders
    max_freq = ui.samplingRate // 2
    band_width = max_freq / 10
    ranges = {f"Band {i}": [(i*band_width, (i+1)*band_width)] for i in range(10)}
    createSliders(ui, ranges)

    MainWindow.show()
    sys.exit(app.exec_())


