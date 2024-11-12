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
        # Previous FFT calculations remain the same
        fft_original_signal = np.fft.fft(self.originalSignal)
        original_freqs = np.fft.fftfreq(len(self.originalSignal), d=(self.signalsTime[1] - self.signalsTime[0]))
        original_magnitudes = np.abs(fft_original_signal) / len(self.originalSignal)

        fft_modified_signal = np.fft.fft(self.filteredSignal)
        filtered_freqs = np.fft.fftfreq(len(self.filteredSignal), d=(self.signalsTime[1] - self.signalsTime[0]))
        filtered_magnitudes = np.abs(fft_modified_signal) / len(self.filteredSignal)

        original_significant_peaks, original_signal_properties = find_peaks(original_magnitudes)
        filtered_significant_peaks, filtered_signal_properties = find_peaks(filtered_magnitudes)

        # Reset graph settings
        self.origianlSignalGraph.clear()
        self.filteredSignalGraph.clear()
        
        # Reset to linear scale
        self.origianlSignalGraph.setLogMode(x=False, y=False)
        self.filteredSignalGraph.setLogMode(x=False, y=False)
        
        # Reset axis ranges
        self.origianlSignalGraph.enableAutoRange()
        self.filteredSignalGraph.enableAutoRange()
        
        # Reset tick formatting
        self.origianlSignalGraph.getAxis('bottom').setTicks(None)
        self.filteredSignalGraph.getAxis('bottom').setTicks(None)
        
        # Plot the data
        self.origianlSignalGraph.plot(original_freqs, original_magnitudes, pen='b', name='Original Frequency Domain')
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
        
        # Standard audiogram frequencies
        audiogram_freqs = np.array([125, 250, 500, 1000, 2000, 4000, 8000])
        
        # Convert to magnitude in dB with proper reference level
        # Using standard reference level for dB calculation
        ref_level = 1.0  # Reference level for dB calculation
        original_magnitudes = 20 * np.log10(np.abs(fft_original) / len(self.originalSignal) / ref_level)
        filtered_magnitudes = 20 * np.log10(np.abs(fft_filtered) / len(self.filteredSignal) / ref_level)
        
        # Keep only positive frequencies and handle zero/negative values in log scale
        positive_mask = freqs > 0
        freqs = freqs[positive_mask]
        original_magnitudes = original_magnitudes[positive_mask]
        filtered_magnitudes = filtered_magnitudes[positive_mask]
        
        # Set minimum dB level
        min_db = -60
        original_magnitudes = np.maximum(original_magnitudes, min_db)
        filtered_magnitudes = np.maximum(filtered_magnitudes, min_db)
        
        # Interpolate magnitudes at audiogram frequencies
        original_interp = np.interp(audiogram_freqs, freqs, original_magnitudes)
        filtered_interp = np.interp(audiogram_freqs, freqs, filtered_magnitudes)
        
        # Clear and setup plots
        self.origianlSignalGraph.clear()
        self.filteredSignalGraph.clear()
        
        # Set logarithmic x-axis and proper ranges
        self.origianlSignalGraph.setLogMode(x=True, y=False)
        self.filteredSignalGraph.setLogMode(x=True, y=False)
        
        # Set proper axis ranges
        self.origianlSignalGraph.setXRange(np.log10(100), np.log10(10000))
        self.origianlSignalGraph.setYRange(min_db, 20)
        self.filteredSignalGraph.setXRange(np.log10(100), np.log10(10000))
        self.filteredSignalGraph.setYRange(min_db, 20)
        
        # Custom tick formatter for log scale
        tick_values = [(freq, str(freq)) for freq in audiogram_freqs]
        self.origianlSignalGraph.getAxis('bottom').setTicks([tick_values])
        self.filteredSignalGraph.getAxis('bottom').setTicks([tick_values])
        
        # Plot with markers
        self.origianlSignalGraph.plot(audiogram_freqs, original_interp, pen='b', symbol='o', symbolSize=10)
        self.filteredSignalGraph.plot(audiogram_freqs, filtered_interp, pen='r', symbol='o', symbolSize=10)
        
        # Set labels
        self.origianlSignalGraph.setLabel('left', 'Amplitude (dB)')
        self.origianlSignalGraph.setLabel('bottom', 'Frequency (Hz)')
        self.filteredSignalGraph.setLabel('left', 'Amplitude (dB)')
        self.filteredSignalGraph.setLabel('bottom', 'Frequency (Hz)')
        
        # Add grid
        self.origianlSignalGraph.showGrid(x=True, y=True)
        self.filteredSignalGraph.showGrid(x=True, y=True)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  
    time_test = [1, 2, 3 , 4]
    signal_1_test= [1 , 2, 3 ,4]
    signal_2_test= [1, 2, 3, 4]
    ui = Audiogram(time_test, signal_1_test, signal_2_test)
    ui.show()
    app.exec_()

