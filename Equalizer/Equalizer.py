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
        margin: 0px;
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
        padding: 0px;
        margin: 0px 0px;
    }}
    QLabel {{
        color: {COLORS['text']};
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 5px;
    }}
"""


STYLES['SPECTROGRAM_AXES'] = {
    'grid_alpha': 0.2,
    'grid_color': COLORS['text'],
    'label_color': COLORS['text'],
    'tick_color': COLORS['text'],
    'title_color': COLORS['text'],
    'spine_color': COLORS['accent']
}

STYLES['SLIDERS_CONTAINER'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border: 2px solid {COLORS['accent']};
        border-radius: 20px;
        padding: 15px;
        margin: 10px 0px;
    }}
"""

STYLES['SLIDER'] = f"""
    QSlider {{
        height: 50px;
        margin: 10px;
    }}
    
    QSlider::groove:horizontal {{
        border: none;
        height: 4px;
        background: {COLORS['background']};
        border-radius: 2px;
        margin: 0px;
    }}
    
    QSlider::handle:horizontal {{
        background: {COLORS['accent']};
        border: 2px solid {COLORS['accent']};
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 10px;
        transition: background-color 0.2s;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {COLORS['button_hover']};
        border-color: {COLORS['button_hover']};
        transform: scale(1.1);
    }}
    
    QSlider::sub-page:horizontal {{
        background: {COLORS['accent']};
        border-radius: 2px;
    }}
"""

STYLES['SLIDER_LABEL'] = f"""
    QLabel {{
        color: {COLORS['text']};
        font-size: 13px;
        font-weight: bold;
        padding: 5px;
    }}
"""

STYLES['SLIDER_VALUE'] = f"""
    QLabel {{
        color: {COLORS['accent']};
        font-size: 12px;
        font-weight: bold;
        padding: 2px 8px;
        background: rgba(114, 137, 218, 0.1);
        border-radius: 10px;
    }}
"""

STYLES['SLIDERS_CONTAINER'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border: 1px solid {COLORS['accent']};
        border-radius: 12px;
        padding: 0px;
        margin: 2px 0px;
    }}
"""

STYLES['PANEL'] = f"""
    QFrame {{
        background-color: rgba(42, 43, 46, 0.7);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
    }}
"""

STYLES['PANEL'] = f"""
    QFrame {{
        background-color: rgba(42, 43, 46, 0.7);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
    }}
