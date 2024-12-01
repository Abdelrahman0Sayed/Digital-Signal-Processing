import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import librosa
from pyqtgraph import PlotWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow, QLayout , QVBoxLayout , QHBoxLayout, QGridLayout ,QWidget, QFileDialog, QPushButton, QColorDialog, QInputDialog, QComboBox, QDialog, QRadioButton
from scipy.io import wavfile
import numpy as np
import pandas as pd
import sounddevice as sd
from PyQt5 import QtCore, QtGui, QtWidgets
from scipy.signal import find_peaks
import pyqtgraph as pg


class Audiogram(QWidget):
    def __init__(self, signalsTime, originalSignal, filteredSignal, parent=None):
        super().__init__()
            # Initialize with minimum valid data if empty
        if len(signalsTime) == 0 or len(originalSignal) == 0:
            self.signalsTime = np.array([0])
            self.originalSignal = np.array([0])
            self.filteredSignal = np.array([0])
        else:
            self.signalsTime = signalsTime
            self.originalSignal = originalSignal
            self.filteredSignal = filteredSignal


        self.setupUi()
        # Set size policy to expand
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, 
                        QtWidgets.QSizePolicy.Expanding)

        # Configure plots to expand
        # self.origianlSignalGraph.setSizePolicy(QtWidgets.QSizePolicy.Expanding, 
        #                                     QtWidgets.QSizePolicy.Expanding)
        self.filteredSignalGraph.setSizePolicy(QtWidgets.QSizePolicy.Expanding, 
                                            QtWidgets.QSizePolicy.Expanding)
        
        # Set size based on whether embedded or standalone
        if parent:
            self.resize(parent.width(), parent.height())
        else:
            self.resize(800, 400)
        
        self.plotSignificantFrequencies()
        self.frequencyShape = "Frequency Domain"

    def setupUi(self):
        self.resize(1464, 798)
        self.setStyleSheet("background-color: transparent;border: 0px;")
        
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        
        # Create horizontal layout with proper margins
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setContentsMargins(5, 5, 5, 20)  # Added bottom margin
        
        # First graph (Original Signal)
        self.widget = QtWidgets.QWidget(self)
        self.widget.setObjectName("widget")
        
        # Second graph (Filtered Signal) - same configuration
        self.widget_2 = QtWidgets.QWidget(self)
        self.widget_2.setObjectName("widget_2")
        self.filteredSignalGraph = PlotWidget(self.widget)
        self.filteredSignalGraph.setBackground('transparent')
        self.filteredSignalGraph.showGrid(x=True, y=True)
        
        # Configure axis
        self.filteredSignalGraph.getPlotItem().getAxis('bottom').setHeight(40)
        self.filteredSignalGraph.getPlotItem().layout.setContentsMargins(10, 10, 10, 25)
        self.horizontalLayout.addWidget(self.filteredSignalGraph)
        
        # Create vertical layout for the entire window
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Add the horizontal layout containing graphs to vertical layout
        self.verticalLayout.addLayout(self.horizontalLayout)
        
        # Add toggle button
        # self.toggleShapeButton = QtWidgets.QPushButton(self)
        # self.toggleShapeButton.setObjectName("pushButton")
        # self.toggleShapeButton.setStyleSheet("""
        #     QPushButton
        #     {
        #         background-color: #4a5178;
        #         border: 2px solid white;
        #         color: white;
        #         font-size: 20px;
        #         font-weight: bold;
        #         padding: 10px;
        #     }
        # """)
        # self.toggleShapeButton.clicked.connect(lambda: self.toggleShape())
        # self.verticalLayout.addWidget(self.toggleShapeButton)
        
        # Add vertical layout to grid
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        #self.toggleShapeButton.setText(_translate("Form", "Toggle Shape"))

    
    
    def plotSignificantFrequencies(self):
        # Previous FFT calculations remain the same
        if len(self.originalSignal) <= 1:
            return
        fft_original_signal = np.fft.fft(self.originalSignal)
        original_freqs = np.fft.fftfreq(len(self.originalSignal), d=(self.signalsTime[1] - self.signalsTime[0]))
        original_magnitudes = np.abs(fft_original_signal) / len(self.originalSignal)

        fft_modified_signal = np.fft.fft(self.filteredSignal)
        filtered_freqs = np.fft.fftfreq(len(self.filteredSignal), d=(self.signalsTime[1] - self.signalsTime[0]))
        filtered_magnitudes = np.abs(fft_modified_signal) / len(self.filteredSignal)

        original_significant_peaks, original_signal_properties = find_peaks(original_magnitudes)
        filtered_significant_peaks, filtered_signal_properties = find_peaks(filtered_magnitudes)

        # Reset graph settings
        self.filteredSignalGraph.clear()
        
        # Reset to linear scale
        self.filteredSignalGraph.setLogMode(x=False, y=False)
        
        # Reset axis ranges
        self.filteredSignalGraph.enableAutoRange()
        
        # Reset tick formatting
        self.filteredSignalGraph.getAxis('bottom').setTicks(None)
        
        # Plot the data
        self.filteredSignalGraph.plot(filtered_freqs, filtered_magnitudes, pen='r', name='Filtered Frequency Domain')
        
    def toggleShape(self):
        print("Switching..")
        if self.frequencyShape == "Frequency Domain":
            self.frequencyShape = "Audiogram"
            self.plotAudiogram()
        else:
            self.frequencyShape = "Frequency Domain"
            self.plotSignificantFrequencies()

    def plotAudiogram(self):
        # Calculate FFT for both signals
        fft_original = np.fft.fft(self.originalSignal)
        fft_filtered = np.fft.fft(self.filteredSignal)
        
        # Get frequency bins
        freqs = np.fft.fftfreq(len(self.originalSignal), d=(self.signalsTime[1] - self.signalsTime[0]))
        
        # Keep only positive frequencies within human hearing range
        positive_mask = (freqs > 20) & (freqs < 20000)  # 20Hz to 20kHz
        freqs = freqs[positive_mask]
        original_magnitudes = 20 * np.log10(np.abs(fft_original[positive_mask]) / len(self.originalSignal))
        filtered_magnitudes = 20 * np.log10(np.abs(fft_filtered[positive_mask]) / len(self.filteredSignal))
        
        # Increase downsample factor
        downsample_factor = 50  # Changed from 10 to 50
        freqs = freqs[::downsample_factor]
        original_magnitudes = original_magnitudes[::downsample_factor]
        filtered_magnitudes = filtered_magnitudes[::downsample_factor]
        
        # Configure graphs with reduced point density
        for graph in [self.filteredSignalGraph]:
            graph.clear()
            graph.setLogMode(x=True, y=False)
            graph.showGrid(x=True, y=True, alpha=0.3)
            graph.setLabel('left', 'Magnitude (dB)', size='12pt')
            graph.setLabel('bottom', 'Frequency (Hz)', size='12pt')
            graph.addLegend(offset=(-30, 30))
        
        # Plot with symbols every N points
        symbol_every = 5  # Show symbols every 5 points
        # self.origianlSignalGraph.plot(freqs, original_magnitudes,
        #                             pen=dict(color='b', width=2),
        #                             name='Original Signal',
        #                             symbol='o',  # Circle symbol
        #                             symbolSize=5,  # Smaller symbols
        #                             symbolBrush='b',
        #                             symbolPen='b',
        #                             skipSymbols=symbol_every)  # Skip symbols
                                    
        self.filteredSignalGraph.plot(freqs, filtered_magnitudes,
                                    pen=dict(color='r', width=2),
                                    name='Filtered Signal',
                                    symbol='o',
                                    symbolSize=5,
                                    symbolBrush='r',
                                    symbolPen='r',
                                    skipSymbols=symbol_every)
    
    def updateData(self, time_data, signal_data, modified_data):
        self.signalsTime = time_data
        self.originalSignal = signal_data
        self.filteredSignal = modified_data
        if self.frequencyShape != "Frequency Domain":
            self.plotAudiogram()
        else:
            self.plotSignificantFrequencies()
        self.show()
    
    def deleteSignal(self):
        self.filteredSignalGraph.clear()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  
    time_test = [1, 2, 3 , 4]
    signal_1_test= [1 , 2, 3 ,4]
    signal_2_test= [1, 2, 3, 4]
    ui = Audiogram(time_test, signal_1_test, signal_2_test)
    ui.show()
    app.exec_()

