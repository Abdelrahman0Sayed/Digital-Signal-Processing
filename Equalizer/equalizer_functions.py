import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz
from scipy.fft import fft, ifft, fftfreq , fftshift
from scipy.io import wavfile
import librosa
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
import sounddevice as sd
from scipy import signal

def changeMode(self, mode):
    self.current_mode = mode
    
    # Clear existing sliders
    for slider in self.sliders:
        slider.deleteLater()
    for label in self.sliderLabels:
        label.deleteLater()
    
    self.sliders = []
    self.sliderLabels = []
    
    if mode == "Uniform Range":
        # Create 10 uniform range sliders
        max_freq = self.samplingRate // 2 if hasattr(self, 'samplingRate') else 22050
        band_width = max_freq / 10
        
        for i in range(10):
            low = i * band_width
            high = (i + 1) * band_width
            createSlider(self,f"{int(low)}-\n{int(high)}Hz")
            
    elif mode == "Musical Instruments":
        for instrument in self.instrument_ranges.keys():
            createSlider(self,instrument)
            
    elif mode == "Animal Sounds":
        for animal in self.animal_ranges.keys():
            createSlider(self,animal)
            
    elif mode == "ECG Abnormalities":
        for condition in self.ecg_ranges.keys():
            createSlider(self,condition)
    
    updateEqualization(self)
    

def createSlider(self, label_text):
    sliderColumn = QtWidgets.QVBoxLayout()
    
    slider = QtWidgets.QSlider()
    slider.setOrientation(QtCore.Qt.Vertical)
    slider.setMinimum(0)
    slider.setMaximum(200)
    slider.setValue(100)
    slider.setMinimumHeight(150)
    slider.valueChanged.connect(lambda: updateEqualization(self))
    self.sliders.append(slider)
    
    label = QtWidgets.QLabel(label_text)
    label.setMinimumWidth(60)
    self.sliderLabels.append(label)
    
    sliderColumn.addWidget(slider, alignment=QtCore.Qt.AlignHCenter)
    sliderColumn.addWidget(label, alignment=QtCore.Qt.AlignHCenter)
    self.horizontalLayout_5.addLayout(sliderColumn)


def updateEqualization(self):
    signal_fft = np.fft.fft(self.signalData)
    frequencies = np.fft.fftfreq(len(self.signalData), 1/self.samplingRate)
    gains = [slider.value()/100 for slider in self.sliders]

    if self.current_mode == "Uniform Range":
        # Apply uniform range equalization
        max_freq = self.samplingRate // 2
        band_width = max_freq / 10
        
        for i, gain in enumerate(gains):
            low_freq = i * band_width
            high_freq = (i + 1) * band_width
            freq_mask = (np.abs(frequencies) >= low_freq) & (np.abs(frequencies) < high_freq)
            signal_fft[freq_mask] *= gain
            
    else:
        # Get appropriate frequency ranges for current mode
        if self.current_mode == "Musical Instruments":
            ranges = self.instrument_ranges
        elif self.current_mode == "Animal Sounds":
            ranges = self.animal_ranges
        elif self.current_mode == "ECG Abnormalities":
            ranges = self.ecg_ranges
            
        # Apply gains to corresponding frequency ranges
        for (name, freq_ranges), gain in zip(ranges.items(), gains):
            for low_freq, high_freq in freq_ranges:
                freq_mask = (np.abs(frequencies) >= low_freq) & (np.abs(frequencies) < high_freq)
                signal_fft[freq_mask] *= gain
    
    # Convert back to time domain
    self.modifiedData = modified_signal = np.real(np.fft.ifft(signal_fft))
    
    # Update plot with appropriate frequency scale
    # self.graph2.clear()
    # if self.frequency_scale == "Audiogram" :
    #     freq_mask = self.frequencies > 0
    #     self.graph2.plot(np.log10(self.frequencies[freq_mask]), 
    #                     20 * np.log10(np.abs(signal_fft[freq_mask])))
    # else :
    #     self.graph2.plot(self.signalTime, modified_signal, pen='r')
    
    # self.graph2.setYRange(min(self.signalData), max(self.signalData))

    # Update the second spectrogram plot
    self.secondGraphAxis.clear()
    frequencies2, times2, power_spectrogram = signal.spectrogram(modified_signal, fs=self.samplingRate)

    # Log-scale for better visualization
    log_power_spectrogram = np.log10(power_spectrogram)

    # Plot the updated spectrogram
    self.secondGraphAxis.pcolormesh(times2, frequencies2, log_power_spectrogram, shading='gouraud')
    self.secondGraphAxis.set_ylabel('Frequency [Hz]')
    self.secondGraphAxis.set_xlabel('Time [sec]')
    self.secondGraphCanvas.draw()

    signalPlotting(self)




