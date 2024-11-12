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
import time


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



# Add to STYLES dictionary
STYLES['SLIDER_CONTAINER'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border-radius: 10px;
        padding: 15px;
        margin: 5px;
    }}
"""


STYLES['SLIDER_LABEL'] = f"""
    QLabel {{
        color: {COLORS['text']};
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 5px;
        padding: 5px 0;
    }}
"""

# Update the STYLES['SLIDER'] to include vertical slider styles
STYLES['SLIDER'] = f"""
    QSlider {{
        background: transparent;
    }}
    QSlider::groove:vertical {{
        background: {COLORS['button']};
        width: 6px;
        border-radius: 3px;
    }}
    QSlider::handle:vertical {{
        background: {COLORS['accent']};
        border: none;
        height: 18px;
        width: 18px;
        margin: 0 -6px;
        border-radius: 9px;
    }}
    QSlider::handle:vertical:hover {{
        background: {COLORS['button_hover']};
    }}
    QSlider::sub-page:vertical {{
        background: {COLORS['secondary']};
        border-radius: 3px;
    }}
    QSlider::add-page:vertical {{
        background: {COLORS['accent']};
        border-radius: 3px;
    }}
"""

def changeMode(self, mode):
    self.current_mode = mode
    
    # Clear existing layout first
    for i in reversed(range(self.horizontalLayout_5.count())): 
        widget = self.horizontalLayout_5.itemAt(i).widget()
        if widget:
            widget.deleteLater()
    
    # Reset lists
    self.sliders = []
    self.sliderLabels = []
    
    # Create new sliders based on mode
    if mode == "Uniform Range":
        max_freq = self.samplingRate // 2 if hasattr(self, 'samplingRate') else 22050
        band_width = max_freq / 10
        
        for i in range(10):
            low = i * band_width
            high = (i + 1) * band_width
            createSlider(self, f"{int(low)}-\n{int(high)}Hz")
            
    elif mode == "Musical Instruments":
        for instrument in self.instrument_ranges.keys():
            createSlider(self, instrument)
            
    elif mode == "Animal Sounds":
        for animal in self.animal_ranges.keys():
            createSlider(self, animal)
            
    elif mode == "ECG Abnormalities":
        for condition in self.ecg_ranges.keys():
            createSlider(self, condition)

    # Force layout update
    self.horizontalLayout_5.update()
    updateEqualization(self)

def createSlider(self, label_text):
    # Create container widget
    container = QtWidgets.QWidget()
    container.setFixedWidth(100)  # Set fixed width for consistency
    container.setStyleSheet(STYLES['SLIDER_CONTAINER'])
    container_layout = QtWidgets.QVBoxLayout(container)
    container_layout.setContentsMargins(5, 10, 5, 10)
    
    # Create slider first
    slider = QtWidgets.QSlider(QtCore.Qt.Vertical)
    slider.setMinimum(0)
    slider.setMaximum(200)
    slider.setValue(100)
    slider.setFixedHeight(150)
    slider.setStyleSheet(STYLES['SLIDER'])
    
    # Create label
    label = QtWidgets.QLabel(label_text)
    label.setStyleSheet(STYLES['SLIDER_LABEL'])
    label.setAlignment(QtCore.Qt.AlignCenter)
    label.setWordWrap(True)  # Allow text wrapping
    
    # Add widgets to container
    container_layout.addWidget(slider, alignment=QtCore.Qt.AlignHCenter)
    container_layout.addWidget(label, alignment=QtCore.Qt.AlignHCenter)
    container_layout.setStretch(0, 2)  # Give slider more vertical space
    container_layout.setStretch(1, 1)  # Give label less vertical space
    
    # Store references and connect signal
    self.sliders.append(slider)
    self.sliderLabels.append(label)
    slider.valueChanged.connect(lambda: updateEqualization(self))
    
    # Add to layout
    self.horizontalLayout_5.addWidget(container)
    return container

def updateEqualization(self):
    # Track if audio is currently playing
    audio_was_playing = False
    try:
        audio_was_playing = sd.get_stream().active
    except:
        pass
    
    # Stop current playback if any
    if audio_was_playing:
        sd.stop()

    # Throttle updates
    if hasattr(self, '_last_update') and time.time() - self._last_update < 0.1:
        return
    self._last_update = time.time()

    # Cache FFT results if not already cached
    if not hasattr(self, '_cached_fft'):
        self._cached_fft = np.fft.fft(self.signalData)
        self._cached_freqs = np.fft.fftfreq(len(self.signalData), 1/self.samplingRate)

    # Work with cached FFT
    signal_fft = self._cached_fft.copy()
    frequencies = self._cached_freqs
    gains = [slider.value()/100 for slider in self.sliders]

    # Apply equalization
    if self.current_mode == "Uniform Range":
        max_freq = self.samplingRate // 2
        band_width = max_freq / 10
        
        # Vectorized operation instead of loop
        for i, gain in enumerate(gains):
            freq_mask = (np.abs(frequencies) >= i * band_width) & (np.abs(frequencies) < (i + 1) * band_width)
            signal_fft[freq_mask] *= gain
    else:
        if self.current_mode == "Musical Instruments":
            ranges = self.instrument_ranges
        elif self.current_mode == "Animal Sounds":
            ranges = self.animal_ranges
        elif self.current_mode == "ECG Abnormalities":
            ranges = self.ecg_ranges
            
        for (name, freq_ranges), gain in zip(ranges.items(), gains):
            for low_freq, high_freq in freq_ranges:
                freq_mask = (np.abs(frequencies) >= low_freq) & (np.abs(frequencies) < high_freq)
                signal_fft[freq_mask] *= gain

    # Convert back to time domain
    self.modifiedData = np.real(np.fft.ifft(signal_fft))

    # Restart audio if it was playing
    if audio_was_playing:
        try:
            # Normalize to prevent clipping
            filtered_signal = self.modifiedData / np.max(np.abs(self.modifiedData))
            # Convert to same dtype as original signal
            filtered_signal = filtered_signal.astype(self.signalData.dtype)
            # Play the filtered signal
            sd.play(filtered_signal, self.samplingRate)
        except Exception as e:
            print(f"Error restarting audio: {e}")

    # Update visualizations
    # Downsample for visualization if signal is too long
    if len(self.modifiedData) > 10000:
        downsample_factor = len(self.modifiedData) // 10000
        modified_signal_vis = self.modifiedData[::downsample_factor]
        times_vis = self.signalTime[::downsample_factor]
    else:
        modified_signal_vis = self.modifiedData
        times_vis = self.signalTime

    # Update spectrogram less frequently
    if not hasattr(self, '_spec_update_counter'):
        self._spec_update_counter = 0
    self._spec_update_counter += 1

    if self._spec_update_counter % 3 == 0:  # Update every 3rd call
        self.secondGraphAxis.clear()
        frequencies2, times2, power_spectrogram = signal.spectrogram(
            modified_signal_vis, 
            fs=self.samplingRate,
            nperseg=min(256, len(modified_signal_vis)//10)  # Smaller window for faster computation
        )
        self.secondGraphAxis.pcolormesh(times2, frequencies2, np.log10(power_spectrogram), shading='gouraud')
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
    from scipy import signal

    # Determine shortest length
    min_length = min(len(self.signalData), len(self.modifiedData))
    
    # Resample both arrays to shortest length
    if len(self.signalData) != min_length:
        self.signalData = signal.resample(self.signalData, min_length)
    if len(self.modifiedData) != min_length:
        self.modifiedData = signal.resample(self.modifiedData, min_length)
    
    # Create new time array matching the resampled data
    self.signalTime = np.linspace(0, min_length/self.samplingRate, min_length)
    
    self.start_time = 0.0
    self.end_time = 1.0
    self.drawn = False

    # Clear existing plots
    self.graph1.clear()
    self.graph2.clear()

    try:
        # Plot resampled data
        self.graph1.plot(self.signalTime, self.signalData, pen='b', name='Original Data')
        self.graph2.plot(self.signalTime, self.modifiedData, pen='r', name='Modified Data')

        # Set plot limits
        y_min = min(min(self.signalData), min(self.modifiedData)) - 0.2
        y_max = max(max(self.signalData), max(self.modifiedData)) + 0.2
        
        self.graph1.setLimits(xMin=0, xMax=self.signalTime[-1], yMin=y_min, yMax=y_max)
        self.graph2.setLimits(xMin=0, xMax=self.signalTime[-1], yMin=y_min, yMax=y_max)

        # Reset and start timer
        self.signalTimer.stop()
        self.signalTimeIndex = 0
        self.signalTimer.timeout.connect(lambda: updateSignalPlotting(self))
        self.signalTimer.start(80)

    except Exception as e:
        print(f"Error during plotting: {str(e)}")
        return



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

def export_signal(self):
    """Export the modified signal"""
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(self, 
                                             "Save Signal",
                                             "",
                                             "WAV files (*.wav);;CSV files (*.csv)", 
                                             options=options)
    
    if file_path:
        if file_path.endswith('.wav'):
            # Normalize the signal to [-1, 1] range
            normalized_signal = self.modifiedData / np.max(np.abs(self.modifiedData))
            
            # Convert to 16-bit PCM
            audio_data = (normalized_signal * 32767).astype(np.int16)
            
            # Export as WAV
            wavfile.write(file_path, int(self.samplingRate), audio_data)
            
        elif file_path.endswith('.csv'):
            # Export as CSV
            df = pd.DataFrame({
                'Time': self.signalTime,
                'Amplitude': self.modifiedData
            })
            df.to_csv(file_path, index=False)