"""

STYLES['SCROLL_AREA'] = f"""
    QScrollArea {{
        border: none;
        background-color: transparent;
        margin: 0px;
        padding: 0px;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    
    QScrollBar:vertical {{
        border: none;
        background: {COLORS['secondary']};
        width: 6px;
        margin: 0px;
        border-radius: 3px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {COLORS['accent']};
        min-height: 20px;
        border-radius: 3px;
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
"""

STYLES['SIDEBAR'] = f"""
    QFrame {{
        background-color: {COLORS['secondary']};
        border-radius: 15px;
        padding:5px;
    }}
"""

STYLES['SIDEBAR_SECTION'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border-radius: 12px;
        padding: 0px;
        margin: 0px 0px;
    }}
"""

STYLES['SECTION_TITLE'] = f"""
    QLabel {{
        color: {COLORS['text']};
        font-size: 16px;
        font-weight: 500;
        letter-spacing: 0.5px;
        padding:0px 0px 0px 0px;
        margin: 0;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
        border-bottom: 1px solid {COLORS['accent']};
        border-bottom:0px;
        border-radius: 0px;
    }}
    QLabel:hover {{
        color: {COLORS['accent']};
    }}
"""

STYLES['DIVIDER'] = f"""
    QFrame {{
        background-color: {COLORS['accent']};
        border: none;
        height: 1px;
        margin: 10px 0px;
    }}
"""

# 1. Add hover tooltips for better usability
TOOLTIPS = {
    'browse': "Click to load an audio file (supports .wav, .mp3, .csv)",
    'freq_domain': "Toggle between time and frequency domain visualization",
    'mode': "Select equalizer mode for different frequency presets",
    'spectogram': "Toggle spectrogram visibility",
    'play_original': "Play the original unmodified audio",
    'play_filtered': "Play the audio with current equalizer settings",
    'export': "Export the modified audio as a new file",
    'zoom_in': "Zoom in on the signal view",
    'zoom_out': "Zoom out of the signal view",
    'speed_up': "Increase playback speed",
    'speed_down': "Decrease playback speed",
    'reset': "Reset all equalizer settings"
}

# 2. Add loading animations
LOADING_STYLE = f"""
    QProgressBar {{
        border: 2px solid {COLORS['accent']};
        border-radius: 8px;
        text-align: center;
        color: {COLORS['text']};
        background-color: {COLORS['secondary']};
    }}
    QProgressBar::chunk {{
        background-color: {COLORS['accent']};
        width: 10px; 
        margin: 0.5px;
    }}
"""

# 3. Add keyboard shortcuts
SHORTCUTS = {
    'play': 'Space',
    'reset': 'R',
    'zoom_in': 'Ctrl++',
    'zoom_out': 'Ctrl+-',
    'speed_up': ']',
    'speed_down': '['
}

# Add these graph style enhancements
GRAPH_STYLES = {
    'AXIS': {
        'color': COLORS['text'],
        'width': 1.5
    },
    'GRID': {
        'color': f"{COLORS['text']}33",  # 20% opacity
        'width': 0.5
    },
    'CURVE': {
        'original': {'color': '#7289DA', 'width': 2},
        'modified': {'color': '#43B581', 'width': 2}
    },
    'LABELS': {
        'color': COLORS['text'],
        'size': '12pt'
    },
    'BACKGROUND': 'transparent'
}



def setup_tooltips(self):
    """Add helpful tooltips to UI elements"""
    self.browseFile.setToolTip(TOOLTIPS['browse'])
    self.frequencyDomainButton.setToolTip(TOOLTIPS['freq_domain']) 
    self.modeList.setToolTip(TOOLTIPS['mode'])
    self.spectogramCheck.setToolTip(TOOLTIPS['spectogram'])
    self.playOriginalSignal.setToolTip(TOOLTIPS['play_original'])
    self.playFilteredSignal.setToolTip(TOOLTIPS['play_filtered'])
    self.exportButton.setToolTip(TOOLTIPS['export'])
    self.zoomIn.setToolTip(f"{TOOLTIPS['zoom_in']} ({SHORTCUTS['zoom_in']})")
    self.zoomOut.setToolTip(f"{TOOLTIPS['zoom_out']} ({SHORTCUTS['zoom_out']})")
    self.speedUp.setToolTip(f"{TOOLTIPS['speed_up']} ({SHORTCUTS['speed_up']})")
    self.speedDown.setToolTip(f"{TOOLTIPS['speed_down']} ({SHORTCUTS['speed_down']})")
    self.resetButton.setToolTip(f"{TOOLTIPS['reset']} ({SHORTCUTS['reset']})")

def setup_shortcuts(self):
    """Set up keyboard shortcuts"""
    QtWidgets.QShortcut(QtGui.QKeySequence("Space"), self.centralwidget, lambda: togglePlaying(self))
    QtWidgets.QShortcut(QtGui.QKeySequence("R"), self.centralwidget, lambda: resetSignal(self))
    QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl++"), self.centralwidget, lambda: zoomingIn(self))
    QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+-"), self.centralwidget, lambda: zoomingOut(self))
    QtWidgets.QShortcut(QtGui.QKeySequence("]"), self.centralwidget, lambda: speedingUp(self))
    QtWidgets.QShortcut(QtGui.QKeySequence("["), self.centralwidget, lambda: speedingDown(self))

def show_loading(self, message="Loading..."):
    """Show loading animation with message"""
    self.loadingSpinner.setFormat(message)
    self.loadingSpinner.show()
    QtWidgets.QApplication.processEvents()

def hide_loading(self):
    """Hide loading animation"""
    self.loadingSpinner.hide()

# 5. Add status messages
def show_status(self, message, duration=3000):
    """Show temporary status message"""
    self.statusbar = QtWidgets.QStatusBar()
    self.statusbar.setStyleSheet(f"""
        QStatusBar {{
            background: {COLORS['secondary']};
            color: {COLORS['text']};
            padding: 5px;
            border-top: 1px solid {COLORS['accent']};
        }}
    """)
    self.setStatusBar(self.statusbar)
    self.statusbar.showMessage(message, duration)

def setup_sidebar(self):
    # Main sidebar frame
    self.sideBarFrame.setStyleSheet(STYLES['SIDEBAR'])
    self.sideBarFrame.setMinimumWidth(350)
    self.verticalLayout_2.setSpacing(15)
    self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)

    # 1. File Section
    self.fileSection = QtWidgets.QWidget()
    fileLayout = QtWidgets.QVBoxLayout(self.fileSection)
    fileLayout.setSpacing(10)
    
    sectionTitle = QtWidgets.QLabel("File Operations")
    sectionTitle.setStyleSheet(STYLES['SECTION_TITLE'])
    fileLayout.addWidget(sectionTitle)
    
    self.browseFile.setStyleSheet(STYLES['BUTTON'])
    fileLayout.addWidget(self.browseFile)
    
    self.verticalLayout_2.addWidget(self.fileSection)

    # 2. View Controls Section
    self.viewSection = QtWidgets.QWidget()
    viewLayout = QtWidgets.QVBoxLayout(self.viewSection)
    viewLayout.setSpacing(10)
    
    viewTitle = QtWidgets.QLabel("View Controls")
    viewTitle.setStyleSheet(STYLES['SECTION_TITLE'])
    viewLayout.addWidget(viewTitle)
    
    # Add frequency domain toggle
    self.frequencyDomainButton.setStyleSheet(STYLES['TOGGLE_BUTTON'])
    viewLayout.addWidget(self.frequencyDomainButton)
    
    # Add spectrogram toggle
    self.spectogramCheck.setStyleSheet(STYLES['CHECKBOX'])
    viewLayout.addWidget(self.spectogramCheck)
    
    self.verticalLayout_2.addWidget(self.viewSection)

    # 3. Mode Selection Section
    self.modeSection = QtWidgets.QWidget()
    modeLayout = QtWidgets.QVBoxLayout(self.modeSection)
    modeLayout.setSpacing(10)
    
    self.modeLabel.setStyleSheet(STYLES['SECTION_TITLE'])
    modeLayout.addWidget(self.modeLabel)
    modeLayout.addWidget(self.modeList)
    
    self.verticalLayout_2.addWidget(self.modeSection)

    # 4. Equalizer Section
    self.equalizerSection = QtWidgets.QWidget()
    equalizerLayout = QtWidgets.QVBoxLayout(self.equalizerSection)
    equalizerLayout.setSpacing(10)
    
    eqTitle = QtWidgets.QLabel("Equalizer")
    eqTitle.setStyleSheet(STYLES['SECTION_TITLE'])
    equalizerLayout.addWidget(eqTitle)
    
    self.scrollArea.setStyleSheet(STYLES['SCROLL_AREA'])
    equalizerLayout.addWidget(self.scrollArea)
    
    self.verticalLayout_2.addWidget(self.equalizerSection)

    # 5. Playback Controls Section
    self.playbackSection = QtWidgets.QWidget()
    playbackLayout = QtWidgets.QVBoxLayout(self.playbackSection)
    playbackLayout.setSpacing(10)
    
    playbackTitle = QtWidgets.QLabel("Playback Controls")
    playbackTitle.setStyleSheet(STYLES['SECTION_TITLE'])
    playbackLayout.addWidget(playbackTitle)
    
    self.playOriginalSignal.setStyleSheet(STYLES['BUTTON'])
    self.playFilteredSignal.setStyleSheet(STYLES['BUTTON'])
    self.exportButton.setStyleSheet(STYLES['BUTTON'])
    playbackLayout.addWidget(self.playOriginalSignal)
    playbackLayout.addWidget(self.playFilteredSignal)

    playbackLayout.addWidget(self.exportButton)
    
    self.verticalLayout_2.addWidget(self.playbackSection)

    # Add stretcher at the bottom
    self.verticalLayout_2.addStretch()

def addDivider(self):
    divider = QtWidgets.QFrame()
    divider.setFrameShape(QtWidgets.QFrame.HLine)
    divider.setStyleSheet(STYLES['DIVIDER'])
    self.verticalLayout_2.addWidget(divider)

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
    for label in [self.modeLabel]:
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
            self.show_status(f"Time: {mouse_point.x():.3f}s, Amplitude: {mouse_point.y():.3f}")

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
                    changeMode(self, self.current_mode)
                
                # Store references
                self.lastLoadedSignal = np.copy(self.signalData)
                self.lastModifiedSignal = np.copy(self.modifiedData)
                show_status(self,"File loaded successfully")
                
            except Exception as e:
                show_status(self,f"Error: {str(e)}", 5000)
            
            finally:
                hide_loading(self)

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
        #self.verticalLayout_2.addWidget(self.browseFile)

        
        
        
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
        #self.verticalLayout_2.addWidget(self.frequencyDomainButton)
        self.frequencyDomainButton.clicked.connect(lambda : self.audiogramWidget.toggleShape())



    
        
        
        
        
        self.setup_mode_selection()

        # Check Box for Spectogram with reduced margins
        self.spectogramCheck = QtWidgets.QCheckBox(self.sideBarFrame)
        font = QtGui.QFont()
        font.setFamily("Overpass SemiBold")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.spectogramCheck.setFont(font)
        self.spectogramCheck.setStyleSheet(f"""
            QCheckBox {{
                spacing: 10px;
                color: {COLORS['text']};
                background: transparent;
                margin: 5px 0;
                padding: 5px 0;
            }}
            
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border-radius: 5px;
            }}
            
            QCheckBox::indicator:unchecked {{
                border: 2px solid #555;
                background-color: #fff;
            }}
            
            QCheckBox::indicator:unchecked:hover {{
                border: 2px solid #777;
            }}
            
            QCheckBox::indicator:checked {{
                border: 2px solid #192462;
                background-color: #405cf5;
            }}
            
            QCheckBox::indicator:checked:hover {{
                border: 2px solid #0C1231;
                background-color: #2C40AB;
            }}
        """)
        self.spectogramCheck.setIconSize(QtCore.QSize(20, 20))
        self.spectogramCheck.setTristate(False)
        self.spectogramCheck.setObjectName("spectogramCheck")
        self.spectogramCheck.stateChanged.connect(lambda : toggleVisibility(self))
        #self.verticalLayout_2.addWidget(self.spectogramCheck)

        
        
        
        self.playOriginalSignal = QtWidgets.QPushButton(self.sideBarFrame)
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.playOriginalSignal.setFont(font)

        self.playOriginalSignal.setStyleSheet(STYLES['BUTTON'])
        self.playOriginalSignal.setIcon(self.playIcon)
        self.playOriginalSignal.setIconSize(QtCore.QSize(25, 25))
        self.playOriginalSignal.setObjectName("playAudio1")
        #self.verticalLayout_2.addWidget(self.playOriginalSignal)
        

        
        
        self.playFilteredSignal = QtWidgets.QPushButton(self.sideBarFrame)
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.playFilteredSignal.setFont(font)
        self.playFilteredSignal.setStyleSheet(STYLES['BUTTON'])
        self.playFilteredSignal.setIcon(self.playIcon)
        self.playFilteredSignal.setIconSize(QtCore.QSize(25, 25))
        #self.playFilteredSignal.setObjectName("playAudio2")

        # Some Spacing to add margin effect
        #self.verticalLayout_2.addWidget(self.playFilteredSignal)

        # ----- Export Button ----- #
        self.exportButton = QtWidgets.QPushButton(self.sideBarFrame)
        self.exportButton.setObjectName("Export Signal")
        self.exportButton.setIcon(self.exportIcon)
        self.exportButton.setIconSize(QtCore.QSize(25, 25))
        #self.verticalLayout_2.addWidget(self.exportButton)
        #self.exportButton.clicked.connect(lambda : export_signal(self))

        



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
        

        viewbox1 = self.graph1.getViewBox()
        viewbox2 = self.graph2.getViewBox()

        # Connect the ViewBox signals in both directions
        viewbox1.sigRangeChanged.connect(lambda window, viewRange: self.sync_pan(viewbox1, viewbox2))
        viewbox2.sigRangeChanged.connect(lambda window, viewRange: self.sync_pan(viewbox2, viewbox1))


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
        
        # Create container with fixed size
        self.spectrogramContainer = QtWidgets.QWidget(self.mainBodyframe)
        self.spectrogramContainer.setFixedHeight(250)
        self.spectrogramContainer.setStyleSheet(STYLES['SPECTROGRAM'])
        self.spectrogramContainer.setLayout(self.spectrogramLayout)

        # Add to main layout
        self.verticalGraphs.addWidget(self.spectrogramContainer)




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

        self.slidersContainer = QtWidgets.QWidget(self.sideBarFrame)
        self.slidersContainer.setStyleSheet(STYLES['SLIDERS_CONTAINER'])
        self.slidersLayout = QtWidgets.QVBoxLayout(self.slidersContainer)
        self.slidersLayout.setSpacing(10)
        self.slidersLayout.setContentsMargins(0 , 0, 0, 0)

        # Create scroll area
        self.scrollArea = QtWidgets.QScrollArea(self.sideBarFrame)
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
        self.slidersInnerLayout = QtWidgets.QVBoxLayout(self.slidersInnerContainer)
        self.slidersInnerLayout.setSpacing(10)
        self.slidersInnerLayout.setContentsMargins(10, 10, 10, 10)

 

        # Add separator line
        # self.slidersSeparator = QtWidgets.QFrame()
        # self.slidersSeparator.setFrameShape(QtWidgets.QFrame.HLine)
        # self.slidersSeparator.setStyleSheet(f"""
        #     background-color: {COLORS['accent']};
        #     border: none;
        #     height: 2px;
        #     margin: 0 10px;
        # """)
        # self.slidersLayout.addWidget(self.slidersSeparator)

        # Set up scroll area
        self.scrollArea.setWidget(self.slidersInnerContainer)
        self.slidersLayout.addWidget(self.scrollArea)

        # Add sliders container to sidebar before the export button
        #self.verticalLayout_2.insertWidget(self.verticalLayout_2.count() - 1, self.slidersContainer)

        setup_sidebar(self)

        setup_tooltips(self)
        setup_shortcuts(self)
        
        # Add status bar
        show_status(self,"Ready")

        self.enhance_graphs()


        
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
        #self.verticalLayout_2.addWidget(self.modeSelectionContainer)

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
        
        self.playOriginalSignal.setText(_translate("MainWindow", "Play Original Audio"))
        self.playFilteredSignal.setText(_translate("MainWindow", "Play Filtered Audio"))
        self.exportButton.setText(_translate("MainWindow", "Export Signal"))
    
    



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
    changeMode(ui, ui.current_mode)

    MainWindow.show()
    sys.exit(app.exec_())

