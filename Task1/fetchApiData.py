import sys
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QHBoxLayout, QColorDialog
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
import pyqtgraph as pg
import requests
import time
import threading


class ApiFetcher(QObject):
    data_fetched = pyqtSignal(float)

    def fetch_iss_position(self):
        """Fetch the ISS position from the API."""
        url = "http://api.open-notify.org/iss-now.json"

        try:
            response = requests.get(url)
            data = response.json()

            if data['message'] == "success":
                latitude = float(data['iss_position']['latitude'])  # Convert to float
                self.data_fetched.emit(latitude)  # Emit the fetched data
            else:
                print("Error in fetching ISS data.")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
        except ValueError:
            print("Error: Response is not valid JSON.")


class FetchApi_MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setObjectName("Link Window")
        self.setWindowTitle("Real-Time Data Fetching")
        self.resize(1300, 600)
        self.setupUiElements()
        self.setStyleSheet("Background-color:#F0F0F0;")

        self.windowSize=50

        # Initialize data variables
        self.latitudeData = []
        self.timeData = []
        self.startTime = time.time()  # Record the start time

        # Set up the timer for real-time data fetching
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Fetch data every second

        self.api_fetcher = ApiFetcher()
        self.api_fetcher.data_fetched.connect(self.update_plot)

        self.graphColor = "#E8E8E8"

        # Plot initialization
        self.plotLine = self.graph.plot([], [], pen=f'{self.graphColor}')

        # Automatically start fetching data on initialization
        self.start_fetching_data()

        # Set initial Y-range around 5 with compact range for better visibility
        self.graph.setYRange(0, 10)  # Adjust as needed

    def setupUiElements(self):
        # Central Widget
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        # # Start Button (optional, can be removed if not needed)
        # self.startButton = QPushButton("Start", self.centralwidget)
        # self.startButton.setGeometry(QtCore.QRect(350, 480, 131, 51))
        # self.startButton.setStyleSheet("font-weight:bold;font-size:16px;background-color:white")
        # self.startButton.setObjectName("startButton")
        # self.startButton.clicked.connect(lambda: self.startDrawing())

        # # Stop Button
        # self.stopButton = QPushButton("Pause", self.centralwidget)
        # self.stopButton.setGeometry(QtCore.QRect(500, 480, 131, 51))
        # self.stopButton.setStyleSheet("font-weight:bold;font-size:16px;background-color:white")
        # self.stopButton.setObjectName("stopButton")
        # self.stopButton.clicked.connect(lambda: self.stopDrawing())

        # # Change Color Button
        # self.changeGraphColor = QPushButton("Change Color", self.centralwidget)
        # self.changeGraphColor.setGeometry(QtCore.QRect(650, 480, 131, 51))
        # self.changeGraphColor.setStyleSheet("font-weight:bold;font-size:16px;background-color:white")
        # self.changeGraphColor.setObjectName("changeColor")
        # self.changeGraphColor.clicked.connect(lambda: self.changeColor())

        # Graph Widget
        self.graphWidget = QWidget(self.centralwidget)
        self.graphWidget.setGeometry(QtCore.QRect(0, 0, 1300, 600))
        self.graphWidget.setObjectName("graph_widget")

        self.graph = pg.plot(title="Real Time Data")
        self.graphLayout = QHBoxLayout(self.graphWidget)
        self.graphLayout.addWidget(self.graph)

        self.setCentralWidget(self.centralwidget)

        QtCore.QMetaObject.connectSlotsByName(self)

    def changeColor(self):
        color = QColorDialog.getColor()
        self.graphColor = color.name()

    def start_fetching_data(self):
        """Start fetching data from the API at intervals."""
        self.timer.timeout.connect(self.fetch_data)
        self.timer.start()  # Start the timer

    def fetch_data(self):
        """Fetch data in a separate thread to avoid blocking."""
        thread = threading.Thread(target=self.api_fetcher.fetch_iss_position)
        thread.start()

    def startDrawing(self):
        if not self.timer.isActive():
            self.timer.start()
    
    def stopDrawing(self):
        if self.timer.isActive():
            self.timer.stop()

    def update_plot(self, latitude):
        elapsed_time = time.time() - self.startTime # عدى قد ايه من ساعة ما بدأنا ال fetching
        # عشان لما اوقف و ارجع تاني لازم اجيب الداتا اللي اللحظة الحالية
        # دي بتساعدني عشان لما اوقف و ارجع اشغل اجيب القيمة الحالية اللي المفروض Real Time


        # Update data lists
        self.latitudeData.append(latitude)
        self.timeData.append(elapsed_time)

        # Set boundary conditions for the Y-axis (latitude)
        minLatitude = -90  
        maxLatitude = 90  

        # Ensure latitude stays within these bounds
        # عشان ال latitude مبخرجش برا الجراف
        latitude = max(minLatitude, min(latitude, maxLatitude))

        # Plotting the new data from the API.
        self.graph.plot(self.timeData, self.latitudeData , pen='g')
        # Set the X-range to start from 5 seconds and slide normally with time
        # Because iam start fetching after 5 seconds.
        # This Condition always true 
        if elapsed_time > 5:
            self.graph.setXRange(elapsed_time - 5, elapsed_time)
        else:
            self.graph.setXRange(0, elapsed_time)

        if latitude:
            # Ensure the Y-axis remains within the boundaries
            y_min = max(minLatitude, latitude - 0.5)
            y_max = min(maxLatitude, latitude + 0.5)
            self.graph.setYRange(y_min, y_max)




def main():
    app = QApplication(sys.argv)
    MainWindow = FetchApi_MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
