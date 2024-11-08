import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from scipy.interpolate import CubicSpline

f_max = 50  # Frequency component for reference
f_s = 2.5 * f_max  # Sampling rate
T = 5  # Signal duration
num_samples = 1000  # High-resolution samples
t_orig = np.linspace(0, T, num_samples, endpoint=False)

# Replace this part with your custom signal (sin, composite, real-world, etc.)
# original_signal = np.sin(2 * np.pi * f_max * t_orig)
original_signal = (0.5 * np.sin(2 * np.pi * 10 * t_orig) + 
                   0.3 * np.sin(2 * np.pi * 30 * t_orig) + 
                   0.2 * np.sin(2 * np.pi * 50 * t_orig))

# Sampling the signal
t_sampled = np.linspace(0, T, int(T * f_s), endpoint=False)
sampled_signal = (0.5 * np.sin(2 * np.pi * 10 * t_sampled) + 
                  0.3 * np.sin(2 * np.pi * 30 * t_sampled) + 
                  0.2 * np.sin(2 * np.pi * 50 * t_sampled))

# Reconstruction using Cubic Spline
cs = CubicSpline(t_sampled, sampled_signal)
reconstructed_signal = cs(t_orig)

# Plot
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True)
win.setWindowTitle("Nyquist Sampling: Custom Signal Reconstruction")

# Plot Original Signal
plot1 = win.addPlot(title="Original Signal")
curve1 = plot1.plot(pen='y')

# Plot Reconstructed Signal
win.nextRow()
plot2 = win.addPlot(title="Reconstructed Signal")
curve2 = plot2.plot(pen='r')

# Update function
def update():
    curve1.setData(t_orig, original_signal)
    curve2.setData(t_orig, reconstructed_signal)

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

if __name__ == '__main__':
    QtWidgets.QApplication.instance().exec_()


"""
import pandas as pd
data = pd.read_csv('ecg_data.csv')
t_orig = data['time'].values  # Time values from the dataset
original_signal = data['voltage'].values  # ECG voltage values
t_sampled = np.linspace(t_orig[0], t_orig[-1], int(len(t_orig) * 0.4))  # Example sampling rate
sampled_signal = np.interp(t_sampled, t_orig, original_signal)  # Linear downsampling
"""

"""
Questions:
    1- Usage of np.linespace
    2- Usage of Cubic Spline
"""