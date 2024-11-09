from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider
from PyQt5.QtGui import QIcon , QFont, QPixmap, QColor # Package to set an icon , fonts and images
from PyQt5.QtCore import Qt , QTimer  # used for alignments.
from PyQt5.QtWidgets import QLayout , QVBoxLayout , QHBoxLayout, QGridLayout ,QWidget, QFileDialog, QPushButton, QColorDialog, QInputDialog, QComboBox, QDialog
import pyqtgraph as pg
import random
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        uploadIcon = QtGui.QIcon("Images/upload.png")
        signalIcon = QtGui.QIcon("Images/signal.png")
        playIcon = QtGui.QIcon("Images/play.png")
        replayIcon = QtGui.QIcon("Images/replay.png")
        pauseIcon = QtGui.QIcon("Images/pause.png")
        zoomInIcon = QtGui.QIcon("Images/zoom_in.png")
        zoomOutIcon = QtGui.QIcon("Images/zoom_out.png")
        speedUpIcon = QtGui.QIcon("Images/up.png")
        speedDownIcon = QtGui.QIcon("Images/down.png")

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1500, 950)
        MainWindow.setStyleSheet("background-color: #1d2029;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setObjectName("widget")
        self.widget.setStyleSheet("""
            QWidget{
                Background-color: #15171e;
                color: white;
                margin-bottom:0;
            }
        """)
        self.widget.setMaximumWidth(400)

        self.gridLayout = QtWidgets.QVBoxLayout(self.widget)
        self.gridLayout.setObjectName("gridLayout")



        self.browseFileButton = QtWidgets.QPushButton(self.widget)
        self.browseFileButton.setObjectName("pushButton")
        self.browseFileButton.setStyleSheet("""
            QPushButton{
                Background-color: transparent;
                color: white;
                border: 2px solid white;
                border-radius: 10px;
                padding:10px;
                font-size:16px;
                font-weight: bold;
            }""")
        self.browseFileButton.setIcon(uploadIcon)
        self.browseFileButton.setIconSize(QtCore.QSize(20, 20))
        self.gridLayout.addWidget(self.browseFileButton)


        self.frequencyDomainButton = QtWidgets.QPushButton(self.widget)
        self.frequencyDomainButton.setObjectName("pushButton_2")
        self.frequencyDomainButton.setStyleSheet("""
            QPushButton{
                Background-color: transparent;
                color: white;
                border: 2px solid white;
                border-radius: 10px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 20px;
            }""")
        self.frequencyDomainButton.setIcon(signalIcon)
        self.frequencyDomainButton.setIconSize(QtCore.QSize(30, 30))
        self.gridLayout.addWidget(self.frequencyDomainButton)
        
        self.optionsLayout = QtWidgets.QVBoxLayout(self.widget)

        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.label.setMaximumHeight(60)
        self.label.setStyleSheet("font-size:20px;font-weight:bold;")
        self.optionsLayout.addWidget(self.label)


        self.comboBox = QtWidgets.QComboBox(self.widget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setStyleSheet("""
            QComboBox{
                background-color: transparent;                
                border: 2px solid white;
                border-radius:10px;
                color:white;    
                font-size:16px;
                padding:10px;
                font-weight: bold;
            }
        """)
        self.comboBox.addItem("Uniform Range")
        self.comboBox.addItem("Musical Instruments")
        self.comboBox.addItem("Animal Sounds")
        self.comboBox.addItem("ECG Abnormalities")

        self.optionsLayout.addWidget(self.comboBox)
        
        self.checkBox = QtWidgets.QCheckBox(self.widget)
        self.checkBox.setObjectName("checkBox")
        self.checkBox.setStyleSheet("""
            QComboBox{
                font-size:18px;
                margin-bottom:100px;
            }
        """)
        self.optionsLayout.addWidget(self.checkBox)

        
        self.line = QtWidgets.QFrame(self.widget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setStyleSheet("background-color: white;")
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line)


        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.label_2.setStyleSheet("""
            QLabel{
                font-size:16px;
                font-weight:bold;
                background-color:#282d3c;
                display:flex;
                justify-content:center;
                align-items:center;
                text-align:center;
            }
        """)
        self.label_2.setMaximumHeight(40)
        self.gridLayout.addWidget(self.label_2)
        self.horizontalSlider = QtWidgets.QSlider(self.widget)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setStyleSheet("""
            QSlider::groove{
                width: 20px;
            }
                                            QSlider{
                                            }
        """)
        self.gridLayout.addWidget(self.horizontalSlider)

        self.pushButton_3 = QtWidgets.QPushButton(self.widget)
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.setStyleSheet("""
            QPushButton{
                background-color: #415cf5;
                font-size: 16px;
                font-weight: bold;
                color:white;
                padding: 5px;
                border-radius: 10px;
                                        margin-bottom:100px;
            }
        """)
        self.gridLayout.addWidget(self.pushButton_3)


        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.label_3.setStyleSheet("""
            QLabel{
                font-size:16px;
                font-weight:bold;
                background-color:#282d3c;
                display:flex;
                justify-content:center;
                align-items:center;
                text-align:center;
            }
        """)
        self.label_3.setMaximumHeight(40)
        self.gridLayout.addWidget(self.label_3)
        
        self.horizontalSlider_2 = QtWidgets.QSlider(self.widget)
        self.horizontalSlider_2.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_2.setObjectName("horizontalSlider_2")
        self.gridLayout.addWidget(self.horizontalSlider_2)


        self.pushButton_4 = QtWidgets.QPushButton(self.widget)
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.setStyleSheet("""
            QPushButton{
                background-color: #415cf5;
                font-size: 16px;
                font-weight: bold;
                color:white;
                padding: 5px;
                border-radius: 10px;
            
                                        }
        """)
        self.gridLayout.addWidget(self.pushButton_4)
        self.horizontalLayout.addWidget(self.widget)
        
        
        
        
        
        
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setObjectName("widget_2")
        self.widget_2.setMinimumWidth(1200)  # Adjust the value as needed
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        

        self.widget_3 = QtWidgets.QWidget(self.widget_2)
        self.widget_3.setObjectName("widget_3")
        self.gridLayout_2.addWidget(self.widget_3, 0, 0, 1, 3)
        self.normalGraph1Layout = QHBoxLayout(self.widget_3)
        self.normalInputSignalGraph = pg.PlotWidget()
        self.normalInputSignalGraph.showGrid(x=True, y=True)
        self.normalInputSignalGraph.setBackground("transparent")
        self.normalGraph1Layout.addWidget(self.normalInputSignalGraph)


        self.widget_4 = QtWidgets.QWidget(self.widget_2)
        self.widget_4.setObjectName("widget_4")
        self.gridLayout_2.addWidget(self.widget_4, 0, 3, 1, 3)
        self.spectrogramGraph1Layout = QHBoxLayout(self.widget_4)
        self.spectrogramInputSignalGraph = pg.PlotWidget()
        self.spectrogramInputSignalGraph.showGrid(x=True, y=True)
        self.spectrogramInputSignalGraph.setBackground("transparent")
        self.spectrogramGraph1Layout.addWidget(self.spectrogramInputSignalGraph)


        self.widget_5 = QtWidgets.QWidget(self.widget_2)
        self.widget_5.setObjectName("widget_5")
        self.gridLayout_2.addWidget(self.widget_5, 1, 0, 1, 3)
        self.normalGraph2Layout = QHBoxLayout(self.widget_5)
        self.normalOutputSignalGraph = pg.PlotWidget()
        self.normalOutputSignalGraph.showGrid(x=True, y=True)
        self.normalOutputSignalGraph.setBackground("transparent")
        self.normalGraph2Layout.addWidget(self.normalOutputSignalGraph)


        self.widget_6 = QtWidgets.QWidget(self.widget_2)
        self.widget_6.setObjectName("widget_6")
        self.gridLayout_2.addWidget(self.widget_6, 1, 3, 1, 3)
        self.spectrogramGraph2Layout = QHBoxLayout(self.widget_6)
        self.spectrogramlOutputSignalGraph = pg.PlotWidget()
        self.spectrogramlOutputSignalGraph.showGrid(x=True, y=True)
        self.spectrogramlOutputSignalGraph.setBackground("transparent")
        self.spectrogramGraph2Layout.addWidget(self.spectrogramlOutputSignalGraph)

        self.normalInputSignalGraph.setFixedSize(700, 300)      # Wider width, reduced height
        self.spectrogramInputSignalGraph.setFixedSize(700, 300) # Wider width, reduced height
        self.normalOutputSignalGraph.setFixedSize(700, 300)     # Wider width, reduced height
        self.spectrogramlOutputSignalGraph.setFixedSize(700, 300) # Wider width, reduced height




        # Create a QHBoxLayout for widget_7 to center the buttons
        self.widget_7 = QtWidgets.QWidget(self.widget_2)
        self.widget_7.setObjectName("widget_7")
        self.widget_7.setMinimumSize(QtCore.QSize(0, 70))  # Ensures minimum height for visibility
        self.widget_7.setStyleSheet("""
            QWidget{
                background-color: transparent;
                font-size: 16px;
                border-radius:10px;
                font-weight: bold;
                color:white;
                padding:10px;
            }
        """)

        self.widget_7_layout = QtWidgets.QHBoxLayout(self.widget_7)
        self.widget_7_layout.setAlignment(QtCore.Qt.AlignCenter)  # Center align the layout

        # Add buttons to widget_7 with the layout instead of setting specific geometries
        self.startOrPauseButton = QtWidgets.QPushButton(self.widget_7)
        self.startOrPauseButton.setText("Play/Pause")
        self.startOrPauseButton.setStyleSheet("""
            QPushButton{
                background-color: #415cf5;
                font-size: 16px;
                font-weight: bold;
                color:white;
                border:none;
                padding:10px;
            }
        """)
        self.startOrPauseButton.setIcon(playIcon)
        self.startOrPauseButton.setIconSize(QtCore.QSize(20, 20))
        self.widget_7_layout.addWidget(self.startOrPauseButton)

        # Add the remaining buttons similarly
        self.replayButton = QtWidgets.QPushButton(self.widget_7)
        self.replayButton.setText("Replay")
        self.replayButton.setStyleSheet("""
            QPushButton{
                background-color: #415cf5;
                font-size: 16px;
                font-weight: bold;
                color:white;
                border:none;
                padding: 5px;
            }
        """)
        self.replayButton.setIcon(replayIcon)
        self.replayButton.setIconSize(QtCore.QSize(30, 30))
        self.widget_7_layout.addWidget(self.replayButton)

        # Repeat for other buttons
        self.zoomInButton = QtWidgets.QPushButton(self.widget_7)
        self.zoomInButton.setText("Zoom In")
        self.zoomInButton.setStyleSheet("""
            QPushButton{
                background-color: #415cf5;
                font-size: 16px;
                font-weight: bold;
                color:white;
                border:none;
                padding:5px;
            }
        """)
        self.zoomInButton.setIcon(zoomInIcon)
        self.zoomInButton.setIconSize(QtCore.QSize(30, 30))
        self.widget_7_layout.addWidget(self.zoomInButton)

        self.zoomOutButton = QtWidgets.QPushButton(self.widget_7)
        self.zoomOutButton.setText("Zoom Out")
        self.zoomOutButton.setStyleSheet("""
            QPushButton{
                background-color: #415cf5;
                font-size: 16px;
                font-weight: bold;
                color:white;
                border:none;
                padding: 5px;
            }
        """)
        self.zoomOutButton.setIcon(zoomOutIcon)
        self.zoomOutButton.setIconSize(QtCore.QSize(30, 30))
        self.widget_7_layout.addWidget(self.zoomOutButton)

        # Continue adding other buttons like speedUpButton and speedDownButton
        # Speed Up button
        self.speedUpButton = QtWidgets.QPushButton(self.widget_7)
        self.speedUpButton.setText("Speed Up")
        self.speedUpButton.setStyleSheet("""
            QPushButton{
                background-color: #415cf5;
                font-size: 16px;
                font-weight: bold;
                color:white;
                border:none;
                padding: 10px;
            }
        """)
        self.speedUpButton.setIcon(speedUpIcon)
        self.speedUpButton.setIconSize(QtCore.QSize(20, 20))
        self.widget_7_layout.addWidget(self.speedUpButton)

        # Speed Down button
        self.speedDownButton = QtWidgets.QPushButton(self.widget_7)
        self.speedDownButton.setText("Speed Down")
        self.speedDownButton.setStyleSheet("""
            QPushButton{
                background-color: #415cf5;
                font-size: 16px;
                font-weight: bold;
                color:white;
                border:none;
            }
        """)
        self.speedDownButton.setIcon(speedDownIcon)
        self.speedDownButton.setIconSize(QtCore.QSize(20, 20))
        self.widget_7_layout.addWidget(self.speedDownButton)


        # # Add slider
        # self.horizontalSlider_3 = QtWidgets.QSlider(self.widget_7)
        # self.horizontalSlider_3.setGeometry(QtCore.QRect(700, 20, 351, 22))
        # self.horizontalSlider_3.setOrientation(QtCore.Qt.Horizontal)

        # # Add label
        # self.label_4 = QtWidgets.QLabel("Label", self.widget_7)
        # self.label_4.setGeometry(QtCore.QRect(650, 20, 71, 21))

        # Add widget_7 to grid layout
        self.gridLayout_2.addWidget(self.widget_7, 2, 0, 1, 6)

        # Make sure gridLayout_2 is set as the layout for self.widget_2
        self.widget_2.setLayout(self.gridLayout_2)

                
        self.sliderLayout = QtWidgets.QHBoxLayout()

        # Create the vertical sliders and add them to the layout
        self.verticalSlider = QtWidgets.QSlider(self.widget_2)
        self.verticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider.setObjectName("verticalSlider")
        self.verticalSlider.setStyleSheet("""
            QSlider::handle:vertical {
                    background-color: #415cf5;
                    border-radius: 10px;
                    width: 20px;
                    height: 40px;
                    margin: -10px 0;
                }

            QSlider {
                background: transparent;
            }
        """)

        # Add the slider to the layout
        self.sliderLayout.addWidget(self.verticalSlider)

        self.verticalSlider_2 = QtWidgets.QSlider(self.widget_2)
        self.verticalSlider_2.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_2.setObjectName("verticalSlider_2")
        self.sliderLayout.addWidget(self.verticalSlider_2)

        self.verticalSlider_3 = QtWidgets.QSlider(self.widget_2)
        self.verticalSlider_3.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_3.setObjectName("verticalSlider_3")
        self.sliderLayout.addWidget(self.verticalSlider_3)

        self.verticalSlider_4 = QtWidgets.QSlider(self.widget_2)
        self.verticalSlider_4.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_4.setObjectName("verticalSlider_4")
        self.sliderLayout.addWidget(self.verticalSlider_4)

        self.verticalSlider_5 = QtWidgets.QSlider(self.widget_2)
        self.verticalSlider_5.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_5.setObjectName("verticalSlider_5")
        self.sliderLayout.addWidget(self.verticalSlider_5)

        self.verticalSlider_6 = QtWidgets.QSlider(self.widget_2)
        self.verticalSlider_6.setOrientation(QtCore.Qt.Vertical)
        self.verticalSlider_6.setObjectName("verticalSlider_6")
        self.sliderLayout.addWidget(self.verticalSlider_6)

        # Set the spacing and alignment for the slider layout
        self.sliderLayout.setSpacing(200)  # Adjust spacing between sliders
        self.sliderLayout.setAlignment(QtCore.Qt.AlignCenter)  # Align sliders centrally

        # Create a widget to hold the slider layout and add it below widget_7
        self.sliderWidget = QtWidgets.QWidget(self.widget_2)
        self.sliderWidget.setLayout(self.sliderLayout)

        # Add the sliderWidget to the gridLayout_2, ensuring it appears below widget_7
        self.gridLayout_2.addWidget(self.sliderWidget, 3, 0, 1, 6)

        # Make sure gridLayout_2 is set as the layout for self.widget_2
        self.widget_2.setLayout(self.gridLayout_2)
        
        self.horizontalLayout.addWidget(self.widget_2)
        self.gridLayout_3.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1411, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.browseFileButton.setText(_translate("MainWindow", "Browse Signal"))
        self.frequencyDomainButton.setText(_translate("MainWindow", "Frequency Domain"))
        self.label.setText(_translate("MainWindow", "Modes"))
        self.checkBox.setText(_translate("MainWindow", "Hide Spectrogram"))
        self.label_2.setText(_translate("MainWindow", "Original Signal"))
        self.pushButton_3.setText(_translate("MainWindow", "Play Audio Signal"))
        self.label_3.setText(_translate("MainWindow", "Filtered Signal"))
        self.pushButton_4.setText(_translate("MainWindow", "Play Audio Signal"))



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