def toggleFrequencyScale(self):
    if self.domain == "Frequency Domain":
        self.frequency_scale = "Audiogram" if self.frequency_scale == "Linear" else "Linear"
        updateEqualization(self)

def resetSignal(self):
    self.signalTimer.stop()
    self.signalTimeIndex = 0
    signalPlotting(self)

def toggleVisibility(self):
    if self.secondGraphCanvas.isVisible() and self.firstGraphCanvas.isVisible():
        self.secondGraphCanvas.hide()
        self.firstGraphCanvas.hide()
    else:
        self.firstGraphCanvas.show()
        self.secondGraphCanvas.show()


def signalPlotting(self):
    self.start_time = 0.0
    self.end_time = 1.0
    self.drawn = False

    self.graph1.clear()
    self.graph2.clear()

    self.graph1.plot(self.signalTime, self.signalData, pen='b', name='Original Data')
    self.graph2.plot(self.signalTime, self.modifiedData, pen='r', name='Original Data')

    self.graph1.setLimits(xMin=0, xMax=self.signalTime[-1] ,yMin=min(self.signalData) - 0.2 , yMax=max(self.signalData) + 0.2)
    self.graph2.setLimits(xMin=0, xMax=self.signalTime[-1] ,yMin=min(self.signalData) - 0.2 , yMax=max(self.signalData) + 0.2)
    
    self.signalTimer.stop()
    self.signalTimeIndex = 0

    self.signalTimer.timeout.connect(lambda: updateSignalPlotting(self))
    self.signalTimer.start(80)



def updateSignalPlotting(self):
    self.windowSize = 1  # Fixed window size

    
    # Stop the timer if we reach the end of the data
    if self.signalTimeIndex >= len(self.signalData):
        self.signalTimer.stop()
        self.signalTimeIndex = 0

    # if self.signalTime[self.signalTimeIndex] > self.windowSize:
    self.start_time = self.signalTime[self.signalTimeIndex] - self.windowSize
    if self.start_time < 0:
        self.start_time = 0

    self.end_time = self.signalTime[self.signalTimeIndex] + self.windowSize
    if self.signalTime[self.signalTimeIndex] < self.windowSize:
        self.end_time = self.windowSize

    self.graph1.setXRange(self.start_time, self.end_time, padding=0)
    self.graph2.setXRange(self.start_time, self.end_time, padding=0)


    
    self.signalTimeIndex += 100
    


def togglePlaying(self):
    if self.signalTimer.isActive():
        self.signalTimer.stop()
        self.playPause.setIcon(self.playIcon)
    else:
        self.signalTimer.start()
        self.playPause.setIcon(self.stopIcon)



def zoomingIn(self):

    # Get the view box of graph1 and scale it by (0.5, 1)
    view_box1 = self.graph1.plotItem.getViewBox()
    view_box1.scaleBy((0.5, 1))

    # Get the view box of graph2 and scale it by (0.5, 1)
    view_box2 = self.graph2.plotItem.getViewBox()
    view_box2.scaleBy((0.5, 1))

def zoomingOut(self):
    # Get the view box of graph1 and scale it horizontally by a factor of 1.5
    view_box1 = self.graph1.plotItem.getViewBox()
    view_box1.scaleBy((1.5, 1))

    # Get the view box of graph2 and scale it horizontally by a factor of 1.5
    view_box2 = self.graph2.plotItem.getViewBox()
    view_box2.scaleBy((1.5, 1))

