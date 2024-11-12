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
from equalizer_functions import changeMode, updateEqualization, toggleFrequencyScale, playOriginalAudio, playFilteredAudio, toggleVisibility, togglePlaying, resetSignal, stopAudio, signalPlotting , zoomingIn , zoomingOut , speedingUp , speedingDown , toggleFreqDomain , plotSpectrogram, export_signal 
from audiogram import Audiogram
import sys
import os
#import Resources_rc
# Add these color constants at the start of setupUi
COLORS = {
    'background': '#1E1E2E',  # Dark background
    'secondary': '#252535',   # Slightly lighter background
    'accent': '#7AA2F7',     # Soft blue accent
    'text': '#CDD6F4',       # Soft white text
    'button': '#394168',     # Button background
    'button_hover': '#4A5178' # Button hover
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

# Update fonts
FONT_FAMILY = "Segoe UI"  # Modern system font
def setup_fonts(self):
    font = QtGui.QFont(FONT_FAMILY)
    font.setPointSize(10)
    self.setFont(font)
    
    title_font = QtGui.QFont(FONT_FAMILY)
    title_font.setPointSize(12)
    title_font.setBold(True)
    self.modeLabel.setFont(title_font)

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
        
        
        # Frequency ranges for different instruments (Hz)
        self.instrument_ranges = {
            "Guitar": [(0, 170)],
            "Flute": [(170, 250)],
            "Harmonica": [(250, 400)],
            "Xylophone": [(400, 1000)]  
        }
        
        # Frequency ranges for animal sounds (Hz)
        self.animal_ranges = {
            "Dog": [(500, 1500)],
            "Cat": [(400, 1000)],
            "Bird": [(2000, 8000)],
            "Cow": [(100, 600)]
        }
        
        # Frequency ranges for ECG abnormalities
        self.ecg_ranges = {
            "Normal": [(0.5, 40)],
            "Tachycardia": [(60, 100)],
            "Bradycardia": [(30, 60)],
            "Arrhythmia": [(100, 150)]
        }

        self.sliders = []   
        self.sliderLabels = []

        


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
        self.firstGraphCanvas.setStyleSheet(STYLES['GRAPH'])
        self.secondGraphCanvas.setStyleSheet(STYLES['GRAPH'])
        
        # Checkbox
        self.spectogramCheck.setStyleSheet(STYLES['CHECKBOX'])
        
        # Main frame
        self.mainBodyframe.setStyleSheet(f"""
            background-color: {COLORS['background']};
            border-radius: 15px;
            margin: 10px;
        """)

    def LoadSignalFile(self):
        print("Lets Choose a file")
        file_path= ""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Signal File", "", "File Extension (*.wav *.mp3 *.csv)", options=options)
        
        # Get the extension of the file
        extension = file_path.split(".")[-1]
        self.samplingRate = 0
        if extension == "wav" or extension == "mp3":
            self.signalData, self.samplingRate = librosa.load(file_path)
            duration = librosa.get_duration(y=self.signalData, sr=self.samplingRate)
            self.signalTime = np.linspace(0, duration, len(self.signalData))

        elif extension == "csv":
            fileData = pd.read_csv(
                file_path, delimiter=',', skiprows=1)  # Skip header row
            self.signalTime = np.array(fileData.iloc[:, 0].astype(float).tolist())
            self.signalData = np.array(fileData.iloc[:, 1].astype(float).tolist())
            self.samplingRate = 1 / np.mean(np.diff(self.signalTime))
            self.speed = 3

        # Fixed code
        if isinstance(self.modifiedData, str) or len(getattr(self.modifiedData, 'shape', [])) == 0:
            self.modifiedData = self.signalData

        signalPlotting(self) 
        plotSpectrogram(self)
        updateEqualization(self)
        changeMode(self, self.current_mode)

    
    def openFrequencyDomainWindow(self):
        print("Opening Frequency Domain Window")
        domainWindow = Audiogram(self.signalTime, self.signalData, self.modifiedData)
        domainWindow.show()
        domainWindow.exec_()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1329, 911)
        MainWindow.setStyleSheet(f"""
    QMainWindow {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
    }}
""")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        # ------------------------------ Icons ---------------------------- #
        self.uploadIcon = QtGui.QIcon("images/upload.png")
        self.playIcon = QtGui.QIcon("images/play.png")
        self.stopIcon = QtGui.QIcon("images/pause.png")
        self.signalIcon = QtGui.QIcon("images/signal.png")
        self.replayIcon = QtGui.QIcon("images/replay.png")
        self.speedUpIcon = QtGui.QIcon("images/up.png")
        self.speedDownIcon = QtGui.QIcon("images/down.png")
        self.zoomInIcon = QtGui.QIcon("images/zoom_in.png")
        self.zoomOutIcon = QtGui.QIcon("images/zoom_out.png")
        self.exportIcon = QtGui.QIcon("images/file.png")

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
        self.frequencyDomainButton.setStyleSheet("QPushButton{\n"
        "    background-color: transparent;\n"
        "    border-radius: 10px;\n"
        "    color:white;\n"
        "    border: 2px solid white;\n"
        "    font-size: 20px;\n"
        "padding: 10px;\n"
        "}"
        "")
        self.frequencyDomainButton.setIcon(self.signalIcon)
        self.frequencyDomainButton.setIconSize(QtCore.QSize(25, 25))
        self.frequencyDomainButton.setObjectName("frequency domain")
        self.verticalLayout_2.addWidget(self.frequencyDomainButton)
        self.frequencyDomainButton.clicked.connect(lambda : self.openFrequencyDomainWindow())


        
    
        
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
        
        
        self.modeLabel = QtWidgets.QLabel(self.sideBarFrame)
        font = QtGui.QFont()
        font.setFamily("Overpass SemiBold")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.modeLabel.setFont(font)
        self.modeLabel.setStyleSheet("color:rgb(255, 255, 255);\n"
        "background: rgba(74, 74, 74, 0);\n"
        "margin-top: 10px;\n"
        "font-size: 20px;")
        self.modeLabel.setObjectName("modeLabel")
        self.verticalLayout.addWidget(self.modeLabel)


        self.modeList = QtWidgets.QComboBox(self.sideBarFrame)
        self.modeList.setStyleSheet("QComboBox {\n"
        "    font-family: \"Overpass\";\n"
        "    font-weight: bold;\n"
        "    font-size: 16px;\n"
        "    color: white; \n"
        "    border: 2px solid white; \n"
        "    border-radius: 10px;\n"
        "padding: 10px;\n"
        "}\n"
        "")
        self.modeList.setObjectName("modeList")
        self.modeList.addItem("Musical Instruments")
        self.modeList.addItem("Animal Sounds")
        self.modeList.addItem("Uniform Range")
        self.modeList.addItem("ECG Abnormalities")
        self.verticalLayout.addWidget(self.modeList)
        self.verticalLayout_2.addLayout(self.verticalLayout)

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
        # Main Body Frame
        self.mainBodyframe = QtWidgets.QFrame(self.centralwidget)
        self.mainBodyframe.setStyleSheet("background-color: #282c37;\n")
        self.mainBodyframe.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.mainBodyframe.setFrameShadow(QtWidgets.QFrame.Raised)
        self.mainBodyframe.setObjectName("mainBodyframe")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.mainBodyframe)
        self.gridLayout_3.setObjectName("gridLayout_3")
        # Main Body Layout
        self.mainbody = QtWidgets.QVBoxLayout()
        self.mainbody.setContentsMargins(10, -1, 10, -1)
        self.mainbody.setSpacing(6)
        self.mainbody.setObjectName("mainbody")
        # Layuot for Graphs in the same row.
        self.verticalGraphs = QtWidgets.QVBoxLayout()
        self.verticalGraphs.setSpacing(20)
        self.verticalGraphs.setObjectName("verticalGraphs")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(20)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        
        # Normal Graph 1
        self.graph1 = pg.PlotWidget(self.mainBodyframe)
        self.graph1.setBackground("transparent")
        self.graph1.setObjectName("graph1")
        self.graph1.showGrid(x=True, y=True)
        self.graph1.setStyleSheet("border-radius: 6px;border: 2px solid white;")
        self.horizontalLayout.addWidget(self.graph1)
        
        # Normal Graph 2
        self.graph2 = pg.PlotWidget(self.mainBodyframe)
        self.graph2.setBackground("transparent")
        self.graph2.showGrid(x=True, y=True)
        self.graph2.setObjectName("graph2")
        self.graph2.setStyleSheet("border-radius: 6px;border: 2px solid white;")
        self.horizontalLayout.addWidget(self.graph2)
        
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem8)
        
        
        #self.graph1.getViewBox().sigRangeChanged.connect(lambda viewbox, viewrect: self.sync_pan(viewbox, viewrect))
        #self.graph2.getViewBox().sigRangeChanged.connect(lambda viewbox, viewrect: self.sync_pan(viewbox, viewrect))
        self.graph2.getViewBox().sigRangeChanged.connect(
            lambda viewbox, rect: self.sync_pan(viewbox, self.graph1.getViewBox())
        )
        self.graph1.getViewBox().sigRangeChanged.connect(
            lambda viewbox, rect: self.sync_pan(viewbox, self.graph2.getViewBox())
        )
        self.playPause = QtWidgets.QPushButton(self.mainBodyframe)
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.playPause.setFont(font)
        self.playPause.setStyleSheet("QPushButton{\n"
        "background-color: #062e51;\n"
        "border-radius: 6px;\n"
        "color: #fff;\n"
        "cursor: pointer;\n"
        "border: 2px solid white;\n"
        "font-family: -apple-system,system-ui,\"Segoe UI\",Roboto,\"Helvetica Neue\",Ubuntu,sans-serif;\n"
        "font-size: 100%;\n"
        "padding: 10px;\n"
        "}\n"
        "QPushButton:hover{\n"
        "background-color: #283999;\n"
        "}\n"
        "QPushButton:pressed{\n"
        "background-color: #1c2973;\n"
        "}")
        self.playPause.setIcon(self.stopIcon)
        self.playPause.setIconSize(QtCore.QSize(25, 25))
        self.playPause.setObjectName("playPause")
        self.playPause.clicked.connect(lambda : togglePlaying(self))
        self.horizontalLayout_4.addWidget(self.playPause)
        self.resetButton = QtWidgets.QPushButton(self.mainBodyframe)
        
        
        
        
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.resetButton.setFont(font)
        self.resetButton.setStyleSheet("QPushButton{\n"
        "background-color: #062e51;\n"
        "border-radius: 6px;\n"
        "color: #fff;\n"
        "border: 2px solid white;\n"
        "cursor: pointer;\n"
        "font-family: -apple-system,system-ui,\"Segoe UI\",Roboto,\"Helvetica Neue\",Ubuntu,sans-serif;\n"
        "font-size: 100%;\n"
        "padding: 10px;\n"
        "}\n"
        "QPushButton:hover{\n"
        "background-color: #283999;\n"
        "}\n"
        "QPushButton:pressed{\n"
        "background-color: #1c2973;\n"
        "}")
        self.resetButton.setIcon(self.replayIcon)
        self.resetButton.setIconSize(QtCore.QSize(25, 25))
        self.resetButton.setObjectName("resetButton")
        self.resetButton.clicked.connect(lambda : resetSignal(self))
        self.horizontalLayout_4.addWidget(self.resetButton)
        
        
        
        self.zoomIn = QtWidgets.QPushButton(self.mainBodyframe)
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.zoomIn.setFont(font)
        self.zoomIn.setStyleSheet("QPushButton{\n"
        "background-color: #062e51;\n"
        "border-radius: 6px;\n"
        "color: #fff;\n"
        "border: 2px solid white;\n"
        "cursor: pointer;\n"
        "font-family: -apple-system,system-ui,\"Segoe UI\",Roboto,\"Helvetica Neue\",Ubuntu,sans-serif;\n"
        "font-size: 100%;\n"
        "padding: 10px;\n"
        "}\n"
        "QPushButton:hover{\n"
        "background-color: #283999;\n"
        "}\n"
        "QPushButton:pressed{\n"
        "background-color: #1c2973;\n"
        "}")
       
        self.zoomIn.setIcon(self.zoomInIcon)
        self.zoomIn.setIconSize(QtCore.QSize(25, 25))
        self.zoomIn.setObjectName("zoomIn")
        self.horizontalLayout_4.addWidget(self.zoomIn)
        self.zoomIn.clicked.connect(lambda :zoomingIn(self))
        
        
        self.zoomOut = QtWidgets.QPushButton(self.mainBodyframe)
        font = QtGui.QFont()
        font.setFamily("-apple-system")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.zoomOut.setFont(font)
        self.zoomOut.setStyleSheet("QPushButton{\n"
        "background-color: #062e51;\n"
        "border-radius: 6px;\n"
        "color: #fff;\n"
        "cursor: pointer;\n"
        "font-family: -apple-system,system-ui,\"Segoe UI\",Roboto,\"Helvetica Neue\",Ubuntu,sans-serif;\n"
        "font-size: 100%;\n"
        "border: 2px solid white;\n"
        "padding: 10px;\n"
        "}\n"
        "QPushButton:hover{\n"
        "background-color: #283999;\n"
        "}\n"
        "QPushButton:pressed{\n"
        "background-color: #1c2973;\n"
        "}")
        self.zoomOut.setText("")
        self.zoomOut.setIcon(self.zoomOutIcon)
        self.zoomOut.setIconSize(QtCore.QSize(25, 25))
        self.zoomOut.setObjectName("zoomOut")
        self.horizontalLayout_4.addWidget(self.zoomOut)
        self.zoomOut.clicked.connect(lambda :zoomingOut(self))
        
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(3)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        
        self.speedUp = QtWidgets.QPushButton(self.mainBodyframe)
        self.speedUp.setStyleSheet("QPushButton{\n"
                "background-color: #062e51;\n"
                "border-radius: 6px;\n"
                "color: #fff;\n"
                "cursor: pointer;\n"
                "font-family: -apple-system,system-ui,\"Segoe UI\",Roboto,\"Helvetica Neue\",Ubuntu,sans-serif;\n"
                "font-size: 16px;\n"
                "font-weight:bold;\n"
                "padding: 8px;\n"
                "border: 2px solid white;\n"
                "margin: 10px;\n"
                "}\n"
                "QPushButton:hover{\n"
                "background-color: #283999;\n"
                "}\n"
                "QPushButton:pressed{\n"
                "background-color: #1c2973;\n"
        "}")
        self.speedUp.setObjectName("pushButton_2")
        self.speedUp.setIcon(self.speedUpIcon)
        self.speedUp.setIconSize(QtCore.QSize(25, 25))
        self.horizontalLayout_3.addWidget(self.speedUp)
        self.speedUp.clicked.connect(lambda :speedingUp(self))

        self.speedDown = QtWidgets.QPushButton(self.mainBodyframe)
        self.speedDown.setStyleSheet("QPushButton{\n"
                "background-color: #062e51;\n"
                "border-radius: 6px;\n"
                "color: #fff;\n"
                "cursor: pointer;\n"
                "font-family: -apple-system,system-ui,\"Segoe UI\",Roboto,\"Helvetica Neue\",Ubuntu,sans-serif;\n"
                "font-size: 16px;\n"
                "font-weight:bold;\n"
                "padding: 8px;\n"
                "border: 2px solid white;\n"
                "margin: 10px;\n"
                "}\n"
                "QPushButton:hover{\n"
                "background-color: #283999;\n"
                "}\n"
                "QPushButton:pressed{\n"
                "background-color: #1c2973;\n"
                "}")
        self.speedDown.setObjectName("pushButton_3")
        self.speedDown.setIcon(self.speedDownIcon)
        self.speedDown.setIconSize(QtCore.QSize(25, 25))
        self.horizontalLayout_3.addWidget(self.speedDown)
        self.speedDown.clicked.connect(lambda :speedingDown(self))

        spacerItem9 = QtWidgets.QSpacerItem(200, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem9)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem10)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem11)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem12)



        self.horizontalLayout_4.addLayout(self.horizontalLayout_3)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.verticalGraphs.addLayout(self.verticalLayout_3)
        self.line_8 = QtWidgets.QFrame(self.mainBodyframe)
        self.line_8.setStyleSheet("/* Line style */\n"
        "\n"
        "  /* Set the width of the line */\n"
        "  width: 20px;\n"
        "\n"
        "  /* Set the height of the line */\n"
        "  height: 5px;\n"
        "\n"
        "  /* Set the background color of the line */\n"
        "  background-color: #3a3b3c;\n"
        "\n"
        "  /* Set the border of the line */\n"
        "  border: 10px;\n"
        "\n"
        "  /* Set the border radius of the line */\n"
        "  border-radius:5px;\n"
        "\n"
        "\n"
        "\n"
        "")
        self.line_8.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.verticalGraphs.addWidget(self.line_8)
        
        # Spectrogram Layout
        self.spectrogramLayout = QtWidgets.QHBoxLayout()
        self.spectrogramLayout.setObjectName("spectrogramLayout")
        self.spectrogramLayout.setSpacing(20)  # Add spacing between spectrograms
        self.spectrogramLayout.setContentsMargins(10, 10, 10, 10)  # Add margins

        # First Spectrogram
        self.firstSpectrogramFig = Figure(figsize=(5, 4))
        self.firstGraphCanvas = FigureCanvas(self.firstSpectrogramFig)
        self.firstGraphCanvas.setStyleSheet(STYLES['SPECTROGRAM'])
        self.firstGraphAxis = self.firstSpectrogramFig.add_subplot(111)

        # Style the first spectrogram
        self.firstGraphAxis.set_facecolor(COLORS['background'])
        self.firstSpectrogramFig.patch.set_facecolor(COLORS['secondary'])
        self.firstGraphAxis.tick_params(colors=COLORS['text'])
        self.firstGraphAxis.xaxis.label.set_color(COLORS['text'])
        self.firstGraphAxis.yaxis.label.set_color(COLORS['text'])
        for spine in self.firstGraphAxis.spines.values():
            spine.set_color(COLORS['accent'])

        # Create container for first spectrogram
        self.spectogram1 = QtWidgets.QWidget(self.mainBodyframe)
        self.spectogram1.setStyleSheet(STYLES['SPECTROGRAM'])
        self.firstGraphCanvas.draw()
        self.spectrogramLayout.addWidget(self.firstGraphCanvas)

        # Second Spectrogram
        self.secondSpectrogramFig = Figure(figsize=(5, 4))
        self.secondGraphCanvas = FigureCanvas(self.secondSpectrogramFig)
        self.secondGraphCanvas.setStyleSheet(STYLES['SPECTROGRAM'])
        self.secondGraphAxis = self.secondSpectrogramFig.add_subplot(111)

        # Style the second spectrogram
        self.secondGraphAxis.set_facecolor(COLORS['background'])
        self.secondSpectrogramFig.patch.set_facecolor(COLORS['secondary'])
        self.secondGraphAxis.tick_params(colors=COLORS['text'])
        self.secondGraphAxis.xaxis.label.set_color(COLORS['text'])
        self.secondGraphAxis.yaxis.label.set_color(COLORS['text'])
        for spine in self.secondGraphAxis.spines.values():
            spine.set_color(COLORS['accent'])

        # Create container for second spectrogram
        self.spectogram2 = QtWidgets.QWidget(self.mainBodyframe)
        self.spectogram2.setStyleSheet(STYLES['SPECTROGRAM'])
        self.secondGraphCanvas.draw()
        self.spectrogramLayout.addWidget(self.secondGraphCanvas)

        # Add spectrograms to main layout
        self.verticalGraphs.addLayout(self.spectrogramLayout)
        self.verticalGraphs.setStretch(0, 2)
        self.verticalGraphs.setStretch(1, 1)
        self.verticalGraphs.setStretch(2, 2)
        self.mainbody.addLayout(self.verticalGraphs)
        self.slidersWidget = QtWidgets.QWidget(self.mainBodyframe)
        self.slidersWidget.setStyleSheet("background: rgba(74, 74, 74, 0);\n""")
        self.slidersWidget.setObjectName("slidersWidget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.slidersWidget)
        self.horizontalLayout_5.setSpacing(6)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")


        self.mainbody.addWidget(self.slidersWidget)
        self.mainbody.setStretch(0, 4)
        self.mainbody.setStretch(1, 1)
        self.gridLayout_3.addLayout(self.mainbody, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.mainBodyframe, 0, 1, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 6)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1329, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.modeList.currentTextChanged.connect(lambda text: changeMode(self, text))

        # Connect audio buttons
        self.playOriginalSignal.clicked.connect(lambda : playOriginalAudio(self))
        self.playFilteredSignal.clicked.connect(lambda : playFilteredAudio(self))
        
        # Add stop button functionality to export button (or add a new stop button)
        self.exportButton.clicked.connect(lambda : stopAudio(self))

        self.apply_modern_styles()
        setup_fonts(self)


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
        self.frequencyDomainButton.setText(_translate("MainWindow", "Frequency Domain"))
        self.modeLabel.setText(_translate("MainWindow", "Choose The Mode"))
        self.spectogramCheck.setText(_translate("MainWindow", "Hide The Spectograms"))
        self.originalSignal.setText(_translate("MainWindow", "Original Signal"))
        self.playOriginalSignal.setText(_translate("MainWindow", "Play Audio"))
        self.filteredSignal.setText(_translate("MainWindow", "Filtered Signal"))
        self.playFilteredSignal.setText(_translate("MainWindow", "Play Audio"))
        self.exportButton.setText(_translate("MainWindow", "Export Signal"))
        self.playPause.setText(_translate("MainWindow", "Play/Pause"))
        self.resetButton.setText(_translate("MainWindow", "Reset"))
        self.speedUp.setText(_translate("MainWindow", "Speed Up"))
        self.speedDown.setText(_translate("MainWindow", "Speed Down"))
    
    
    




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    # open the file dialog
    ui.browseFile.click()
    signalPlotting(ui)
    plotSpectrogram(ui)
    updateEqualization(ui)
    changeMode(ui, ui.current_mode)

    MainWindow.show()
    sys.exit(app.exec_())


