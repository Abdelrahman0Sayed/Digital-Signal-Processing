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
from equalizer_functions import  updateEqualization, toggleFrequencyScale, playOriginalAudio, playFilteredAudio, toggleVisibility, togglePlaying, resetSignal, stopAudio, signalPlotting , zoomingIn , zoomingOut , speedingUp , speedingDown , toggleFreqDomain , plotSpectrogram, export_signal , deleteSignal
from audiogram import Audiogram
import sys
import os
from style import COLORS, STYLES, FONT_STYLES


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
    #self.sideBarScroll.setStyleSheet(STYLES['SIDEBAR'])
    self.sideBarScroll.setMinimumWidth(350)
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
