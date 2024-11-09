from PyQt5 import QtCore, QtGui, QtWidgets
import librosa
from pyqtgraph import PlotWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QLayout , QVBoxLayout , QHBoxLayout, QGridLayout ,QWidget, QFileDialog, QPushButton, QColorDialog, QInputDialog, QComboBox, QDialog
from scipy.io import wavfile
import numpy as np
import pandas as pd

#import Resources_rc

class Ui_MainWindow(QMainWindow):


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1329, 911)
        MainWindow.setStyleSheet("background-color: #1b1d23;color:white;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")

        # ------------------------------ Icons ---------------------------- #
        uploadIcon = QtGui.QIcon("Images/upload.png")
        playIcon = QtGui.QIcon("Images/play.png")
        stopIcon = QtGui.QIcon("Images/pause.png")
        signalIcon = QtGui.QIcon("Images/signal.png")
        replayIcon = QtGui.QIcon("Images/replay.png")
        speedUpIcon = QtGui.QIcon("Images/up.png")
        speedDownIcon = QtGui.QIcon("Images/down.png")
        zoomInIcon = QtGui.QIcon("Images/zoom_in.png")
        zoomOutIcon = QtGui.QIcon("Images/zoom_out.png")
        exportIcon = QtGui.QIcon("Images/file.png")

        # --------------------------- Important Attributes --------------------------- #
        self.equalizerMode= "Musical Instruments"
        self.signalData = ""
        self.signalTimer = QTimer()
        self.signalTimeIndex = 0



        # ---------------------- Setup the side bar ---------------------- #
        self.sideBarFrame = QtWidgets.QFrame(self.centralwidget)
        self.sideBarFrame.setStyleSheet("\n"
        "   /*border: 1px solid #c0c0c0; /* Border color and width */\n"
        "    padding: 5px; /* Padding around the list items */\n"
        "background-color: #1b1d23;\n"
        "border: 1px solid rgba(255, 255, 255, 0);\n"
        "")
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
        self.browseFile.setIcon(uploadIcon)
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
        self.frequencyDomainButton.setIcon(signalIcon)
        self.frequencyDomainButton.setIconSize(QtCore.QSize(25, 25))
        self.frequencyDomainButton.setObjectName("frequency domain")
        self.verticalLayout_2.addWidget(self.frequencyDomainButton)
        
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
        self.spectogramCheck.stateChanged.connect(self.toggleVisibility)
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
        self.playOriginalSignal.setIcon(playIcon)
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
        self.playFilteredSignal.setIcon(playIcon)
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
        self.exportButton.setIcon(exportIcon)
        self.exportButton.setIconSize(QtCore.QSize(25, 25))
        self.verticalLayout_2.addWidget(self.exportButton)



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
        self.graph1 = PlotWidget(self.mainBodyframe)
        self.graph1.setBackground("transparent")
        self.graph1.setObjectName("graph1")
        self.graph1.showGrid(x=True, y=True)
        self.graph1.setStyleSheet("border-radius: 6px;border: 2px solid white;")
        self.horizontalLayout.addWidget(self.graph1)
        
        # Normal Graph 2
        self.graph2 = PlotWidget(self.mainBodyframe)
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
        self.playPause.setIcon(playIcon)
        self.playPause.setIconSize(QtCore.QSize(25, 25))
        self.playPause.setObjectName("playPause")
        self.playPause.clicked.connect(self.togglePlaying)
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
        self.resetButton.setIcon(replayIcon)
        self.resetButton.setIconSize(QtCore.QSize(25, 25))
        self.resetButton.setObjectName("resetButton")
        self.resetButton.clicked.connect(self.resetSignal)
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
       
        self.zoomIn.setIcon(zoomInIcon)
        self.zoomIn.setIconSize(QtCore.QSize(25, 25))
        self.zoomIn.setObjectName("zoomIn")
        self.horizontalLayout_4.addWidget(self.zoomIn)
        
        
        
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
        self.zoomOut.setIcon(zoomOutIcon)
        self.zoomOut.setIconSize(QtCore.QSize(25, 25))
        self.zoomOut.setObjectName("zoomOut")
        self.horizontalLayout_4.addWidget(self.zoomOut)
        
        
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
        self.speedUp.setIcon(speedUpIcon)
        self.speedUp.setIconSize(QtCore.QSize(25, 25))
        self.horizontalLayout_3.addWidget(self.speedUp)\
        
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
        self.speedDown.setIcon(speedDownIcon)
        self.speedDown.setIconSize(QtCore.QSize(25, 25))
        self.horizontalLayout_3.addWidget(self.speedDown)
        
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
        self.firstSpectrogramFig = Figure(figsize=(5, 4))
        self.firstGraphCanvas = FigureCanvas(self.firstSpectrogramFig)
        self.firstGraphAxis = self.firstSpectrogramFig.add_subplot(111)
        self.firstGraphAxis.set_facecolor('white')
        self.firstSpectrogramFig.patch.set_facecolor('#282c37')
        self.firstGraphAxis.plot([0, 1, 2, 3], [10, 1, 20, 3]) 
        self.spectogram1 = QtWidgets.QWidget(self.mainBodyframe)
        self.spectogram1.setStyleSheet("border-radius: 6px;\n"
        "background: rgba(74, 74, 74, 0);")
        self.spectogram1.setObjectName("spectogram1")
        self.firstGraphCanvas.draw()
        self.spectrogramLayout.addWidget(self.firstGraphCanvas)
        


        
        # Second Spectrogram Widget
        self.spectogram2 = QtWidgets.QWidget(self.mainBodyframe)
        self.spectogram2.setStyleSheet("border-radius: 6px;\n""background: rgba(74, 74, 74, 0);")
        self.spectogram2.setObjectName("spectogram2")
        self.secondSpectrogramFig = Figure(figsize=(5, 4))
        self.secondGraphCanvas = FigureCanvas(self.secondSpectrogramFig)
        self.secondGraphAxis = self.secondSpectrogramFig.add_subplot(111)
        self.secondGraphAxis.set_facecolor('white')
        self.secondSpectrogramFig.patch.set_facecolor('#282c37')
        self.secondGraphAxis.plot([0, 1, 2, 3], [10, 1, 20, 3]) 
        """ ----------- Place Here the matplotlib for the Spectrogram ----------- """
        self.secondGraphCanvas.draw()
        self.spectrogramLayout.addWidget(self.secondGraphCanvas)
        
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
        
        self.verticalSlider = QtWidgets.QSlider(self.slidersWidget)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.horizontalLayout_5.addWidget(self.verticalSlider)
        
        self.verticalSlider_2 = QtWidgets.QSlider(self.slidersWidget)
        self.verticalSlider_2.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_2.setObjectName("verticalSlider_2")
        self.horizontalLayout_5.addWidget(self.verticalSlider_2)
        
        self.verticalSlider_3 = QtWidgets.QSlider(self.slidersWidget)
        self.verticalSlider_3.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_3.setObjectName("verticalSlider_3")
        self.horizontalLayout_5.addWidget(self.verticalSlider_3)
        
        self.verticalSlider_4 = QtWidgets.QSlider(self.slidersWidget)
        self.verticalSlider_4.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_4.setObjectName("verticalSlider_4")
        self.horizontalLayout_5.addWidget(self.verticalSlider_4)
        
        self.verticalSlider_5 = QtWidgets.QSlider(self.slidersWidget)
        self.verticalSlider_5.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_5.setObjectName("verticalSlider_5")
        self.horizontalLayout_5.addWidget(self.verticalSlider_5)
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



    def resetSignal(self):
        self.signalTimer.stop()
        self.signalTimeIndex = 0
        self.signalPlotting()

    def toggleVisibility(self):
        if self.secondGraphCanvas.isVisible() and self.firstGraphCanvas.isVisible():
            self.secondGraphCanvas.hide()
            self.firstGraphCanvas.hide()
        else:
            self.firstGraphCanvas.show()
            self.secondGraphCanvas.show()


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

        self.signalPlotting()    




    def signalPlotting(self):
        self.graph2.plot(self.signalTime ,self.signalData, pen='b')  # Add name parameter for legend
        self.graph1.clear()
        self.signalTimer.stop()
        self.signalTimeIndex = 0

        self.signalTimer.timeout.connect(self.updateSignalPlotting)
        self.signalTimer.start(0)
        


        #self.graph1.plot(self.signalTime, self.signalData, pen='b', name='Data')
    def updateSignalPlotting(self):
        self.windowSize = 2  # The window size in terms of time (5 units of time)
        
        # Get the current time based on the latest index
        current_time = self.signalTime[self.signalTimeIndex]
        
        # Calculate the start time of the window (5 units before the current time)
        start_time = current_time - self.windowSize
        if start_time < self.signalTime[0]:  # Ensure the start time doesn't go before the first data point
            start_time = self.signalTime[0]
        
        # Get the relevant data points within the time window
        start_index = next(i for i, t in enumerate(self.signalTime) if t >= start_time)
        end_index = self.signalTimeIndex + 100  # Include the current time point
        
        # Clear the graph before plotting new data
        self.graph1.clear()

        # Plot the data within the time window (from start_index to end_index)
        self.graph1.plot(self.signalTime[start_index:end_index], 
                        self.signalData[start_index:end_index], 
                        pen='b', name='Data')

        # Increment signalTimeIndex to the next data point
        self.signalTimeIndex += 10

        # Stop the timer and reset the index if we reach the end of the data
        if self.signalTimeIndex >= len(self.signalData):
            self.signalTimer.stop()  # Stop the signal timer
            self.signalTimeIndex = 0  # Reset the index to start from the beginning

        # Set the X-range to zoom in on the most recent `windowSize` data points based on time
        if self.signalTimeIndex > self.windowSize:
            pass
        else:
            self.graph1.setXRange(0, self.windowSize, padding=0)

        self.graph1.setYRange(min(self.signalData) , max(self.signalData), padding=0)

    def togglePlaying(self):
        if self.signalTimer.isActive():
            self.signalTimer.stop()
            self.playPause.setIcon(self.playIcon)
        else:
            self.signalTimer.start(0)
            self.playPause.setIcon(self.stopIcon)

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
    MainWindow.show()
    sys.exit(app.exec_())
