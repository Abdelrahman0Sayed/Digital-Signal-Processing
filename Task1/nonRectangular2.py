import sys
import pandas as pd
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QPushButton, QFileDialog, QColorDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
from PyQt5 import QtCore, QtGui, QtWidgets


class CombinedRespiratoryPlot(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Respiratory Signal Visualization")
        self.setStyleSheet("background-color: black; color: white;") 
        self.file_path = "Signals/respiratory_normal.csv"
        self.load_data(self.file_path)
        self.setup_ui()

    def setup_ui(self):
        self.start_pause_icon = QtGui.QIcon("Images\start-pause.jpg")
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        
        # Create the figure and canvas for the graph
        self.fig = Figure(figsize=(8, 8))  # Square aspect ratio
        self.canvas = FigureCanvasQTAgg(self.fig)
        layout.addWidget(self.canvas)

        # Configure the figure's appearance
        self.fig.patch.set_facecolor('black')
        self.ax_polar = self.fig.add_subplot(111, projection='polar')
        self.polar_line, = self.ax_polar.plot([], [], color='blue', linewidth=2)
        self.ax_polar.set_facecolor('black')
        self.ax_polar.set_title("Polar Plot of Respiratory Signals", color='white')
        self.ax_polar.set_rlabel_position(0)
        self.ax_polar.set_rticks(np.linspace(0, 7, 8))
        self.ax_polar.tick_params(colors='white')
        
        # Animation settings
        self.frame_index = 0
        self.animation_speed = 2  # Default animation speed (ms)
        self.ani = FuncAnimation(self.fig, self.update, frames=len(self.time),
                                 interval=self.animation_speed, blit=True)
        
        self.setGeometry(100, 100, 800, 800)
        
        # Horizontal layout for buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        # Browse data button
        self.button_browse = QPushButton("Browse Data", self)
        self.button_browse.clicked.connect(self.browse_data)
        self.button_browse.setStyleSheet("""
            QPushButton{
                background-color: white;
                color: Black; 
                font-weight: bold;
                border: 2px solid black;
                font-size: 20px; 
                padding: 10px 24px;
                border-radius: 10px;
            }
                            
        """)
        button_layout.addWidget(self.button_browse)

        # Change signal color button
        self.button_color = QPushButton("Change Color", self)
        self.button_color.clicked.connect(self.change_signal_color)
        self.button_color.setStyleSheet("""
            QPushButton{
                background-color: white;
                color: Black; 
                font-weight: bold;
                border: 2px solid black;
                font-size: 20px; 
                padding: 10px 24px;
                border-radius: 10px;
            }
                            
        """)
        button_layout.addWidget(self.button_color)

        # Start/stop plotting button
        self.button_toggle = QPushButton(self)
        self.button_toggle.setIcon(self.start_pause_icon)
        self.button_toggle.setIconSize(QtCore.QSize(25,25))
        self.button_toggle.setStyleSheet("""
            QPushButton{
                background-color: white;
                color: Black; 
                font-weight: bold;
                border: 2px solid black;
                font-size: 20px; 
                padding: 10px 24px;
                border-radius: 10px;
            }
                            
        """)
        self.button_toggle.clicked.connect(self.toggle_animation)
        button_layout.addWidget(self.button_toggle)

        # Rewind data button
        self.button_rewind = QPushButton("Rewind Data", self)
        self.button_rewind.setStyleSheet("""
            QPushButton{
                background-color: white;
                color: Black; 
                font-weight: bold;
                border: 2px solid black;
                font-size: 20px; 
                padding: 10px 24px;
                border-radius: 10px;
            }
                            
        """)
        self.button_rewind.clicked.connect(self.rewind_data)
        button_layout.addWidget(self.button_rewind)

        # Add the button layout below the canvas
        layout.addLayout(button_layout)

        # Variable to control the animation state
        self.is_animating = False


    def load_data(self, file_path):
        self.df = pd.read_csv(file_path, header=None)
        self.df.columns = ['Time (s)', 'Respiratory Value']
        
        self.time = self.df['Time (s)']
        self.respiratory_values = self.df['Respiratory Value']
        self.normalized_values = (self.respiratory_values - self.respiratory_values.min()) / (self.respiratory_values.max() - self.respiratory_values.min())
        self.theta = np.linspace(0, 2 * np.pi, len(self.normalized_values))
        self.r = self.normalized_values * 6

    def update(self, frame):
        self.polar_line.set_data(self.theta[:frame], self.r[:frame])
        
        if frame == len(self.time) - 1:
            self.frame_index = 0
            self.polar_line.set_data([], [])  
            self.ani.event_source.stop()  
            self.ani.event_source.start() 

        return self.polar_line,

    def showEvent(self, event):
        if self.is_animating:
            self.ani.event_source.start()

    def closeEvent(self, event):
        self.ani.event_source.stop()
        super().closeEvent(event)

    def toggle_animation(self):
        self.is_animating = not self.is_animating
        if self.is_animating:
            self.ani.event_source.start()
        else:
            self.ani.event_source.stop()

    def browse_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            if hasattr(self, 'ani'):
                self.ani.event_source.stop()
                del self.ani

            self.polar_line.set_data([], [])
            self.canvas.draw()  
            self.load_data(file_path)
            self.frame_index = 0
            self.ani = FuncAnimation(self.fig, self.update, frames=len(self.time),
                                    interval=self.animation_speed, blit=True)
            if self.is_animating:
                self.ani.event_source.start()


    def change_signal_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.polar_line.set_color(color.name())
            self.canvas.draw()



    def rewind_data(self):
        self.frame_index = 0
        
        # Clear existing data from the plot
        self.polar_line.set_data([], [])
        self.canvas.draw()  

        if hasattr(self, 'ani'):
            self.ani.event_source.stop()  
            del self.ani  

        self.ani = FuncAnimation(self.fig, self.update, frames=len(self.time),
                                interval=self.animation_speed, blit=True)
        
        if self.is_animating:
            self.ani.event_source.start()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CombinedRespiratoryPlot()
    window.show()
    sys.exit(app.exec_())
