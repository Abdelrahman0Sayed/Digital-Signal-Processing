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
from audiogram import Audiogram

SPECTROGRAM_CONFIG = {
    'cmap': 'viridis',
    'aspect': 'auto',
    'interpolation': 'gaussian',
    'vmin': -80,  # Minimum dB value
    'vmax': 0,    # Maximum dB value
}

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
        padding: 0px;
        margin: 0px;
    }}
"""


STYLES['SLIDER_LABEL'] = f"""
    QLabel {{
        color: {COLORS['text']};
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 5px;
        padding: 0px 0;
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

STYLES['SPECTROGRAM'] = f"""
    QWidget {{
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;  # Increased padding
        background-color: rgba(26, 27, 30, 0.8);
        backdrop-filter: blur(10px);
    }}
"""

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
        margin: 0px;
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
        padding: 2px 0px;
        background: rgba(114, 137, 218, 0.1);
        border-radius: 10px;
    }}
"""

def change_mode(self, mode):
    """Handle mode changes"""
    self.current_mode = mode
    
    if mode == "Music and Animals":
        self.create_music_animal_sliders()
        self.hide_wiener_controls()
        self.slidersContainer.show()
        
    elif mode == "Vocals and Phonemes":
        self.create_vocal_phoneme_sliders()
        self.hide_wiener_controls()
        self.slidersContainer.show()
        
    elif mode == "Wiener Filter":
        self.clear_sliders()
        self.show_wiener_controls()
        self.slidersContainer.hide()
    
    # Update equalization if signal loaded
    if hasattr(self, 'signalData') and len(self.signalData) > 1:
        if mode == "Music and Animals":
            self.apply_music_animal_equalization()
        elif mode == "Vocals and Phonemes":
            self.apply_vocal_phoneme_equalization()


def clear_sliders(self):
    """Clear all existing sliders"""
    for slider in self.sliders:
        slider.deleteLater()
    for label in self.sliderLabels:
        label.deleteLater()
    self.sliders = []
    self.sliderLabels = []
    
def add_slider(self, name, min_freq, max_freq):
    """Add a slider with frequency range label"""
    # Create container for slider group
    container = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 10)
    
    # Add label with name and frequency range
    label = QtWidgets.QLabel(f"{name} ({min_freq}-{max_freq} Hz)")
    label.setStyleSheet(f"""
        color: {COLORS['text']};
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 2px;
    """)
    layout.addWidget(label)
    
    # Create slider
    slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
    slider.setMinimum(0)
    slider.setMaximum(100)
    slider.setValue(0)
    slider.setStyleSheet(f"""
        QSlider::groove:horizontal {{
            border: 1px solid {COLORS['accent']};
            height: 8px;
            background: {COLORS['secondary']};
            margin: 2px 0;
            border-radius: 4px;
        }}

        QSlider::handle:horizontal {{
            background: {COLORS['accent']};
            border: none;
            width: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }}

        QSlider::handle:horizontal:hover {{
            background: {COLORS['button_hover']};
        }}
    """)
    
    # Connect slider value changed signal
    slider.valueChanged.connect(self.on_slider_changed)
    
    layout.addWidget(slider)
    self.slidersInnerLayout.addWidget(container)
    
    # Store references
    self.sliders.append(slider)
    self.sliderLabels.append(label)
    
def on_slider_changed(self):
    """Handle slider value changes"""
    if self.current_mode == "Music and Animals":
        self.apply_music_animal_equalization()
    elif self.current_mode == "Vocals and Phonemes":
        self.apply_vocal_phoneme_equalization()
        
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

    # # Cache FFT results if not already cached
    if not self.cached:
        self._cached_fft = np.fft.fft(self.signalData)
        self._cached_freqs = np.fft.fftfreq(len(self.signalData), 1/self.samplingRate)
        self.cached= True

    # Work with cached FFT
    signal_fft = self._cached_fft.copy()
    frequencies = self._cached_freqs
    gains = [slider.value()/10 for slider in self.sliders]

    # Apply equalization
    # if self.current_mode == "Uniform Range":
    #     max_freq = self.samplingRate // 2
    #     band_width = max_freq / 10
        
    #     # Vectorized operation instead of loop
    #     for i, gain in enumerate(gains):
    #         freq_mask = (np.abs(frequencies) >= i * band_width) & (np.abs(frequencies) < (i + 1) * band_width)
    #         signal_fft[freq_mask] *= gain
    
    # else:
    #     if self.current_mode == "Musical Instruments":
    #         ranges = self.instrument_ranges
    #     elif self.current_mode == "Animal Sounds":
    #         gains = [slider.value() for slider in self.sliders]  # Remove /100 division
    #         ranges = self.animal_ranges
            
    #         for (name, freq_ranges), gain in zip(ranges.items(), gains):
    #             gain = gain/100  
    #             for low_freq, high_freq in freq_ranges:
    #                 freq_mask = (np.abs(frequencies) >= low_freq) & (np.abs(frequencies) < high_freq)
    #                 signal_fft[freq_mask] *= gain
    #     elif self.current_mode == "ECG Abnormalities":
    #         gains = [slider.value()/10 for slider in self.sliders]  # Add /100 scaling
    #         ranges = self.ecg_ranges
    #         for (name, freq_ranges), gain in zip(ranges.items(), gains):
    #             for low_freq, high_freq in freq_ranges:
    #                 freq_mask = (np.abs(frequencies) >= low_freq) & (np.abs(frequencies) < high_freq)
    #                 signal_fft[freq_mask] *= gain
                
            
    #     for (name, freq_ranges), gain in zip(ranges.items(), gains):
    #         for low_freq, high_freq in freq_ranges:
    #             freq_mask = (np.abs(frequencies) >= low_freq) & (np.abs(frequencies) < high_freq)
    #             signal_fft[freq_mask] *= gain

    if self.current_mode == "Music and Animals":
        self.apply_music_animal_equalization()
    elif self.current_mode == "Vocals and Phonemes":
        self.apply_vocal_phoneme_equalization()

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
    plotSpectrogram(self)

    self.audiogramWidget.updateData(self.signalTime, self.signalData, self.modifiedData)
    
    





def toggleFrequencyScale(self):
    if self.domain == "Frequency Domain":
        self.frequency_scale = "Audiogram" if self.frequency_scale == "Linear" else "Linear"
        updateEqualization(self)



def resetSignal(self):
    self.signalTimer.stop()
    self.signalTimeIndex = 0
    signalPlotting(self)

def toggleVisibility(self):
    """Toggle visibility of spectrograms only"""
    if self.spectogramCheck.isChecked():
        self.spectrogramContainer.hide()
        self.spectogramCheck.setText("Show Spectrograms")
    else:
        self.spectrogramContainer.show()
        self.spectogramCheck.setText("Hide Spectrograms")



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
        
# Add this function to handle colorbar styling
def style_colorbar(colorbar, ax):
    """Apply consistent styling to spectrogram colorbars"""
    # Get colorbar axis
    cax = colorbar.ax
    
    # Style the colorbar ticks and labels
    cax.tick_params(
        colors=COLORS['text'],
        labelsize=8,
        length=3,
        width=1
    )
    
    # Style the colorbar outline
    cax.spines['top'].set_color(COLORS['accent'])
    cax.spines['right'].set_color(COLORS['accent']) 
    cax.spines['bottom'].set_color(COLORS['accent'])
    cax.spines['left'].set_color(COLORS['accent'])
    
    # Adjust colorbar position to prevent overlap
    colorbar.set_label(
        'Magnitude (dB)',
        color=COLORS['text'],
        fontsize=10,
        labelpad=10
    )
    
    # Make sure colorbar background is transparent
    cax.set_facecolor('none')

def plotSpectrogram(self):
    if len(self.signalData) <= 1:
        return
        
    # Clear and reset figures
    self.firstSpectrogramFig.clear()
    self.secondSpectrogramFig.clear()
    
    # Create new subplots with proper spacing
    self.firstGraphAxis = self.firstSpectrogramFig.add_subplot(111)
    self.secondGraphAxis = self.secondSpectrogramFig.add_subplot(111)
    
    # Calculate spectrograms
    f1, t1, Sxx1 = signal.spectrogram(
        self.signalData, 
        fs=self.samplingRate,
        nperseg=256,
        noverlap=128,
        mode='magnitude'
    )
    
    f2, t2, Sxx2 = signal.spectrogram(
        self.modifiedData, 
        fs=self.samplingRate,
        nperseg=256,
        noverlap=128,
        mode='magnitude'
    )
    
    # Plot spectrograms
    im1 = self.firstGraphAxis.pcolormesh(
        t1, f1, 10 * np.log10(Sxx1),
        shading='gouraud',
        cmap='viridis'
    )
    
    im2 = self.secondGraphAxis.pcolormesh(
        t2, f2, 10 * np.log10(Sxx2),
        shading='gouraud',
        cmap='viridis'
    )
    
    # Style axes
    for ax in [self.firstGraphAxis, self.secondGraphAxis]:
        ax.set_facecolor('none')
        ax.grid(True, alpha=0.2, color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
    
    # Add labels and titles with white text
    self.firstGraphAxis.set_ylabel('Frequency [Hz]', color='white')
    self.firstGraphAxis.set_xlabel('Time [sec]', color='white')
    self.firstGraphAxis.set_title('Original Signal Spectrogram', color='white')
    
    self.secondGraphAxis.set_ylabel('Frequency [Hz]', color='white')
    self.secondGraphAxis.set_xlabel('Time [sec]', color='white')
    self.secondGraphAxis.set_title('Filtered Signal Spectrogram', color='white')
    
    # Add colorbars
    cbar1 = self.firstSpectrogramFig.colorbar(im1)
    cbar2 = self.secondSpectrogramFig.colorbar(im2)
    
    # Style colorbars
    for cbar in [cbar1, cbar2]:
        cbar.ax.yaxis.set_tick_params(colors='white')
        cbar.set_label('Power [dB]', color='white')
    
    # Update layouts
    self.firstSpectrogramFig.tight_layout()
    self.secondSpectrogramFig.tight_layout()
    
    # Draw canvases
    self.firstGraphCanvas.draw()
    self.secondGraphCanvas.draw()

    

def playOriginalAudio(self):
    # Check if audio is currently playing
    if hasattr(self, '_playing_original') and self._playing_original:
        # Stop the audio
        sd.stop()
        self._playing_original = False
        # Change button icon/text to play
        self.playOriginalSignal.setIcon(self.playIcon)
        self.playOriginalSignal.setText("Play Audio")
    else:
        # Stop any other playing audio first
        sd.stop()
        if hasattr(self, '_playing_filtered'):
            self._playing_filtered = False
            self.playFilteredSignal.setIcon(self.playIcon)
            self.playFilteredSignal.setText("Play Audio")
            
        # Play the original audio
        sd.play(self.signalData, self.samplingRate)
        self._playing_original = True
        # Change button icon/text to stop
        self.playOriginalSignal.setIcon(self.stopIcon)
        self.playOriginalSignal.setText("Stop Audio")

def playFilteredAudio(self):
    # Check if audio is currently playing
    if hasattr(self, '_playing_filtered') and self._playing_filtered:
        # Stop the audio
        sd.stop()
        self._playing_filtered = False
        # Change button icon/text to play
        self.playFilteredSignal.setIcon(self.playIcon)
        self.playFilteredSignal.setText("Play Audio")
    else:
        # Stop any other playing audio first
        sd.stop()
        if hasattr(self, '_playing_original'):
            self._playing_original = False
            self.playOriginalSignal.setIcon(self.playIcon)
            self.playOriginalSignal.setText("Play Audio")

        # Get the current modified data from the modifiedData attribute
        current_modified_data = self.modifiedData
            
        # Play the filtered audio using current modified data
        sd.play(current_modified_data, self.samplingRate)
        self._playing_filtered = True
        # Change button icon/text to stop
        self.playFilteredSignal.setIcon(self.stopIcon)
        self.playFilteredSignal.setText("Stop Audio")

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


def deleteSignal(self):
    # Delete All Signals
    if hasattr(self, 'graph1'):
        self.graph1.clear()
    if hasattr(self, 'graph2'):
        self.graph2.clear()
    if hasattr(self, 'firstGraphAxis'):
        self.firstGraphAxis.clear()  
        self.firstGraphCanvas.draw()
    if hasattr(self, 'secondGraphAxis'):  
        self.secondGraphAxis.clear()  
        self.secondGraphCanvas.draw() 
    if hasattr(self, 'audiogramWidget'):
        self.audiogramWidget.deleteSignal()
    
    self.frequency_scale = "Linear"
    self.signalData = ""
    self.signalTime = ""
    self.modifiedData = ""
    self.cached = False  
    if hasattr(self, '_cached_fft'):
        del self._cached_fft  # Remove cached FFT
    if hasattr(self, '_cached_freqs'):
        del self._cached_freqs  # Remove cached frequencies
    
    self.lastLoadedSignal = None
    self.lastModifiedSignal = None
    
    self.signalTimeIndex = 0
    self.domain = "Time Domain"
