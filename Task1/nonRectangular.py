import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PyQt5 import QtWidgets, QtGui
import sys

class PolarEcgPlot(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ECG Signals in Polar Coordinates")
        self.setGeometry(100, 100, 800, 600)

        # Store file paths and colors for all plots
        self.GraphFilePaths = []
        self.GraphColors = []
        self.EcgSignals = []

        # Initialize the figure and axis for the polar plot
        self.fig, self.ax = plt.subplots(subplot_kw={'projection': 'polar'})
        self.lines = []  # Store multiple lines for each signal

        # Set up the animation
        self.ani = None

    def LoadEcgSignals(self, FilePaths, Colors):
        self.GraphFilePaths = FilePaths
        self.GraphColors = [color.name() if isinstance(color, QtGui.QColor) else color for color in Colors]  # Convert QColor to hex
        self.EcgSignals = self.LoadSignalsFromFiles(FilePaths)
        print(f"Loaded ECG signals: {self.EcgSignals}")

        if self.EcgSignals:
            theta = np.linspace(0, 2 * np.pi, len(self.EcgSignals[0]))  # Assume all signals have the same length
            r_list = [self.NormalizeSignal(signal) for signal in self.EcgSignals]

            # Ensure the number of colors matches the number of signals
            if len(self.GraphColors) < len(r_list):
                # If there are fewer colors, fill the rest with a default color (e.g., black)
                self.GraphColors += ['#000000'] * (len(r_list) - len(self.GraphColors))

            # Start animation for all signals
            self.StartAnimation(theta, r_list)

    def LoadSignalsFromFiles(self, FilePaths):
        Signals = []
        for FilePath in FilePaths:
            try:
                Data = pd.read_csv(FilePath, header=None)
                EcgSignal = Data.values.flatten()
                Signals.append(EcgSignal)
            except Exception as e:
                print(f"Error loading {FilePath}: {e}")
                Signals.append(np.array([]))  
        return Signals

    def NormalizeSignal(self, signal):
        """ Normalize the ECG signal to a range between 0 and 1 """
        return (signal - np.min(signal)) / (np.max(signal) - np.min(signal))

    def StartAnimation(self, theta, r_list):
        """ Start the animation for all signals in the polar plot """
        self.ax.set_title('ECG Signals in Polar Coordinates - Cine Mode')

        # Initialize lines for each signal
        self.lines = [self.ax.plot([], [], color=self.GraphColors[i], lw=2)[0] for i in range(len(r_list))]

        # Function to initialize the plot (called once at the start)
        def init():
            for line in self.lines:
                line.set_data([], [])
            return self.lines

        # Function to update the plot dynamically in cine mode
        def update(frame):
            for i, r in enumerate(r_list):
                self.lines[i].set_data(theta[:frame], r[:frame])
            return self.lines

        # Create the animation
        self.ani = FuncAnimation(self.fig, update, frames=len(theta), init_func=init, blit=True, interval=10, repeat=False)

        plt.show()

# Step 4: Run the application
if __name__ == "__main__":
    App = QtWidgets.QApplication(sys.argv)
    Window = PolarEcgPlot()
    Window.show()

    # Example usage (provide file paths and colors here)
    Window.LoadEcgSignals(["signal1.csv", "signal2.csv"], [QtGui.QColor("blue"), QtGui.QColor("red")])

    sys.exit(App.exec_())
