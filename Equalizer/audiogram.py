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


class Audiogram(QWidget):
    def __init__(self, signalsTime, originalSignal, filteredSignal):
        super().__init__()
        self.signalsTime = signalsTime
        self.originalSignal = originalSignal
        self.filteredSignal = filteredSignal
        self.setupUi()
        self.plotSignificantFrequencies()
        self.frequencyShape = "Frequency Domain"

    def setupUi(self):

        self.resize(1464, 798)
        self.setStyleSheet("background-color: #1b1d23;")
        
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        
        
        self.widget = QtWidgets.QWidget(self)
        self.widget.setObjectName("widget")
        self.origianlSignalGraph = PlotWidget(self.widget)
        self.origianlSignalGraph.setBackground('transparent')
        self.origianlSignalGraph.showGrid(x=True, y=True)
        self.verticalLayout.addWidget(self.origianlSignalGraph)

        
        
        self.widget_2 = QtWidgets.QWidget(self)
        self.widget_2.setObjectName("widget_2")
        self.filteredSignalGraph = PlotWidget(self.widget)
        self.filteredSignalGraph.setBackground('transparent')
        self.filteredSignalGraph.showGrid(x=True, y=True)
        self.verticalLayout.addWidget(self.filteredSignalGraph)


        self.toggleShapeButton = QtWidgets.QPushButton(self)
        self.toggleShapeButton.setObjectName("pushButton")
        self.toggleShapeButton.setStyleSheet("""
            QPushButton
            {
                background-color: #062e51;
                border: 2px solid white;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.toggleShapeButton.clicked.connect(lambda: self.toggleShape())
        
        self.verticalLayout.addWidget(self.toggleShapeButton)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Form"))
        self.toggleShapeButton.setText(_translate("Form", "Toggle Shape"))

    
    
    def plotSignificantFrequencies(self):
        fft_original_signal = np.fft.fft(self.originalSignal)  # Return Complex Numbers (Real -> Amplitude, Imaginary -> Phase)
        original_freqs = np.fft.fftfreq(len(self.originalSignal), d=(self.signalsTime[1] - self.signalsTime[0]))  # Frequency bins
        original_magnitudes = np.abs(fft_original_signal) / len(self.originalSignal)  # Amplitudes

        fft_modified_signal = np.fft.fft(self.filteredSignal)
        filtered_freqs =  np.fft.fftfreq(len(self.filteredSignal), d=(self.signalsTime[1] - self.signalsTime[0]))
        filtered_magnitudes = np.abs(fft_modified_signal) / len(self.filteredSignal)  # Amplitudes

        # Set a dynamic threshold to detect significant peaks
        original_significant_peaks, original_signal_properties = find_peaks(original_magnitudes)
        filtered_significant_peaks, filtered_signal_properties = find_peaks(filtered_magnitudes)

        original_positive_peaks = original_freqs[original_significant_peaks]
        original_positive_peaks = original_positive_peaks[original_positive_peaks > 0]

        filtered_positive_peaks = filtered_freqs[filtered_significant_peaks]
        filtered_positive_peaks = filtered_positive_peaks[filtered_positive_peaks > 0]


        if original_significant_peaks.size > 0:
            # Clear the frequency domain graph and plot the original frequencies
            self.origianlSignalGraph.clear()
            self.filteredSignalGraph.clear()
            # Call the repeat function with the calculated sampling frequency
          
            self.origianlSignalGraph.plot(original_freqs, original_magnitudes, pen='b', name='Original Frequency Domain')
            self.filteredSignalGraph.plot(filtered_freqs, filtered_magnitudes, pen='r', name='Original Frequency Domain')
        
    
    def toggleShape(self):
        print("Switching..")
        if self.frequencyShape == "Frequency Domain":
            self.frequencyShape = "Audiogram"
            self.plotAudiogram()
        else:
            self.frequencyShape = "Frequency Domain"
            self.plotSignificantFrequencies()

    def plotAudiogram(self):
        # Put your code here to plot the audiogram.
        pass

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  
    time_test = [1, 2, 3 , 4]
    signal_1_test= [1 , 2, 3 ,4]
    signal_2_test= [1, 2, 3, 4]
    ui = Audiogram(time_test, signal_1_test, signal_2_test)
    ui.show()
    app.exec_()

