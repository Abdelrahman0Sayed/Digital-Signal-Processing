#####################################
#        Signal Viewer App          #
#                                   #
#            Team 16                #
#                                   #
#####################################

import sys
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider
from PyQt5.QtGui import QIcon , QFont, QPixmap, QColor # Package to set an icon , fonts and images
from PyQt5.QtCore import Qt , QTimer  # used for alignments.
from PyQt5.QtWidgets import QLayout , QVBoxLayout , QHBoxLayout, QGridLayout ,QWidget, QFileDialog, QPushButton, QColorDialog, QInputDialog, QComboBox, QDialog
import pyqtgraph as pg
import random
from fetchApiData import FetchApi_MainWindow
from GlueMenu import Ui_GlueMenu
from functions_graph import zoom_in, zoom_out, show_graph, hide_graph, increase_speed, decrease_speed, start_simulation, stop_simulation, rewind, change_color, export_to_pdf, remove_signal
from nonRectangular import PolarEcgPlot

class Ui_MainWindow(QMainWindow):

    # Important Variables
    max_num_of_file= 4 
    num_of_files= 0 # To get the Maximum Number of files can user draw in the Graph.
    graph_1_files= []
    graph_2_files=[]
    all_signals=[]


    def show_ecg_plot(self):
        print("Start Non Rectangular Coordinates")
        if self.ecg_plot_window is None:  # Create the window only if it doesn't exist
            self.ecg_plot_window = PolarEcgPlot()
            all_signals = self.graph_1_files + self.graph_2_files
            all_colors = self.graph1_colors = self.graph2_colors
            self.ecg_plot_window.LoadEcgSignals(all_signals, all_colors)
            self.ecg_plot_window.show()
        else:
            self.ecg_plot_window.raise_()  # Bring to front if already exists
        


    def setup_buttons_connections(self):
        # Button connections for Graph 1
        self.zoom_in_graph1.clicked.connect(lambda: zoom_in(self, self.linkedSignals, 1))
        self.zoom_out_graph1.clicked.connect(lambda: zoom_out(self, self.linkedSignals, 1))
        self.show_graph_1.clicked.connect(lambda: show_graph(self, self.linkedSignals, 1))
        self.hide_graph_1.clicked.connect(lambda: hide_graph(self, self.linkedSignals, 1))
        self.high_speed_1.clicked.connect(lambda: increase_speed(self, self.linkedSignals, 1))
        self.slow_speed_1.clicked.connect(lambda: decrease_speed(self, self.linkedSignals, 1))
        self.start_graph_1.clicked.connect(lambda: start_simulation(self, self.linkedSignals, 1))
        self.stop_graph_1.clicked.connect(lambda: stop_simulation(self, self.linkedSignals, 1))
        self.rewind_graph1.clicked.connect(lambda: rewind(self, self.linkedSignals , 1))
        self.Change_color_1.clicked.connect(lambda: self.openColorChangeDialog(1))
        #self.export_graph1.clicked.connect(lambda: export_to_pdf(self, self.linkedSignals, 1))

        # Button connections for Graph 2
        self.zoom_in_graph2.clicked.connect(lambda: zoom_in(self, self.linkedSignals, 2))
        self.zoom_out_graph2.clicked.connect(lambda: zoom_out(self, self.linkedSignals, 2))
        self.show_graph_2.clicked.connect(lambda: show_graph(self, self.linkedSignals, 2))
        self.hide_graph_2.clicked.connect(lambda: hide_graph(self, self.linkedSignals, 2))
        self.high_speed_2.clicked.connect(lambda: increase_speed(self, self.linkedSignals, 2))
        self.slow_speed_2.clicked.connect(lambda: decrease_speed(self, self.linkedSignals, 2))
        self.start_graph_2.clicked.connect(lambda: start_simulation(self, self.linkedSignals, 2))
        self.stop_graph_2.clicked.connect(lambda: stop_simulation(self, self.linkedSignals, 2))
        self.rewind_graph2.clicked.connect(lambda: rewind(self, self.linkedSignals, 2))
        self.Change_color_2.clicked.connect(lambda: change_color(self, self.linkedSignals, 2))
        self.Change_color_2.clicked.connect(lambda: self.openColorChangeDialog(2))
        #self.export_graph2.clicked.connect(lambda: export_to_pdf(self, self.linkedSignals, 2))

        self.change_to_graph_1.clicked.connect(self.move_to_graph_2_to_1)
        self.change_to_graph_2.clicked.connect(self.move_to_graph_1_to_2)

        self.graph_1_H_slider.valueChanged.connect(self.update_graph_positions)
        self.graph_2_H_slider.valueChanged.connect(self.update_graph_positions)
        self.graph_1_V_slider.valueChanged.connect(self.update_graph_positions)
        self.graph_2_V_slider.valueChanged.connect(self.update_graph_positions)

        #remove signal button will open a dialog to select the signal to remove from graph 1
        self.remove_signal_1.clicked.connect(lambda: self.remove_signal(1))

        #remove signal button will open a dialog to select the signal to remove from graph 2
        self.remove_signal_2.clicked.connect(lambda: self.remove_signal(2))
        
    def remove_signal(self, graph_num):
        dialog = SignalSelectionDialogRemove(self.graph_1_files, self.graph_2_files, graph_num, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_signal = dialog.selected_signal
            remove_signal(self, self.linkedSignals, graph_num, selected_signal)


    def update_graph_positions(self):
        """ Update the position of the graphs based on the slider values. """
        # Get the current slider values
        h_value1 = self.graph_1_H_slider.value()
        h_value2 = self.graph_2_H_slider.value()
        v_value1 = self.graph_1_V_slider.value()
        v_value2 = self.graph_2_V_slider.value()

        # Get the current view ranges
        x_range1 = self.graph1.viewRange()[0]
        y_range1 = self.graph1.viewRange()[1]
        x_range2 = self.graph2.viewRange()[0]
        y_range2 = self.graph2.viewRange()[1]

        # Calculate the new ranges based on the slider values
        new_x_range1 = (h_value1, h_value1 + (x_range1[1] - x_range1[0]))
        new_y_range1 = (v_value1, v_value1 + (y_range1[1] - y_range1[0]))
        new_x_range2 = (h_value2, h_value2 + (x_range2[1] - x_range2[0]))
        new_y_range2 = (v_value2, v_value2 + (y_range2[1] - y_range2[0]))

        # Update the x-range and y-range of the graphs based on the new ranges
        self.graph1.setXRange(*new_x_range1, padding=0)
        self.graph1.setYRange(*new_y_range1, padding=0)
        self.graph2.setXRange(*new_x_range2, padding=0)
        self.graph2.setYRange(*new_y_range2, padding=0)

    #moving_graphs
    def move_to_graph_1_to_2(self):
        if len(self.graph_1_files) > 0:
            # Move the last signal from graph 1 to graph 2
            self.graph_2_files.append(self.graph_1_files.pop())  # Move file from graph 1 to graph 2
            self.graph2_colors.append(self.graph1_colors.pop())  # Move color from graph 1 to graph 2

            self.timer_graph_1.stop()  # Stop timer for graph 1
            self.graph1.clear()  # Clear graph 1
            self.graph2.clear()  # Clear graph 2

            # Plot new data for graph 1 if available
            if len(self.graph_1_files) > 0:
                graph1Data = self.loadSignalData(self.graph_1_files[-1], 1)  # Load new data for graph 1
                self.signalPlotting(self.graph1, graph1Data, 1)  # Plot the new data on graph 1

            # Load and plot data for graph 2 (the one just moved)
            if len(self.graph_2_files) > 0:
                graph2Data = self.loadSignalData(self.graph_2_files[-1], 2)  # Load data for graph 2
                self.signalPlotting(self.graph2, graph2Data, 2)  # Plot the data on graph 2
        else:
            print("No Signals to Move")



    def move_to_graph_2_to_1(self):
        if len(self.graph_2_files) > 0:
            # Move the last signal from graph 2 to graph 1
            self.graph_1_files.append(self.graph_2_files.pop())  # Move file from graph 2 to graph 1
            self.graph1_colors.append(self.graph2_colors.pop())  # Move color from graph 2 to graph 1

            self.timer_graph_2.stop()  # Stop timer for graph 2
            self.graph1.clear()  # Clear graph 1
            self.graph2.clear()  # Clear graph 2

            # Plot new data for graph 2 if available
            if len(self.graph_2_files) > 0:
                graph2Data = self.loadSignalData(self.graph_2_files[-1],1)  # Load new data for graph 2
                self.signalPlotting(self.graph2, graph2Data, 2)  # Plot the new data on graph 2

            # Load and plot data for graph 1 (the one just moved)
            if len(self.graph_1_files) > 0:
                graph1Data = self.loadSignalData(self.graph_1_files[-1],2)  # Load data for graph 1
                self.signalPlotting(self.graph1, graph1Data, 1)  # Plot the data on graph 1
        else:
            print("No Signals to Move")


    

    # Constructing the Main Window.
    def __init__(self):
        super().__init__()
        
        self.graph_1_files = []  # Store file paths for Graph 1 signals
        self.graph_2_files = []  # Store file paths for Graph 2 signals
        self.graph1_colors = []  # Store colors for each signal in Graph 1
        self.graph2_colors = []  # Store colors for each signal in Graph 2
        self.linked_graphs_color = self.get_random_color()
        # Other existing initializations
        self.setWindowTitle("Multi Channel Signal Viewer")
        self.setFixedSize(1300, 1000)
        self.setStyleSheet("Background-color:#e3e3e3;")
        self.linkedSignals = False
        
        self.timer_graph_1 = QTimer(self)  # Used primarily for cine mode
        self.time_index_graph_1 = 0  # For Cine Mode Scrolling

        self.timer_graph_2 = QTimer(self)  # Used primarily for cine mode
        self.time_index_graph_2 = 0  # For Cine Mode Scrolling

        self.timer_linked_graphs = QTimer(self)  # Used primarily for cine mode
        self.time_index_linked_graphs = 0  # For Cine Mode Scrolling


        self.ecg_plot_window = None  # Instance variable to keep reference

        self.setupUiElements()  # Call method to set up UI components
        self.windowSize = 200
    
    def apiData(self):
        self.apiData = FetchApi_MainWindow()
        self.apiData.show()
    
    def show_signal_selection_dialog(self):
        dialog = SignalSelectionDialog(self.graph_1_files, self.graph_2_files, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_signal_1 = dialog.selected_signal_1
            selected_signal_2 = dialog.selected_signal_2
            self.glue_signals(selected_signal_1, selected_signal_2)

    def glue_signals(self, signal_1, signal_2):
        # Load the selected signals
        signal_data1 = self.loadSignalData(signal_1, 1)
        signal_data2 = self.loadSignalData(signal_2, 2)

        # Show the glue menu with the selected signals
        self.signalGlue = Ui_GlueMenu(None, signal_data1, signal_data2)
        self.signalGlue.show()
    

    def setupUiElements(self):
        startIcon =QtGui.QIcon("images/play.png")
        stopIcon = QtGui.QIcon("images/pause.png")
        rewindIcon = QtGui.QIcon("images/rewind.png")
        showIcon = QtGui.QIcon("images/show.png")
        hideIcon = QtGui.QIcon("images/hide.png")
        zoomInIcon = QtGui.QIcon("images/zoom_in.png")
        zoomOutIcon = QtGui.QIcon("images/zoom_out.png")
        binIcon = QtGui.QIcon("images/bin.png")

        # Create the central widget -> Wich Will Contain All our layout.
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        
        ##### Graph 1 Section ####
        self.Graph1_Section = QtWidgets.QWidget(self.centralwidget)
        self.Graph1_Section.setGeometry(QtCore.QRect(0, 10, 1281, 510))
        self.Graph1_Section.setObjectName("Graph1_Section")

        self.Graph1 = QtWidgets.QWidget(self.Graph1_Section)
        self.Graph1.setGeometry(QtCore.QRect(40, 35, 1200, 330))
        self.Graph1.setObjectName("Graph1")
        graph_1_layout = QHBoxLayout(self.Graph1)
        self.graph1 = pg.PlotWidget(title="Graph 1 Signals")
        graph_1_layout.addWidget(self.graph1)
        
        #-- Graph 1 Horizontal Slider --#
        self.graph_1_H_slider = QSlider(self.Graph1_Section)
        self.graph_1_H_slider.setGeometry(QtCore.QRect(40, 350, 1200, 30))
        self.graph_1_H_slider.setOrientation(QtCore.Qt.Horizontal)
        self.graph_1_H_slider.setObjectName("graph_1_H_slider")
        self.graph_1_H_slider.setMinimum(0)
        self.graph_1_H_slider.setMaximum(5000)  # Placeholder; will update based on the signal length
        self.graph_1_H_slider.setValue(0)
        self.graph_1_H_slider.setTickInterval(1)


        #-- Graph 1 Vertical Slider --#
        self.graph_1_V_slider = QSlider(self.Graph1_Section)
        self.graph_1_V_slider.setGeometry(QtCore.QRect(1250, 30, 30, 300))
        self.graph_1_V_slider.setOrientation(QtCore.Qt.Vertical)
        self.graph_1_V_slider.setObjectName("graph_1_V_slider")

        
        self.zoom_in_graph1 = QtWidgets.QPushButton(self.Graph1_Section)
        self.zoom_in_graph1.setIcon(zoomInIcon)
        self.zoom_in_graph1.setIconSize(QtCore.QSize(32,40))
        self.zoom_in_graph1.setGeometry(QtCore.QRect(1005, 0, 40, 40))
        self.zoom_in_graph1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.zoom_in_graph1.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid black;
                border-radius: 50px;
                font-size: 40px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.zoom_in_graph1.setObjectName("zoom_in_graph1")
        
        #-- Graph 1 Zoom Out --#
        self.zoom_out_graph1 = QtWidgets.QPushButton(self.Graph1_Section)
        self.zoom_out_graph1.setIcon(zoomOutIcon)
        self.zoom_out_graph1.setIconSize(QtCore.QSize(32,40))
        self.zoom_out_graph1.setGeometry(QtCore.QRect(1050, 0, 40, 40))
        self.zoom_out_graph1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.zoom_out_graph1.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid black;
                font-size: 40px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.zoom_out_graph1.setObjectName("zoom_out_graph1")
        
        #-- Graph 1 Show/Hide --#
        self.show_graph_1 = QtWidgets.QPushButton(self.Graph1_Section)
        self.show_graph_1.setIcon(showIcon)
        self.show_graph_1.setIconSize(QtCore.QSize(32,40))
        self.show_graph_1.setGeometry(QtCore.QRect(1140, 0, 40, 40))
        self.show_graph_1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.show_graph_1.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid black;
                font-size: 10px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.show_graph_1.setObjectName("show_graph_1")
        
        self.hide_graph_1 = QtWidgets.QPushButton( self.Graph1_Section)
        self.hide_graph_1.setIcon(hideIcon)
        self.hide_graph_1.setIconSize(QtCore.QSize(32,40))
        self.hide_graph_1.setGeometry(QtCore.QRect(1190, 0, 40, 40))
        self.hide_graph_1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.hide_graph_1.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid black;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }

        """)
        self.hide_graph_1.setObjectName("hide_graph_1")
        
        #-- Graph 1 Browse File --#
        self.browse_file_1 = QtWidgets.QPushButton("Browse File" , self.Graph1_Section)
        self.browse_file_1.setGeometry(QtCore.QRect(880, 390, 131, 41))
        self.browse_file_1.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.browse_file_1.setObjectName("browse_file_1")
        self.browse_file_1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.browse_file_1.clicked.connect(lambda : self.openSignalFile(self.graph1, 1))


        #-- Graph 1 Transfer --#
        self.change_to_graph_2 = QPushButton("Move to Graph 2", self.Graph1_Section)
        self.change_to_graph_2.setGeometry(QtCore.QRect(1100, 390, 180, 40))
        self.change_to_graph_2.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid black;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.change_to_graph_2.setObjectName("move_to_graph_2")
        self.change_to_graph_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        # Create and set the shadow effect
        shadow_effect = QtWidgets.QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(5)  # Adjust the blur radius
        shadow_effect.setXOffset(2)       # Horizontal offset of the shadow
        shadow_effect.setYOffset(2)       # Vertical offset of the shadow
        shadow_effect.setColor(QtGui.QColor(0, 0, 0))  # Shadow color
        self.change_to_graph_2.setGraphicsEffect(shadow_effect)

        #-- Graph 1 Change Color --#
        self.Change_color_1 = QtWidgets.QPushButton("Change Color", self.Graph1_Section)
        self.Change_color_1.setGeometry(QtCore.QRect(720, 390, 151, 41))
        self.Change_color_1.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.Change_color_1.setObjectName("Change_color_1")
        
        #-- Graph 1 High Speed --#
        self.high_speed_1 = QtWidgets.QPushButton("Speed (+)", self.Graph1_Section)
        self.high_speed_1.setGeometry(QtCore.QRect(480, 390, 111, 41))
        self.high_speed_1.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.high_speed_1.setObjectName("high_speed_1")
        self.high_speed_1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))        

        
        #-- Graph 1 Slow Speed --#
        self.slow_speed_1 = QtWidgets.QPushButton( "Speed (-)", self.Graph1_Section)
        self.slow_speed_1.setGeometry(QtCore.QRect(600, 390, 111, 41))
        self.slow_speed_1.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.slow_speed_1.setObjectName("slow_speed_1")
        self.slow_speed_1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))


        #-- Graph 1 Stop Simulating --#
        self.stop_graph_1 = QtWidgets.QPushButton(self.Graph1_Section)
        self.stop_graph_1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.stop_graph_1.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.stop_graph_1.setObjectName("start_graph_1")
        self.stop_graph_1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.stop_graph_1.setGeometry(QtCore.QRect(150, 390, 91, 41))
        self.stop_graph_1.setIcon(stopIcon)
        self.stop_graph_1.setIconSize(QtCore.QSize(32,32))


        #-- Graph 1 Start Simulating --#
        
        self.start_graph_1 = QtWidgets.QPushButton( self.Graph1_Section)
        self.start_graph_1.setGeometry(QtCore.QRect(60, 390, 81, 41))
        self.start_graph_1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.start_graph_1.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.start_graph_1.setObjectName("start_graph_1")
        self.start_graph_1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.start_graph_1.setIcon(startIcon)
        self.start_graph_1.setIconSize(QtCore.QSize(32, 32))

        #-- Graph 1 Rewind --#
        self.rewind_graph1 = QtWidgets.QPushButton(self.Graph1_Section)
        self.rewind_graph1.setGeometry(QtCore.QRect(250, 390, 91, 41))
        self.rewind_graph1.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.rewind_graph1.setObjectName("rewind_graph1")
        self.rewind_graph1.setIcon(rewindIcon)
        self.rewind_graph1.setIconSize(QtCore.QSize(32,32))

        # remove signal button will open a dialog to select the signal to remove from graph 1
        self.remove_signal_1 = QPushButton(self.Graph1_Section)
        self.remove_signal_1.setGeometry(QtCore.QRect(350, 390, 81, 41))
        self.remove_signal_1.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.remove_signal_1.setIcon(binIcon)
        self.remove_signal_1.setIconSize(QtCore.QSize(32,32))

        ##### Separator Line #####
        self.separator = QtWidgets.QFrame(self.Graph1_Section)
        self.separator.setGeometry(QtCore.QRect(0, 470, 1350, 10))  # Adjust Y position as needed
        self.separator.setFrameShape(QtWidgets.QFrame.HLine)  # Horizontal line
        self.separator.setFrameShadow(QtWidgets.QFrame.Sunken)  # Make it appear sunken
        self.separator.setStyleSheet("""
            QFrame{
                color: black;
                border: 20px solid black;
            }
        """)  # Optional: change color if needed


        #-- The Same Thing For Graph 2 --#
        self.Graph2_Section = QtWidgets.QWidget(self.centralwidget)
        self.Graph2_Section.setGeometry(QtCore.QRect(0, 520, 1281, 510))  # Match Graph 1 size and position
        self.Graph2_Section.setObjectName("Graph2_Section")
        

        self.Graph2 = QWidget(self.Graph2_Section)
        self.Graph2.setGeometry(QtCore.QRect(40, 35, 1200, 330))  # Match Graph 1 geometry
        self.Graph2.setObjectName("Graph2")
        graph_2_layout = QHBoxLayout(self.Graph2)  # Use QHBoxLayout to match Graph 1
        self.graph2 = pg.PlotWidget(title="Graph 2 Signals")
        graph_2_layout.addWidget(self.graph2)

        # Horizontal Slider for Graph 2
        self.graph_2_H_slider = QSlider(self.Graph2_Section)
        self.graph_2_H_slider.setGeometry(QtCore.QRect(40, 350, 1200, 30))  # Match Graph 1 slider geometry
        self.graph_2_H_slider.setOrientation(QtCore.Qt.Horizontal)
        self.graph_2_H_slider.setObjectName("graph_2_H_slider")
        self.graph_2_H_slider.setMinimum(0)
        self.graph_2_H_slider.setMaximum(5000)  # Adjust as needed
        self.graph_2_H_slider.setValue(0)
        self.graph_2_H_slider.setTickInterval(1)

        # Vertical Slider for Graph 2
        self.graph_2_V_slider = QSlider(self.Graph2_Section)
        self.graph_2_V_slider.setGeometry(QtCore.QRect(1250, 30, 30, 300))  # Match Graph 1 vertical slider
        self.graph_2_V_slider.setOrientation(QtCore.Qt.Vertical)
        self.graph_2_V_slider.setObjectName("graph_2_V_slider")

        # Zoom In for Graph 2
        self.zoom_in_graph2 = QtWidgets.QPushButton(self.Graph2_Section)
        self.zoom_in_graph2.setIcon(zoomInIcon)
        self.zoom_in_graph2.setIconSize(QtCore.QSize(32, 40))
        self.zoom_in_graph2.setGeometry(QtCore.QRect(1005, 0, 40, 40))  # Match Graph 1 button position
        self.zoom_in_graph2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.zoom_in_graph2.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid black;
                border-radius: 50px;
                font-size: 40px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.zoom_in_graph2.setObjectName("zoom_in_graph2")

        # Zoom Out for Graph 2
        self.zoom_out_graph2 = QtWidgets.QPushButton(self.Graph2_Section)
        self.zoom_out_graph2.setIcon(zoomOutIcon)
        self.zoom_out_graph2.setIconSize(QtCore.QSize(32, 40))
        self.zoom_out_graph2.setGeometry(QtCore.QRect(1050, 0, 40, 40))  # Match Graph 1 button position
        self.zoom_out_graph2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.zoom_out_graph2.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid black;
                font-size: 40px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.zoom_out_graph2.setObjectName("zoom_out_graph2")

        # Show/Hide Buttons for Graph 2
        self.show_graph_2 = QtWidgets.QPushButton(self.Graph2_Section)
        self.show_graph_2.setIcon(showIcon)
        self.show_graph_2.setIconSize(QtCore.QSize(32, 40))
        self.show_graph_2.setGeometry(QtCore.QRect(1140, 0, 40, 40))  # Match Graph 1 button position
        self.show_graph_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.show_graph_2.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid black;
                font-size: 10px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.show_graph_2.setObjectName("show_graph_2")


        self.hide_graph_2 = QtWidgets.QPushButton(self.Graph2_Section)
        self.hide_graph_2.setIcon(hideIcon)
        self.hide_graph_2.setIconSize(QtCore.QSize(32, 40))
        self.hide_graph_2.setGeometry(QtCore.QRect(1190, 0, 40, 40))  # Match Graph 1 button position
        self.hide_graph_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.hide_graph_2.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid black;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.hide_graph_2.setObjectName("hide_graph_2")

        # Browse File for Graph 2
        self.browse_file_2 = QPushButton("Browse File", self.Graph2_Section)
        self.browse_file_2.setGeometry(QtCore.QRect(880, 390, 131, 41))  # Match Graph 1 button position
        self.browse_file_2.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.browse_file_2.setObjectName("browse_file_2")
        self.browse_file_2.clicked.connect(lambda: self.openSignalFile(self.graph2, 2))

        # Change Color for Graph 2
        self.Change_color_2 = QtWidgets.QPushButton("Change Color", self.Graph2_Section)
        self.Change_color_2.setGeometry(QtCore.QRect(720, 390, 151, 41))  # Match Graph 1 button position
        self.Change_color_2.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.Change_color_2.setObjectName("Change_color_2")

        # High Speed for Graph 2
        self.high_speed_2 = QtWidgets.QPushButton("Speed (+)", self.Graph2_Section)
        self.high_speed_2.setGeometry(QtCore.QRect(480, 390, 111, 41))  # Match Graph 1 button position
        self.high_speed_2.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.high_speed_2.setObjectName("high_speed_2")

        # Slow Speed for Graph 2
        self.slow_speed_2 = QtWidgets.QPushButton("Speed (-)", self.Graph2_Section)
        self.slow_speed_2.setGeometry(QtCore.QRect(600, 390, 111, 41))  # Match Graph 1 button position
        self.slow_speed_2.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.slow_speed_2.setObjectName("slow_speed_2")

        # Stop Simulating for Graph 2
        self.stop_graph_2 = QtWidgets.QPushButton(self.Graph2_Section)
        self.stop_graph_2.setGeometry(QtCore.QRect(150, 390, 91, 41))  # Match Graph 1 button position
        self.stop_graph_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.stop_graph_2.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.stop_graph_2.setObjectName("stop_graph_2")
        self.stop_graph_2.setIcon(stopIcon)
        self.stop_graph_2.setIconSize(QtCore.QSize(32, 32))

        # Start Simulating for Graph 2
        self.start_graph_2 = QtWidgets.QPushButton(self.Graph2_Section)
        self.start_graph_2.setGeometry(QtCore.QRect(60, 390, 81, 41))  # Match Graph 1 button position
        self.start_graph_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.start_graph_2.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.start_graph_2.setObjectName("start_graph_2")
        self.start_graph_2.setIcon(startIcon)
        self.start_graph_2.setIconSize(QtCore.QSize(32, 32))

        # Rewind for Graph 2
        self.rewind_graph2 = QtWidgets.QPushButton(self.Graph2_Section)
        self.rewind_graph2.setGeometry(QtCore.QRect(250, 390, 91, 41))  # Match Graph 1 button position
        self.rewind_graph2.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.rewind_graph2.setObjectName("rewind_graph2")
        self.rewind_graph2.setIcon(rewindIcon)
        self.rewind_graph2.setIconSize(QtCore.QSize(32, 32))

        # Remove Signal for Graph 2
        self.remove_signal_2 = QPushButton(self.Graph2_Section)
        self.remove_signal_2.setGeometry(QtCore.QRect(350, 390, 81, 41))  # Match Graph 1 button position
        self.remove_signal_2.setStyleSheet("font-weight:bold;font-size:16px;background-color:white;border:2px solid black;border-radius:10px;")
        self.remove_signal_2.setIcon(binIcon)
        self.remove_signal_2.setIconSize(QtCore.QSize(32, 32))
        self.remove_signal_2.setObjectName("remove_signal_2")

                #-- Graph 1 Transfer --#
        self.change_to_graph_1 = QPushButton("Move to Graph 1", self.Graph2_Section)
        self.change_to_graph_1.setGeometry(QtCore.QRect(1100, 390, 180, 40))
        self.change_to_graph_1.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid black;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        # Create and set the shadow effect
        shadow_effect = QtWidgets.QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(5)  # Adjust the blur radius
        shadow_effect.setXOffset(2)       # Horizontal offset of the shadow
        shadow_effect.setYOffset(2)       # Vertical offset of the shadow
        shadow_effect.setColor(QtGui.QColor(0, 0, 0))  # Shadow color
        self.change_to_graph_1.setGraphicsEffect(shadow_effect)



        # Menu Bar for more features.
        # For each menubar we need actions ? -> To Add Action while clicking on it (make sense)

        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1290, 20))
        self.menubar.setObjectName("menubar")
        self.menubar.setStyleSheet("QMenuBar { background-color: white; }")


        self.menuOptions = QtWidgets.QMenu("Signal Options",self.menubar)
        self.menuOptions.setObjectName("Signal Options")
        self.setMenuBar(self.menubar)

        self.actionApiData = QtWidgets.QAction("API Data",self)
        self.actionApiData.setObjectName("API Data")
        self.actionApiData.triggered.connect(self.apiData)

        self.actionLink_Signals = QtWidgets.QAction("Link Signals",self)
        self.actionLink_Signals.setObjectName("Link Signals")
        self.actionLink_Signals.triggered.connect(self.toggleLinkedSignals)

        self.actionSignal_Glue = QtWidgets.QAction("Signal Glue",self)
        self.actionSignal_Glue.setObjectName("Signal Glue")
        self.actionSignal_Glue.triggered.connect(self.show_signal_selection_dialog)

        self.menuOptions.addAction(self.actionApiData)
        self.menuOptions.addAction(self.actionLink_Signals)
        self.menuOptions.addAction(self.actionSignal_Glue)
        self.menubar.addAction(self.menuOptions.menuAction())

        self.coordinates = self.menubar.addMenu('Polar Coordinates')
        self.actionPolarCoordinates = QtWidgets.QAction("Show Polar ECG Plot", self)
        self.coordinates.addAction(self.actionPolarCoordinates)
        self.actionPolarCoordinates.triggered.connect(lambda: self.show_ecg_plot())

        QtCore.QMetaObject.connectSlotsByName(self)

        self.setup_buttons_connections()


    def toggleLinkedSignals(self):
        if not self.linkedSignals:
            self.linkedSignals = True
            self.graph1.clear()
            self.graph2.clear()
        else:
            self.linkedSignals = False
            self.timer_linked_graphs.stop()
            self.graph1.clear()
            self.graph2.clear()
    
    def get_random_color(self):
        return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def openSignalFile(self, Graph, graphNum):
        signalData = ""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Signal File", "", "File Extension (*.csv *.dat)", options=options)

        if file_path:
            try:
                if graphNum == 1:
                    print(f"The Length of list = {len(self.graph_1_files)}")
                    if file_path not in self.graph_1_files:
                        self.graph_1_files.append(file_path)
                        self.graph1_colors.append(self.get_random_color())  # Assign a random color for the signal
                    
                    self.timer_graph_1.stop()
                    signalData = self.loadSignalData(file_path,1)
                    self.signalPlotting(self.graph1, signalData, 1)  # Plot the new data on graph 1

                else:
                    print(f"The Length of list = {len(self.graph_2_files)}")

                    if file_path not in self.graph_2_files: 
                        self.graph_2_files.append(file_path)
                        self.graph2_colors.append(self.get_random_color())  # Assign a random color for the signal
                    
                    self.timer_graph_2.stop()
                    signalData = self.loadSignalData(file_path,2)
                    self.signalPlotting(self.graph2, signalData, 2)  # Plot the new data on graph 2

                if signalData is None:
                    print("No valid signal data found.")
                    return

            except Exception as e:
                print(f"Couldn't open signal file: {str(e)}")

    def loadSignalData(self, file_path, graphNum):
        try:
            # Load the Signal file.
            signalData = np.loadtxt(file_path, delimiter=',')
            
            # Check if any data was  loaded
            if signalData is None or signalData.size == 0:
                print(f"File at {file_path} contains no data.")
                return None

            if graphNum == 1:
                self.graph1.setLimits(xMin=0, xMax=len(signalData), yMin=min(signalData), yMax=max(signalData))
            else:
                self.graph2.setLimits(xMin=0, xMax=len(signalData), yMin=min(signalData), yMax=max(signalData))
            
            return signalData
        except ValueError as ve:
            print(f"Failed to load signal data from {file_path}: {ve}")
            return None
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred while loading signal data: {e}")
            return None

    def signalPlotting(self, Graph, signalData, GraphNum):
        if self.linkedSignals:
            self.timer_graph_1.stop()
            self.timer_graph_2.stop()

            self.time_index_linked_graphs = 0
            self.timer_linked_graphs.timeout.connect(lambda: self.slide_through_data(Graph, signalData, 3))
            self.timer_linked_graphs.start(200)
        else:
            if GraphNum == 1:
                self.timer_graph_1.stop()
                self.time_index_graph_1 = 0
                self.timer_graph_1.timeout.connect(lambda: self.slide_through_data(Graph, signalData, GraphNum))
                self.timer_graph_1.start(200)
            else:
                self.timer_graph_2.stop()
                self.time_index_graph_2 = 0
                self.timer_graph_2.timeout.connect(lambda: self.slide_through_data(Graph, signalData, GraphNum))
                self.timer_graph_2.start(200)

    def slide_through_data(self, Graph, signalData, GraphNum):
        if signalData is None or len(signalData) == 0:
            print("There's no signal data.")
            return

        # Plot all signals on the graph with different colors
        if self.linkedSignals:
            Graph.clear()
            for i, signal in enumerate(self.graph_1_files + self.graph_2_files):
                color = self.linked_graphs_color if i < len(self.graph_1_files) else self.graph2_colors[i - len(self.graph_1_files)]
                Graph.plot(signalData[:self.time_index_linked_graphs + 1], pen=color)

            if self.time_index_linked_graphs > self.windowSize:
                Graph.setXRange(self.time_index_linked_graphs - self.windowSize + 1, self.time_index_linked_graphs + 1)
            else:
                Graph.setXRange(0, self.windowSize)

            self.time_index_linked_graphs += 5
            if self.time_index_linked_graphs >= len(signalData):
                self.timer_linked_graphs.stop()
                self.timer_graph_1.stop()
                self.timer_graph_2.stop()

        else:
            if GraphNum == 1:
                Graph.clear()
                for i, file in enumerate(self.graph_1_files):
                    signal = self.loadSignalData(file, 1)
                    Graph.plot(signal[:self.time_index_graph_1 + 1], pen=self.graph1_colors[i])

                if self.time_index_graph_1 > self.windowSize:
                    Graph.setXRange(self.time_index_graph_1 - self.windowSize + 1, self.time_index_graph_1 + 1)
                else:
                    Graph.setXRange(0, self.windowSize)

                self.time_index_graph_1 += 5
                if self.time_index_graph_1 >= len(signalData):
                    self.timer_graph_1.stop()
            else:
                Graph.clear()
                for i, file in enumerate(self.graph_2_files):
                    signal = self.loadSignalData(file, 2)
                    Graph.plot(signal[:self.time_index_graph_2 + 1], pen=self.graph2_colors[i])

                if self.time_index_graph_2 > self.windowSize:
                    Graph.setXRange(self.time_index_graph_2 - self.windowSize + 1, self.time_index_graph_2 + 1)
                else:
                    Graph.setXRange(0, self.windowSize)

                self.time_index_graph_2 += 5
                if self.time_index_graph_2 >= len(signalData):
                    self.timer_graph_2.stop() 

    def openColorChangeDialog(self, GraphNum):
        # Check if any signals are loaded in either graph
        if len(self.graph_1_files) == 0 and len(self.graph_2_files) == 0:
            print("No signals loaded to change color.")
            return
        
        # Create a dialog to choose the signal
        if GraphNum == 1:
            #This return the Selected Signal and if the signal is selected or not
            signalSelector, isPressed = QInputDialog.getItem(
                self,
                "Select Signal",
                "Choose the signal to change its color:",
                self.graph_1_files,  # Combine signals from both graphs
                0,
                False
            )
            if isPressed and signalSelector:
                # get the index of the signal that the user choose
                signalIndex = (self.graph_1_files).index(signalSelector)
                if signalIndex < len(self.graph_1_files):
                    # Open a color picker dialog
                    newColor = QColorDialog.getColor()
                    if newColor.isValid():
                        self.updateSignalColor(1, signalIndex, newColor)
            else:
                print("Invalid color selected.")
       
        else:
            # This return the Selected Signal and if the signal is selected or not
            signalSelector, isPressed = QInputDialog.getItem(
                self,
                "Select Signal",
                "Choose the signal to change its color:",
                self.graph_2_files,  # Combine signals from both graphs
                0,
                False
            )
            if isPressed and signalSelector:
                # get the index of the signal that the user choose
                signalIndex = (self.graph_2_files).index(signalSelector)
                if signalIndex < len(self.graph_2_files):
                    # Open a color picker dialog
                    newColor = QColorDialog.getColor()
                    if newColor.isValid():
                        self.updateSignalColor(2, signalIndex, newColor)
            else:
                print("Invalid color selected.")

    
    def updateSignalColor(self, graphNum, signalIndex, newColor):
        if graphNum == 1:
            # Update color for the selected signal in graph 1
            self.graph1_colors[signalIndex] = newColor
        else:
            # Update color for the selected signal in graph 2
            self.graph2_colors[signalIndex] = newColor


class SignalSelectionDialog(QDialog):
    def __init__(self, graph_1_files, graph_2_files, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Signals")
        self.graph_1_files = graph_1_files
        self.graph_2_files = graph_2_files
        self.selected_signal_1 = None
        self.selected_signal_2 = None
        self.setupUi()

    def setupUi(self):
        layout = QVBoxLayout(self)

        # ComboBox for selecting signal from graph 1
        self.comboBox1 = QComboBox(self)
        self.comboBox1.addItems(self.graph_1_files)
        layout.addWidget(QLabel("Select Signal from Graph 1:"))
        layout.addWidget(self.comboBox1)

        # ComboBox for selecting signal from graph 2
        self.comboBox2 = QComboBox(self)
        self.comboBox2.addItems(self.graph_2_files)
        layout.addWidget(QLabel("Select Signal from Graph 2:"))
        layout.addWidget(self.comboBox2)

        # OK and Cancel buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.cancel_button = QPushButton("Cancel", self)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def accept(self):
        self.selected_signal_1 = self.comboBox1.currentText()
        self.selected_signal_2 = self.comboBox2.currentText()
        super().accept()

    def reject(self):
        super().reject() 

class SignalSelectionDialogRemove(QDialog):
    # take the signals from the graph and remove the selected signal 
    def __init__(self, graph_1_files, graph_2_files, graph_num, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Signals")
        self.graph_1_files = graph_1_files
        self.graph_2_files = graph_2_files
        self.selected_signal = None
        self.graph_num = graph_num
        self.setupUi()

    def setupUi(self):
        layout = QVBoxLayout(self)

        # ComboBox for selecting signal from graph 1
        self.comboBox = QComboBox(self)
        if self.graph_num == 1:
            self.comboBox.addItems(self.graph_1_files)
        else:
            self.comboBox.addItems(self.graph_2_files)
        layout.addWidget(QLabel(f"Select Signal from Graph {self.graph_num}:"))
        layout.addWidget(self.comboBox)

        # OK and Cancel buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.cancel_button = QPushButton("Cancel", self)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Connect buttons
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def accept(self):
        self.selected_signal = self.comboBox.currentText()
        super().accept()

    def reject(self):
        super().reject()




def main():
    app = QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