def speedingUp(self):

    #self.signalTimer.stop()
    # Get the current interval and reduce it for faster updates
    current_interval = self.signalTimer.interval()
    if current_interval > 50:
        new_interval = max(50, current_interval - 100)  # Decrease the interval to speed up
        self.signalTimer.setInterval(new_interval)
        
def speedingDown(self):

    current_interval = self.signalTimer.interval()
    # Increase interval by a fixed amount to slow down
    new_interval = min(1000, current_interval + 100)  # Maximum interval of 1000ms for reasonable slow speed
    self.signalTimer.setInterval(new_interval)

def toggleFreqDomain(self):
    if self.domain == "Time Domain":
        self.domain = "Frequency Domain"
        self.frequencyDomainButton.setText("Frequency Domain")
        self.graph2.clear()
        self.graph2.plot(self.signalTime ,self.signalData, pen='r')
        self.scaleToggle.setEnabled(False)
  
    else:
        self.domain = "Time Domain"
        self.frequencyDomainButton.setText("Time Domain")
        self.graph2.clear()
        self.updateEqualization(self)
        self.scaleToggle.setEnabled(True)
        
        
def plotSpectrogram(self):
    # Compute the spectrogram
    frequencies, times, power_spectrogram = signal.spectrogram(self.signalData, fs=self.samplingRate)
    
    # Clear the previous plot (optional)
    self.firstGraphAxis.clear()

    # Plot the spectrogram
    self.firstGraphAxis.pcolormesh(times, frequencies, np.log10(power_spectrogram), shading='gouraud')
    self.firstGraphAxis.set_ylabel('Frequency [Hz]')
    self.firstGraphAxis.set_xlabel('Time [sec]')
    self.firstGraphCanvas.draw()  # Redraw the canvas


def playOriginalAudio(self):
    if hasattr(self, 'signalData') and hasattr(self, 'samplingRate'):
        try:
            # Stop any playing audio first
            sd.stop()
            # Play the original signal
            sd.play(self.signalData, self.samplingRate)
        except Exception as e:
            print(f"Error playing original audio: {e}")

def playFilteredAudio(self):
    if hasattr(self, 'signalData') and hasattr(self, 'samplingRate'):
        try:
            # Stop any playing audio first
            sd.stop()
            
            # Perform FFT on the signal data
            signal_fft = np.fft.fft(self.signalData)
            frequencies = np.fft.fftfreq(len(self.signalData), 1/self.samplingRate)
            
            # Get current slider values and apply equalization
            modified_fft = signal_fft.copy()
            gains = [slider.value()/100 for slider in self.sliders]
            
            if self.current_mode == "Uniform Range":
                max_freq = self.samplingRate // 2
                band_width = max_freq / 10
                
                for i, gain in enumerate(gains):
                    low_freq = i * band_width
                    high_freq = (i + 1) * band_width
                    freq_mask = (np.abs(frequencies) >= low_freq) & (np.abs(frequencies) < high_freq)
                    modified_fft[freq_mask] *= gain
            else:
                # Handle other modes
                ranges = None
                if self.current_mode == "Musical Instruments":
                    ranges = self.instrument_ranges
                elif self.current_mode == "Animal Sounds":
                    ranges = self.animal_ranges
                elif self.current_mode == "ECG Abnormalities":
                    ranges = self.ecg_ranges
                    
                if ranges:
                    for (name, freq_ranges), gain in zip(ranges.items(), gains):
                        for low_freq, high_freq in freq_ranges:
                            freq_mask = (np.abs(frequencies) >= low_freq) & (np.abs(frequencies) < high_freq)
                            modified_fft[freq_mask] *= gain
            
            # Convert back to time domain
            filtered_signal = np.real(np.fft.ifft(modified_fft))
            
            # Normalize to prevent clipping
            filtered_signal = filtered_signal / np.max(np.abs(filtered_signal))
            
            # Convert to same dtype as original signal
            filtered_signal = filtered_signal.astype(self.signalData.dtype)
            
            # Play the filtered signal
            sd.play(filtered_signal, self.samplingRate)
            
        except Exception as e:
            print(f"Error playing filtered audio: {e}")
            # Add more detailed error information
            import traceback
            traceback.print_exc()

def stopAudio(self):
    sd.stop()
