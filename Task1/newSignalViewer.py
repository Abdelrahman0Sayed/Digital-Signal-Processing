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
from functions_graph import increase_speed, decrease_speed, start_simulation, stop_simulation, rewind, change_color, export_to_pdf, remove_signal,remove_linked_signals
from nonRectangular import PolarEcgPlot
from PyQt5 import QtCore, QtGui, QtWidgets
from nonRectangular2 import CombinedRespiratoryPlot

class Ui_MainWindow(QMainWindow):

    def remove_signal(self ,graph_num):
        if self.linkedSignals:
            for i,signal in enumerate(self.graph_1_files):
                self.deleteSignalFromList(1, signal)
            for i,signal in enumerate(self.graph_2_files):
                self.deleteSignalFromList(2, signal)
            remove_linked_signals(self)
        
        else:
            if graph_num == 1:
                file_to_delete= self.directoryPath + "/"+ self.graph_1_selected_file
                self.deleteSignalFromList(1, self.graph_1_selected_file)
                remove_signal(self, self.linkedSignals, 1, file_to_delete)
            else:
                file_to_delete= self.directoryPath + "/" + self.graph_2_selected_file
                self.deleteSignalFromList(2, self.graph_2_selected_file)
                remove_signal(self, self.linkedSignals, 2, file_to_delete)


    def deleteSignalFromList(self, graphNum, selectedSignal):
        if graphNum == 1:
            item_to_delete = None
            for i in range(self.fileListWidgetGraph1.count()):
                item = self.fileListWidgetGraph1.item(i)
                if item.text() == selectedSignal:
                    item_to_delete = item
                    break

            if item_to_delete:
                self.fileListWidgetGraph1.takeItem(self.fileListWidgetGraph1.row(item_to_delete))
                print(f"Deleted file: {selectedSignal}")
            else:
                print(f"Signal '{selectedSignal}' not found in the list.")
        else:
                       
            item_to_delete = None
            for i in range(self.fileListWidgetGraph2.count()):
                item = self.fileListWidgetGraph2.item(i)
                if item.text() == selectedSignal:
                    item_to_delete = item
                    break

            if item_to_delete:
                self.fileListWidgetGraph2.takeItem(self.fileListWidgetGraph2.row(item_to_delete))
                print(f"Deleted file: {selectedSignal}")
            else:
                print(f"Signal '{selectedSignal}' not found in the list.")


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
    def move_to_graph_1_to_2(self, selectedSignal):
        if len(self.graph_1_files) > 0:
            movedSignal  = self.directoryPath + "/" +selectedSignal 
            signalIndex = 0
            for i, signal in enumerate(self.graph_1_files):
                if signal == movedSignal:
                    signalIndex = i
                    break
            
            self.swapSignalsBetweenLists(1, selectedSignal)
            # Move the last signal from graph 1 to graph 2
            self.graph_2_files.append(self.graph_1_files.pop(signalIndex))  # Move file from graph 1 to graph 2
            self.graph2_colors.append(self.graph1_colors.pop(signalIndex))  # Move color from graph 1 to graph 2


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



    def move_to_graph_2_to_1(self, selectedSignal):
        if len(self.graph_2_files) > 0:
            signalIndex = 0
            movedSignal = self.directoryPath + "/" + selectedSignal
            print(movedSignal)
            for i, signal in enumerate(self.graph_2_files):
                if signal == movedSignal:
                    signalIndex = i
                    break
            
            self.swapSignalsBetweenLists(2, selectedSignal)

            # Move the last signal from graph 2 to graph 1
            self.graph_1_files.append(self.graph_2_files.pop(signalIndex))  # Move file from graph 2 to graph 1
            self.graph1_colors.append(self.graph2_colors.pop(signalIndex))  # Move color from graph 2 to graph 1


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


    
    def swapSignalsBetweenLists(self, DeleteFrom, selectedSignal):
        if DeleteFrom == 1:
            print(f"We Move {selectedSignal} from Graph 1 to Graph 2")
            self.fileListWidgetGraph2.addItem(selectedSignal)
            self.deleteSignalFromList(1, selectedSignal)
        else:
            print(f"We Move {selectedSignal} from Graph 1 to Graph 2")
            self.fileListWidgetGraph1.addItem(selectedSignal)
            self.deleteSignalFromList(2, selectedSignal)


    def show_old_ecg_plot(self):
        print("Start Non Rectangular Coordinates")
        self.ecg_plot_window = PolarEcgPlot()
        all_signals = self.graph_1_files + self.graph_2_files
        all_colors = self.graph1_colors = self.graph2_colors
        self.ecg_plot_window.LoadEcgSignals(all_signals, all_colors)
        self.ecg_plot_window.show()
        

    def show_new_ecg_plot(self):
        print("Start Non Rectangular Coordinates")
        self.ecg_plot_window = CombinedRespiratoryPlot()
        self.ecg_plot_window.show()



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


    def toggleIcons(self, isLinked, GraphNum):
        if isLinked:
            if self.timer_linked_graphs.isActive():
                self.startOrPauseGraph1.setIcon(self.stopIcon)
                self.startOrPauseGraph2.setIcon(self.stopIcon)
                self.linkedPlayingMode = "stop"
            else:
                self.startOrPauseGraph1.setIcon(self.startIcon)
                self.startOrPauseGraph2.setIcon(self.startIcon)
                self.linkedPlayingMode = "start"
        else: 
            if GraphNum == 1:
                if not self.timer_graph_1.isActive():
                    self.startOrPauseGraph1.setIcon(self.startIcon)
                    self.playingModeGraph1 = "stop"
                else:
                    self.startOrPauseGraph1.setIcon(self.stopIcon)
                    self.playingModeGraph1 = "start"
            else:
                if not self.timer_graph_2.isActive():
                    self.startOrPauseGraph2.setIcon(self.startIcon)
                    self.playingModeGraph2 = "stop"
                else:
                    self.startOrPauseGraph2.setIcon(self.stopIcon)
                    self.playingModeGraph2 = "start"
            

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.setWindowTitle("Multi-Channel Signal Viewer")
        self.setStyleSheet("background-color:black; color:white")
           
        self.graph_1_files = []  # Store file paths for Graph 1 signals
        self.graph_2_files = []  # Store file paths for Graph 2 signals
        self.graph1_colors = []  # Store colors for each signal in Graph 1
        self.graph2_colors = []  # Store colors for each signal in Graph 2
        self.playingModeGraph1 = "stop"
        self.playingModeGraph2 = "stop"
        self.linkedPlayingMode = "start"
        self.directoryPath = ""
        

        self.linked_graphs_color = self.get_random_color()

        self.graph_1_selected_file= ""
        self.graph_2_selected_file= ""

        self.timer_graph_1 = QTimer(self)  # Used primarily for cine mode
        self.time_index_graph_1 = 0  # For Cine Mode Scrolling

        self.timer_graph_2 = QTimer(self)  # Used primarily for cine mode
        self.time_index_graph_2 = 0  # For Cine Mode Scrolling

        self.timer_linked_graphs = QTimer(self)  # Used primarily for cine mode
        self.time_index_linked_graphs = 0  # For Cine Mode Scrolling

        self.linkedSignals = False
        self.isPlayed = True

        self.ecg_plot_window = None  # Instance variable to keep reference
        self.windowSize = 200




    def setup_buttons_connections(self):
        # Button connections for Graph 1
       
        self.moveToGraph2.clicked.connect(lambda: self.move_to_graph_1_to_2(self.graph_1_selected_file))
        self.speedUpGraph1.clicked.connect(lambda: increase_speed(self, self.linkedSignals, 1))
        self.speedDownGraph1.clicked.connect(lambda: decrease_speed(self, self.linkedSignals, 1))
        self.startOrPauseGraph1.clicked.connect(lambda: start_simulation(self ,self.linkedSignals, 1))
        self.rewindGraph1.clicked.connect(lambda: rewind(self, self.linkedSignals , 1))
        self.changeColorGraph1.clicked.connect(lambda: self.openColorChangeDialog(1))
        #self.export_graph1.clicked.connect(lambda: export_to_pdf(self, self.linkedSignals, 1))


        # Button connections for Graph 2
        self.moveToGraph1.clicked.connect(lambda: self.move_to_graph_2_to_1(self.graph_2_selected_file))
        self.speedUpGraph2.clicked.connect(lambda: increase_speed(self, self.linkedSignals, 2))
        self.speedDownGraph2.clicked.connect(lambda: decrease_speed(self, self.linkedSignals, 2))
        self.startOrPauseGraph2.clicked.connect(lambda: start_simulation(self ,self.linkedSignals, 2))
        self.rewindGraph2.clicked.connect(lambda: rewind(self, self.linkedSignals, 2))
        self.changeColorGraph2.clicked.connect(lambda: self.openColorChangeDialog(2))
        #self.export_graph2.clicked.connect(lambda: export_to_pdf(self, self.linkedSignals, 2))


        # self.change_to_graph_1.clicked.connect(self.move_to_graph_2_to_1)
        # self.change_to_graph_2.clicked.connect(self.move_to_graph_1_to_2)

    
        #remove signal button will open a dialog to select the signal to remove from graph 1
        self.deleteSignalGraph1.clicked.connect(lambda: self.remove_signal(1))

        #remove signal button will open a dialog to select the signal to remove from graph 2
        self.deleteSignalGraph2.clicked.connect(lambda: self.remove_signal(2))
    

    

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(1600, 1000)

        self.startIcon =QtGui.QIcon("images/play.png")
        self.stopIcon = QtGui.QIcon("images/pause.png")
        self.rewindIcon = QtGui.QIcon("images/rewind.png")
        self.showIcon = QtGui.QIcon("images/show.png")
        self.hideIcon = QtGui.QIcon("images/hide.png")
        self.zoomInIcon = QtGui.QIcon("images/zoom_in.png")
        self.zoomOutIcon = QtGui.QIcon("images/zoom_out.png")
        binIcon = QtGui.QIcon("images/bin.png")

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.gridLayout.setObjectName("gridLayout")

        
        self.Graph1Widget = QtWidgets.QWidget(self.centralwidget)
        self.Graph1Widget.setObjectName("Graph1Widget")
        self.Graph1Widget.setStyleSheet("""
            QWidget{
                border-radius:10px;
                border: 2px solid #a5a5a5;                
            }
        """)
        self.Graph1Layout = QHBoxLayout(self.Graph1Widget)
        # Set up the graph
        self.graph1 = pg.PlotWidget()
        self.graph1.showGrid(x=True, y=True)
        self.legend1 = self.graph1.addLegend()

        # Function to toggle visibility
        def toggle_visibility(event, item):
            print(item)
            plot_item = item.item
            plot_item.setVisible(not plot_item.isVisible())
        
        # Iterate over legend items to connect click events
        for item in self.legend1.items:
            label, sample = item
            sample.mousePressEvent = lambda evt, itm=label: toggle_visibility(evt, itm)
        
        # Add the graph to the layout
        self.Graph1Layout.addWidget(self.graph1)
        self.gridLayout.addWidget(self.Graph1Widget, 1, 0, 1, 7)

    


        
        # Create your widget and set basic properties
        self.widget_2 = QtWidgets.QWidget(self.centralwidget)
        self.widget_2.setObjectName("widget_2")
        self.widget_2.setMinimumWidth(350)
        self.widget_2.setMaximumWidth(450)
        self.widget_2.setStyleSheet("""
            QWidget{
                background-color: #212529;
                border-radius:10px;
                border: 2px solid #a5a5a5;    
            }                        
        """)

        # Create a vertical layout for the widget (no need for setGeometry)
        Graph1SideButtonsLayout = QtWidgets.QVBoxLayout(self.widget_2)
        
        # Label for the list of signals
        self.label = QtWidgets.QLabel("List of Signals", self.widget_2)
        self.label.setStyleSheet("color: black; background-color: #a5a5a5; font-size: 16px; font-weight: bold;padding:10px")
        self.label.setAlignment(Qt.AlignCenter)
        Graph1SideButtonsLayout.addWidget(self.label)

        # Add QListWidget to display the signal files
        self.fileListWidgetGraph1 = QtWidgets.QListWidget(self.widget_2)
        self.fileListWidgetGraph1.setStyleSheet("""
            QListWidget  {
                background-color: #0a0908;
                color: black;
                border-radius: 10px;
                font-weight: bold;
                color: white;
            }
        """)
        list1Font = QtGui.QFont("Arial", 10, QtGui.QFont.Bold)
        self.fileListWidgetGraph1.setFont(list1Font)
        Graph1SideButtonsLayout.addWidget(self.fileListWidgetGraph1)
        self.fileListWidgetGraph1.itemClicked.connect(
            lambda item: self.fileSelected(item, 1)
        )


        row_1_layout = QtWidgets.QHBoxLayout()

        Graph1SideButtonsLayout.addLayout(row_1_layout)
        self.moveToGraph2 = QtWidgets.QPushButton("Move to Graph 2")
        self.moveToGraph2.setStyleSheet("""
            QPushButton{
                background-color: #a5a5a5;
                padding: 10px;
                font-weight: bold;
                font-size: 15px;
                color: black;
                border-radius:0                             
            }        
        """)
        self.moveToGraph2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        Graph1SideButtonsLayout.addWidget(self.moveToGraph2)

        self.gridLayout.addWidget(self.widget_2, 1, 7, 2, 1)


        self.changeColorGraph1 = QtWidgets.QPushButton(self.centralwidget)
        self.changeColorGraph1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.changeColorGraph1.setObjectName("changeColorGraph1")
        self.changeColorGraph1.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:15px;padding:10px;border:2px solid black;
            }
        """)
        self.gridLayout.addWidget(self.changeColorGraph1, 2, 1, 1, 1)
        
        self.browseFileGraph1 = QtWidgets.QPushButton(self.centralwidget)
        self.browseFileGraph1.setObjectName("browse File Graph 1")
        self.browseFileGraph1.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:15px;padding:10px;border:2px solid black;
            }
        """)
        self.browseFileGraph1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.browseFileGraph1.clicked.connect(lambda : self.openSignalFile(self.graph1, 1))
        self.gridLayout.addWidget(self.browseFileGraph1, 2, 0, 1, 1)


        self.startOrPauseGraph1 = QtWidgets.QPushButton(self.centralwidget)
        self.startOrPauseGraph1.setObjectName("startOrPauseGraph1")
        self.gridLayout.addWidget(self.startOrPauseGraph1, 2, 2, 1, 1)
        self.startOrPauseGraph1.setMaximumWidth(100)
        self.startOrPauseGraph1.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:20px;border:2px solid black;                            
            }
        """)
        self.startOrPauseGraph1.setIcon(self.stopIcon)
        self.startOrPauseGraph1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.startOrPauseGraph1.setIconSize(QtCore.QSize(40,40))

        self.rewindGraph1 = QtWidgets.QPushButton(self.centralwidget)
        self.rewindGraph1.setObjectName("rewindGraph1")
        self.gridLayout.addWidget(self.rewindGraph1, 2, 3, 1, 1)
        self.rewindGraph1.setMaximumWidth(100)
        self.rewindGraph1.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:20px;border:2px solid black;                            
            }
        """)
        self.rewindGraph1.setIcon(self.rewindIcon)
        self.rewindGraph1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.rewindGraph1.setIconSize(QtCore.QSize(40,40))
        
        self.deleteSignalGraph1 = QtWidgets.QPushButton(self.centralwidget)
        self.deleteSignalGraph1.setObjectName("deleteSignalGraph1")
        self.deleteSignalGraph1.setMaximumWidth(100)
        self.deleteSignalGraph1.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:20px;border:2px solid black; padding:5px                           
            }
        """)
        self.deleteSignalGraph1.setIcon(binIcon)
        self.deleteSignalGraph1.setIconSize(QtCore.QSize(30,30))
        self.deleteSignalGraph1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.gridLayout.addWidget(self.deleteSignalGraph1, 2, 4, 1, 1)
        self.gridLayout.setSpacing(20)


        self.speedUpGraph1 = QtWidgets.QPushButton(self.centralwidget)
        self.speedUpGraph1.setObjectName("speedUpGraph1")
        self.speedUpGraph1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.speedUpGraph1.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:15px;padding:10px;border:2px solid black;
            }
        """)
        self.gridLayout.addWidget(self.speedUpGraph1, 2, 5, 1, 1)
        
        self.speedDownGraph1 = QtWidgets.QPushButton(self.centralwidget)
        self.speedDownGraph1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.speedDownGraph1.setObjectName("speedDownGraph1")
        self.speedDownGraph1.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:15px;padding:10px;border:2px solid black;
            }
        """)
        self.gridLayout.addWidget(self.speedDownGraph1, 2, 6, 1, 1)
        


        



        # -------------------- Graph 2 --------------------------------#
        self.Graph2Widget = QtWidgets.QWidget(self.centralwidget)
        self.Graph2Widget.setObjectName("Graph1Widget")
        self.Graph2Widget.setStyleSheet("""
            QWidget{
                border-radius:10px;
                border: 2px solid #a5a5a5;                
            }
        """)
        self.Graph2Layout = QHBoxLayout(self.Graph2Widget)        
        self.graph2 = pg.PlotWidget()
        self.graph2.showGrid(x=True, y=True)
        self.legend2 = self.graph2.addLegend()

        # Function to toggle visibility
        def toggle_visibility(event, item):
            plot_item = item.item
            plot_item.setVisible(not plot_item.isVisible())
        
        # Iterate over legend items to connect click events
        for item in self.legend2.items:
            label, sample = item
            sample.mousePressEvent = lambda evt, itm=label: toggle_visibility(evt, itm)
        
        # Add the graph to the layout
        self.Graph2Layout.addWidget(self.graph2)
        self.gridLayout.addWidget(self.Graph2Widget, 3, 0, 1, 7)



        self.widget_4 = QtWidgets.QWidget(self.centralwidget)
        self.widget_4.setObjectName("widget_4")
        self.widget_4.setMinimumWidth(350)
        self.widget_4.setMaximumWidth(450)
        self.widget_4.setStyleSheet("""
            QWidget{
                background-color: #212529;
                border-radius:10px;
                border: 2px solid #a5a5a5;    
            }                        
        """)
        Graph2SideButtonsLayout = QtWidgets.QVBoxLayout(self.widget_4)

        self.label_2 = QtWidgets.QLabel("List of Signals", self.widget_4)
        self.label_2.setStyleSheet("color: black; background-color: #a5a5a5; font-size: 16px; font-weight: bold;padding:10px")
        self.label_2.setAlignment(Qt.AlignCenter)
        Graph2SideButtonsLayout.addWidget(self.label_2)
        self.gridLayout.addWidget(self.widget_4, 3, 7, 2, 1)
        
        #Add QListWidget to display the signal files
        self.fileListWidgetGraph2 = QtWidgets.QListWidget(self.widget_4)
        self.fileListWidgetGraph2.setStyleSheet("""
            QListWidget {
                background-color: #0a0908;
                color: black;
                border-radius: 10px;
                font-weight: bold;
                color: white;
            }
        """)
        list2Font = QtGui.QFont("Arial", 10, QtGui.QFont.Bold)
        self.fileListWidgetGraph2.setFont(list2Font)
        Graph2SideButtonsLayout.addWidget(self.fileListWidgetGraph2)
        self.fileListWidgetGraph2.itemClicked.connect(
            lambda item: self.fileSelected(item, 2)
        )
        row_1_layout_graph_2 = QtWidgets.QHBoxLayout()
        Graph2SideButtonsLayout.addLayout(row_1_layout_graph_2)
        self.moveToGraph1 = QtWidgets.QPushButton("Move to Graph 1")
        self.moveToGraph1.setStyleSheet("""
            QPushButton{
                background-color: #a5a5a5;
                padding: 10px;
                font-weight: bold;
                font-size: 15px;
                color: black;
                border-radius:0                             
            }        
        """)
        self.moveToGraph1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        Graph2SideButtonsLayout.addWidget(self.moveToGraph1)

        self.changeColorGraph2 = QtWidgets.QPushButton(self.centralwidget)
        self.changeColorGraph2.setObjectName("pushButton_12")
        self.changeColorGraph2.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:15px;padding:10px;border:2px solid black;
            }
        """)
        self.gridLayout.addWidget(self.changeColorGraph2, 4, 1, 1, 1)
        
        self.browseFileGraph2 = QtWidgets.QPushButton(self.centralwidget)
        self.browseFileGraph2.setObjectName("pushButton_13")
        self.browseFileGraph2.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:15px;padding:10px;border:2px solid black;
            }
        """)
        self.browseFileGraph2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.browseFileGraph2.clicked.connect(lambda : self.openSignalFile(self.graph2, 2))

        self.gridLayout.addWidget(self.browseFileGraph2, 4, 0, 1, 1)


        self.startOrPauseGraph2 = QtWidgets.QPushButton(self.centralwidget)
        self.startOrPauseGraph2.setObjectName("startOrPauseGraph2")
        self.startOrPauseGraph2.setMaximumWidth(100)
        self.startOrPauseGraph2.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:20px;border:2px solid black;                            
            }
        """)
        self.startOrPauseGraph2.setIcon(self.stopIcon)
        self.startOrPauseGraph2.setIconSize(QtCore.QSize(40,40))
        self.gridLayout.addWidget(self.startOrPauseGraph2, 4, 2, 1, 1)
        
        self.rewindGraph2 = QtWidgets.QPushButton(self.centralwidget)
        self.rewindGraph2.setObjectName("pushButton_14")
        self.rewindGraph2.setMaximumWidth(100)
        self.rewindGraph2.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:20px;border:2px solid black;                            
            }
        """)
        self.rewindGraph2.setIcon(self.rewindIcon)
        self.rewindGraph2.setIconSize(QtCore.QSize(40,40))
        self.gridLayout.addWidget(self.rewindGraph2, 4, 3, 1, 1)
        
        self.deleteSignalGraph2 = QtWidgets.QPushButton(self.centralwidget)
        self.deleteSignalGraph2.setObjectName("pushButton_10")
        self.deleteSignalGraph2.setMaximumWidth(100)
        self.deleteSignalGraph2.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:20px;border:2px solid black;padding:5px;                            
            }
        """)
        self.deleteSignalGraph2.setIcon(binIcon)
        self.deleteSignalGraph2.setIconSize(QtCore.QSize(30,30))
        self.gridLayout.addWidget(self.deleteSignalGraph2, 4, 4, 1, 1)
        
        self.speedUpGraph2 = QtWidgets.QPushButton(self.centralwidget)
        self.speedUpGraph2.setObjectName("pushButton_9")
        self.speedUpGraph2.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:15px;padding:10px;border:2px solid black;
            }
        """)
        self.gridLayout.addWidget(self.speedUpGraph2, 4, 5, 1, 1)
        
        self.speedDownGraph2 = QtWidgets.QPushButton(self.centralwidget)
        self.speedDownGraph2.setObjectName("pushButton_11")
        self.speedDownGraph2.setStyleSheet("""
            QPushButton{
                background-color:white;color:black;font-weight:bold;border-radius:10px;font-size:15px;padding:10px;border:2px solid black;
            }
        """)
        self.gridLayout.addWidget(self.speedDownGraph2, 4, 6, 1, 1)
        

        
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        

        self.setup_buttons_connections()
        



        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1290, 20))
        self.menubar.setObjectName("menubar")
        self.menubar.setStyleSheet("QMenuBar { background-color: white; color:black; font-weight:bold}")


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

        self.old_polar_coordinates = self.menubar.addMenu('Old Polar Coordinates')
        self.actionOldPolarCoordinates = QtWidgets.QAction("Show Old Polar ECG Plot", self)
        self.old_polar_coordinates.addAction(self.actionOldPolarCoordinates)
        self.actionOldPolarCoordinates.triggered.connect(lambda: self.show_old_ecg_plot())


        self.new_polar_coordinates = self.menubar.addMenu('New Polar Coordinates')
        self.actionNewPolarCoordinates = QtWidgets.QAction("Show New Polar ECG Plot", self)
        self.new_polar_coordinates.addAction(self.actionNewPolarCoordinates)
        self.actionNewPolarCoordinates.triggered.connect(lambda: self.show_new_ecg_plot())

        self.circularPlotting = self.menubar.addMenu('Circular Plotting')
        self.actionCircularPlotting = QtWidgets.QAction("Show Polar ECG Plot", self)
        self.circularPlotting.addAction(self.actionCircularPlotting)
        self.actionCircularPlotting.triggered.connect(lambda: self.show_circular_plotting())

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)


    def toggle_visibility(self, event):
            # Find the corresponding plot item
            for item in self.legend.items:
                for single_item in item:
                    if isinstance(single_item, pg.graphicsItems.LegendItem.ItemSample):
                        if single_item.mousePressEvent == event:
                            plot_item = item[1]
                            plot_item.setVisible(not plot_item.isVisible())
                            break

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.label.setText(_translate("MainWindow", "Graph 1 Signals"))
        self.speedUpGraph1.setText(_translate("MainWindow", "Speed (+)"))
        self.speedDownGraph1.setText(_translate("MainWindow", "Speed (-)"))
        self.changeColorGraph1.setText(_translate("MainWindow", "Change Color"))
        self.browseFileGraph1.setText(_translate("MainWindow", "Browse File"))

        self.label_2.setText(_translate("MainWindow", "Graph 2 Signals"))
        self.speedUpGraph2.setText(_translate("MainWindow", "Speed (+)"))
        self.speedDownGraph2.setText(_translate("MainWindow", "Speed (-)"))
        self.changeColorGraph2.setText(_translate("MainWindow", "Change Color"))
        self.browseFileGraph2.setText(_translate("MainWindow", "Browse File"))


    def fileSelected(self, item, GraphNum):
        # Get the selected file path from the clicked item
        if GraphNum == 1:
            self.graph_1_selected_file = item.text()
        else:
            self.graph_2_selected_file = item.text()



    def toggleLinkedSignals(self):
        if not self.linkedSignals:
            self.linkedSignals = True
            self.graph1.clear()
            self.graph2.clear()
            self.graph1.getViewBox().sigRangeChanged.connect(self.sync_pan)
            self.graph2.getViewBox().sigRangeChanged.connect(self.sync_pan)
        else:
            self.linkedSignals = False
            self.timer_linked_graphs.stop()
            self.graph1.clear()
            self.graph2.clear()
            self.graph1.getViewBox().sigRangeChanged.disconnect(self.sync_pan)
            self.graph2.getViewBox().sigRangeChanged.disconnect(self.sync_pan)

    
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
                        fileName = file_path.split("/")[-1]
                        # Extract directory path
                        self.directoryPath = "/".join(file_path.split("/")[:-1])
                        self.fileListWidgetGraph1.addItem(fileName)
                    
                    self.timer_graph_1.stop()
                    signalData = self.loadSignalData(file_path,1)
                    self.signalPlotting(self.graph1, signalData, 1)  # Plot the new data on graph 1

                else:
                    print(f"The Length of list = {len(self.graph_2_files)}")

                    if file_path not in self.graph_2_files: 
                        self.graph_2_files.append(file_path)
                        self.graph2_colors.append(self.get_random_color())  # Assign a random color for the signal
                        fileName = file_path.split("/")[-1]
                        # Extract directory path
                        self.directoryPath = "/".join(file_path.split("/")[:-1])
                        self.fileListWidgetGraph2.addItem(fileName)

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
            
                self.graph1.setLimits(xMin=0, xMax=len(signalData), yMin=min(signalData)-0.5, yMax=max(signalData)+0.5)
            else:
                self.graph2.setLimits(xMin=0, xMax=len(signalData), yMin=min(signalData)-0.5, yMax=max(signalData)+0.5)
            
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
            # Re-add legend for Graph 1
            if Graph == self.graph1:
                for i, signal in enumerate(self.graph_1_files):
                    Graph.plot(signalData[:self.time_index_linked_graphs + 1], 
                            pen=self.linked_graphs_color, 
                            name=f"{signal}")  # Add name parameter for legend
                    
            # Re-add legend for Graph 2 
            elif Graph == self.graph2:
                for i, signal in enumerate(self.graph_2_files):
                    Graph.plot(signalData[:self.time_index_linked_graphs + 1],
                            pen=self.linked_graphs_color,
                            name=f"{signal}")  # Add name parameter for legend

            if self.time_index_linked_graphs > self.windowSize:
                Graph.setXRange(self.time_index_linked_graphs - self.windowSize + 1, self.time_index_linked_graphs + 1)
            else:
                Graph.setXRange(0, self.windowSize)

            self.time_index_linked_graphs += 3
            if self.time_index_linked_graphs >= len(signalData):
                self.timer_linked_graphs.stop()
                self.timer_graph_1.stop()
                self.timer_graph_2.stop()

        else:
            if GraphNum == 1:
                Graph.clear()
                for i, file in enumerate(self.graph_1_files):
                    signal = self.loadSignalData(file, 1)
                    Graph.plot(signal[:self.time_index_graph_1 + 1], pen=self.graph1_colors[i], name=f"{file}")

                if self.time_index_graph_1 > self.windowSize:
                    Graph.setXRange(self.time_index_graph_1 - self.windowSize + 1, self.time_index_graph_1 + 1)
                else:
                    Graph.setXRange(0, self.windowSize)

                self.time_index_graph_1 += 3
                if self.time_index_graph_1 >= len(signalData):
                    self.timer_graph_1.stop()
            else:
                Graph.clear()
                for i, file in enumerate(self.graph_2_files):
                    signal = self.loadSignalData(file, 2)
                    Graph.plot(signal[:self.time_index_graph_2 + 1], pen=self.graph2_colors[i], name=f"{file}")

                if self.time_index_graph_2 > self.windowSize:
                    Graph.setXRange(self.time_index_graph_2 - self.windowSize + 1, self.time_index_graph_2 + 1)
                else:
                    Graph.setXRange(0, self.windowSize)

                self.time_index_graph_2 += 3
                if self.time_index_graph_2 >= len(signalData):
                    self.timer_graph_2.stop()
 


    def openColorChangeDialog(self, GraphNum):
        print("Enter Color Dialoge")
        # Check if any signals are loaded in either graph
        if len(self.graph_1_files) == 0 and len(self.graph_2_files) == 0:
            print("No signals loaded to change color.")
            return
        
        if self.linkedSignals:
            print("Let's choose color for linked signals")
            newColor = QColorDialog.getColor()
            if newColor.isValid():
                self.linked_graphs_color = newColor.name()
                self.graph1_colors = [newColor] * len(self.graph1_colors)
                self.graph2_colors = [newColor] * len(self.graph1_colors)
                print(f"New color: {self.linked_graphs_color}")

        else:
            if GraphNum == 1:
                #This return the Selected Signal and if the signal is selected or not
                signalIndex= 0
                for i, signal in enumerate(self.graph_1_files):
                    if signal == self.graph_1_selected_file:
                        signalIndex = i
                        break

                # get the index of the signal that the user choose
                if signalIndex < len(self.graph_1_files):
                    # Open a color picker dialog
                    newColor = QColorDialog.getColor()
                    if newColor.isValid():
                        self.updateSignalColor(1, signalIndex, newColor)

        
            else:
                signalIndex= 0
                for i, signal in enumerate(self.graph_2_files):
                    print(f"Graph Files: {self.graph_2_files}")
                    print(f"Selected Graph: {self.graph_2_selected_file} ")
                    if signal == self.graph_2_selected_file:
                        signalIndex = i
                        print("We got the file")
                        break

                # get the index of the signal that the user choose
                print(f"Index of the file: {signalIndex}")
                print(f"Length of Signals File : {len(self.graph_2_files)}")
                if signalIndex < len(self.graph_2_files):
                    print("Let's Select your color")
                    # Open a color picker dialog
                    newColor = QColorDialog.getColor()
                    if newColor.isValid():
                        self.updateSignalColor(2, signalIndex, newColor)


    
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



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = Ui_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())
