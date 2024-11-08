from PyQt5.QtCore import Qt, QTimer  # used for alignments.
from PyQt5.QtWidgets import QMainWindow, QSlider, QLabel, QGroupBox, QVBoxLayout, QGridLayout, QSpinBox, QComboBox, QPushButton
from functions_graph import export_to_pdf_glued
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from scipy.interpolate import interp1d
from pyqtgraph import LinearRegionItem
import math
from numpy.polynomial import Polynomial
from PyQt5.QtGui import QImage, QPainter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import pyqtgraph as pg
import sys
import numpy as np
import tempfile
import os
import datetime


class Ui_GlueMenu(QMainWindow):
    def __init__(self, parent=None, signal_data1=None, signal_data2=None):
        super().__init__()
        self.setObjectName("GluMenu")
        self.setWindowTitle("Glue Menu")
        self.resize(1200, 800)  # Increase the window size

        # Pass the loaded signal data
        self.signal_data1 = signal_data1
        self.signal_data2 = signal_data2
        self.screenshots = []
        self.signal_data = []
        try:
            self.signal_data1 = self.signal_data1[:, 1]
            self.signal_data2 = self.signal_data2[:, 1]
        except:
            pass
        
        # Calculate the min and max of the signal data for constraints
        self.min_signal1 = np.min(self.signal_data1)
        self.max_signal1 = np.max(self.signal_data1)
        self.min_signal2 = np.min(self.signal_data2)
        self.max_signal2 = np.max(self.signal_data2)

        self.setupUi()
        

        # Set the range limits for the graphs based on the signal data
        self.set_graph_constraints()

        # Store initial offset values
        self.offset1 = 0
        self.offset2 = 0
        self.start1 = 0
        self.end1 = len(self.signal_data1) // 2
        self.start2 = 0
        self.end2 = len(self.signal_data2) // 2

        # Timer for live updating the glued signal
        self.timer_glued_signal = QTimer(self)
        self.time_index_glued_signal = 0  # For Cine Mode Scrolling
        self.update_interval = 200  # Initial update interval (ms)

        self.setupGraphInteraction()

    def setupUi(self):
        self.update_interval = 200  # Initial update interval (ms)
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)

        # Apply dark theme and modern styles
        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: Arial, sans-serif;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QPushButton {
                background-color: white;
                color: black;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #3E3E3E;
                height: 10px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                width: 20px;
                margin: -5px 0;
                border-radius: 10px;
            }
            QSlider::groove:vertical {
                border: 1px solid #bbb;
                background: #3E3E3E;
                width: 10px;
                border-radius: 4px;
            }
            QSlider::handle:vertical {
                background: #4CAF50;
                border: 1px solid #4CAF50;
                height: 20px;
                margin: 0 -5px;
                border-radius: 10px;
            }
            QComboBox {
                background-color: #3E3E3E;
                color: white;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 5px;
            }
            QLabel {
                color: #FFFFFF;
            }
        """)

        # Create a layout
        main_layout = QGridLayout(self.centralwidget)

        # Create a plot widget for the original signals
        # Graph Widgets
        self.graphWidget1 = pg.PlotWidget(self.centralwidget)
        self.graphWidget2 = pg.PlotWidget(self.centralwidget)
        self.graphWidget_glued = pg.PlotWidget(self.centralwidget)

        main_layout.addWidget(self.graphWidget1, 0, 0, 1, 2)
        main_layout.addWidget(self.graphWidget2, 1, 0, 1, 2)
        main_layout.addWidget(self.graphWidget_glued, 2, 0, 1, 2)

        # Legends and labels for clarity
        self.graphWidget1.addLegend()
        self.graphWidget1.setLabel('left', 'Amplitude')
        self.graphWidget1.setLabel('bottom', 'Time', 's')
        self.graphWidget1.plot(self.signal_data1, pen='b', name='Signal 1')

        self.graphWidget2.addLegend()
        self.graphWidget2.setLabel('left', 'Amplitude')
        self.graphWidget2.setLabel('bottom', 'Time', 's')
        self.graphWidget2.plot(self.signal_data2, pen='g', name='Signal 2')

        self.graphWidget_glued.addLegend()
        self.graphWidget_glued.setLabel('left', 'Amplitude')
        self.graphWidget_glued.setLabel('bottom', 'Time', 's')

        # Horizontal slider for glued signal
        self.glue_h_slider = QSlider(QtCore.Qt.Horizontal)
        self.glue_h_slider.setMinimum(0)
        self.glue_h_slider.setMaximum(1000)  # Placeholder; will update based on the signal length
        self.glue_h_slider.setValue(0)
        self.glue_h_slider.setTickInterval(1)
        main_layout.addWidget(self.glue_h_slider, 3, 0, 1, 2)
        self.glue_h_slider.valueChanged.connect(self.update_glued_signal_position)

        # Vertical slider for glued signal
        self.glue_v_slider = QSlider(QtCore.Qt.Vertical)
        self.glue_v_slider.setMinimum(0)
        self.glue_v_slider.setMaximum(1000)  # Placeholder; will update based on the signal length
        self.glue_v_slider.setValue(0)
        self.glue_v_slider.setTickInterval(1)
        main_layout.addWidget(self.glue_v_slider, 2, 3, 1, 1)
        self.glue_v_slider.valueChanged.connect(self.update_glued_signal_position)

        # Export PDF button
        self.exportGluedSignalButton = QtWidgets.QPushButton("Export Glued Signal", self.centralwidget)
        main_layout.addWidget(self.exportGluedSignalButton, 6, 0, 1, 2)
        self.exportGluedSignalButton.clicked.connect(lambda: self.export_pdf())

        # Export PDF button
        self.exportGluedSignalButton = QtWidgets.QPushButton("Take Screenshot", self.centralwidget)
        main_layout.addWidget(self.exportGluedSignalButton, 5, 0, 1, 2)
        self.exportGluedSignalButton.clicked.connect(lambda: self.take_screenshot())

        # Group box for Glue Parameters
        group_box_glue = QGroupBox("Interpolation Order")
        layout_glue = QGridLayout()
        group_box_glue.setLayout(layout_glue)

        # Interpolation Order
        self.interp_label = QLabel("Interpolation Order:")
        layout_glue.addWidget(self.interp_label, 0, 0)
        self.interp_combobox = QComboBox()
        self.interp_combobox.addItems(["nearest", "linear", "cubic", "polynomial"])
        layout_glue.addWidget(self.interp_combobox, 0, 1)
        self.interp_combobox.currentIndexChanged.connect(self.glue_signals)

        main_layout.addWidget(group_box_glue, 4, 0, 1, 2)

    def glue_signals(self):
        view_range = self.graphWidget_glued.viewRange()

        # Define the segments of signal1 and signal2
        segment1 = self.signal_data1[self.start1:self.end1]
        segment2 = self.signal_data2[self.start2:self.end2]

        # Find the maximum length for the combined signal
        max_length = max(self.end1, self.end2)
        combined_signal1 = np.full(max_length, np.nan)
        combined_signal2 = np.full(max_length, np.nan)

        combined_signal1[self.start1:self.end1] = segment1
        combined_signal2[self.start2:self.end2] = segment2

        # Find overlapping range and sum the overlapping sections
        overlap_start = max(self.start1, self.start2)
        overlap_end = min(self.end1, self.end2)
        glued_signal = np.nan_to_num(combined_signal1) + np.nan_to_num(combined_signal2)

        # Handle gap interpolation for non-overlapping segments
        signal1_x = np.arange(self.start1, self.end1)
        signal1_y = segment1
        signal2_x = np.arange(self.start2, self.end2)
        signal2_y = segment2

        gap1 = self.start2 - self.end1
        gap2 = self.start1 - self.end2

        if gap1 > 0:
            gap_x = np.linspace(signal1_x[-1], signal2_x[0], num=math.ceil(abs(gap1) * 100))
            combined_x = np.concatenate([signal1_x, signal2_x])
            combined_y = np.concatenate([signal1_y, signal2_y])
        else:
            gap_x = np.linspace(signal2_x[-1], signal1_x[0], num=math.ceil(abs(gap2) * 100))
            combined_x = np.concatenate([signal2_x, signal1_x])
            combined_y = np.concatenate([signal2_y, signal1_y])

        # Interpolate gap segment
        interp_order = self.interp_combobox.currentText()
        if interp_order == 'linear':
            f = interp1d(combined_x, combined_y, kind='linear', fill_value="extrapolate")
        elif interp_order == 'cubic':
            f = interp1d(combined_x, combined_y, kind='cubic', fill_value="extrapolate")
        elif interp_order == 'nearest':
            f = interp1d(combined_x, combined_y, kind='nearest', fill_value="extrapolate")
        elif interp_order == 'polynomial':
            degree = min(len(combined_x) - 1, 3)
            coefficients = Polynomial.fit(combined_x, combined_y, degree)
            f = lambda x: coefficients(x)

        gap_y = f(gap_x)

        # Plot only in their respective segments
        # Plot the gap interpolation segment only
        self.graphWidget_glued.clear()

        # if there is a gap, plot the gap segment
        if gap1 > 0 or gap2 > 0:

            self.graphWidget_glued.plot(gap_x, gap_y, pen=pg.mkPen('red', width=2), name='Interpolated Gap Segment')

        # Plot the summated overlap signal only in the overlapping region
        overlap_x = np.arange(overlap_start, overlap_end)
        glued_overlap_signal = glued_signal[overlap_start:overlap_end]

        self.graphWidget_glued.plot(overlap_x, glued_overlap_signal, pen=pg.mkPen('purple', width=2, style=QtCore.Qt.DashLine), name='Summed Overlap')

        # Plot the original signals for reference
        self.graphWidget_glued.plot(signal1_x, signal1_y, pen=pg.mkPen('blue', width=1), name='Signal 1')
        self.graphWidget_glued.plot(signal2_x, signal2_y, pen=pg.mkPen('green', width=1), name='Signal 2')

        # Set the limits and restore view range
        y_min_glued = np.nanmin(glued_signal)
        y_max_glued = np.nanmax(glued_signal)
        x_max_glued = len(glued_signal) - 1

        self.graphWidget_glued.setLimits(
            xMin=0, xMax=x_max_glued,
            yMin=y_min_glued - 5, yMax=y_max_glued + 5
        )

        self.graphWidget_glued.setXRange(view_range[0][0], view_range[0][1], padding=0)
        self.graphWidget_glued.setYRange(view_range[1][0], view_range[1][1], padding=0)

        self.glued_signal = glued_signal


        #self.update_glued_signal_position()




    def setupGraphInteraction(self):
        # Adding LinearRegionItems for selecting segments
        self.region1 = LinearRegionItem([0, len(self.signal_data1)//2], movable=True)
        self.region2 = LinearRegionItem([0, len(self.signal_data2)//2], movable=True)

        self.graphWidget1.addItem(self.region1)
        self.graphWidget2.addItem(self.region2)

        # Connecting region changes to update signals and sliders
        self.region1.sigRegionChanged.connect(self.update_from_region1)
        self.region2.sigRegionChanged.connect(self.update_from_region2)

        # Initialize glued graph as empty
        self.glue_signals()
        #self.update_glued_signal_position()

    def update_from_region1(self):
        region = self.region1.getRegion()
        self.start1, self.end1 = int(region[0]), int(region[1])
        
        # Ensure the start and end are within the signal boundaries
        self.start1 = max(0, self.start1)
        self.end1 = min(len(self.signal_data1), self.end1)
        
        self.glue_signals()
        #self.update_glued_signal_position()

    def update_from_region2(self):
        region = self.region2.getRegion()
        self.start2, self.end2 = int(region[0]), int(region[1])
        
        # Ensure the start and end are within the signal boundaries
        self.start2 = max(0, self.start2)
        self.end2 = min(len(self.signal_data2), self.end2)
        
        self.glue_signals()
        #self.update_glued_signal_position()
    
    def update_graphs(self):
        # Update Signal 1 graph with the selected segment
        self.graphWidget1.clear()
        self.graphWidget1.plot(self.signal_data1, pen=pg.mkPen('r', width=2))
        self.graphWidget1.plot(np.arange(self.start1, self.end1), self.signal_data1[self.start1:self.end1], pen=pg.mkPen('b', width=3))

        # Update Signal 2 graph with the selected segment
        self.graphWidget2.clear()
        self.graphWidget2.plot(self.signal_data2, pen=pg.mkPen('r', width=2))
        self.graphWidget2.plot(np.arange(self.start2, self.end2), self.signal_data2[self.start2:self.end2], pen=pg.mkPen('b', width=3))

        # Regenerate glued signal with the updated segments
        self.glue_signals()

    def update_glued_signal_position(self):
        """ Update the position of the glued signal based on the slider values. """
        h_value = self.glue_h_slider.value()  # Horizontal slider value
        v_value = self.glue_v_slider.value()  # Vertical slider value

        # Get the current x and y ranges
        x_range = self.graphWidget_glued.viewRange()[0]  # Current x-axis range (min, max)
        y_range = self.graphWidget_glued.viewRange()[1]  # Current y-axis range (min, max)

        # Adjust the x-axis range based on the horizontal slider value
        # Keep the width of the range the same, just shift it horizontally
        x_width = x_range[1] - x_range[0]
        new_x_min = h_value
        new_x_max = h_value + x_width

        # Adjust the y-axis range based on the vertical slider value
        # Keep the height of the range the same, just shift it vertically
        y_height = y_range[1] - y_range[0]
        new_y_min = v_value
        new_y_max = v_value + y_height

        # Update the glued signal graph's view range
        self.graphWidget_glued.setRange(xRange=(new_x_min, new_x_max), yRange=(new_y_min, new_y_max), padding=0)

    def set_graph_constraints(self):
        """Set X and Y axis constraints for the graphs based on signal data."""
        
        # X-axis range is the length of the signals
        x_range_signal1 = (0, len(self.signal_data1) - 1)
        x_range_signal2 = (0, len(self.signal_data2) - 1)

        # Y-axis range is based on the minimum and maximum values of the signals
        y_range_signal1 = (self.min_signal1, self.max_signal1)
        y_range_signal2 = (self.min_signal2, self.max_signal2)

        # Setting constraints for graphWidget1 (Signal 1)
        self.graphWidget1.setXRange(*x_range_signal1, padding=0)
        self.graphWidget1.setYRange(*y_range_signal1, padding=0)
        self.graphWidget1.setLimits(
            xMin=x_range_signal1[0], xMax=x_range_signal1[1],
            yMin=y_range_signal1[0], yMax=y_range_signal1[1]
        )

        # Setting constraints for graphWidget2 (Signal 2)
        self.graphWidget2.setXRange(*x_range_signal2, padding=0)
        self.graphWidget2.setYRange(*y_range_signal2, padding=0)
        self.graphWidget2.setLimits(
            xMin=x_range_signal2[0], xMax=x_range_signal2[1],
            yMin=y_range_signal2[0], yMax=y_range_signal2[1]
        )

        # Calculate the glued signal constraints
        max_length = max(len(self.signal_data1), len(self.signal_data2)) 
        glued_signal = np.full(max_length, np.nan)

        # Insert the segments into the glued signal array
        glued_signal[:len(self.signal_data1)] = self.signal_data1
        glued_signal[:len(self.signal_data2)] = np.nan_to_num(glued_signal[:len(self.signal_data2)]) + self.signal_data2

        # Calculate the y-axis range for the glued signal
        y_min_glued = np.nanmin(glued_signal) - 1
        y_max_glued = np.nanmax(glued_signal) + 1
        x_max_glued = max(len(self.signal_data1), len(self.signal_data2)) - 1

        # Setting constraints for glued signal graph
        self.graphWidget_glued.setXRange(0, x_max_glued, padding=0)
        self.graphWidget_glued.setYRange(y_min_glued, y_max_glued, padding=0)
        self.graphWidget_glued.setLimits(
            xMin=0, xMax=x_max_glued,
            yMin=y_min_glued, yMax=y_max_glued
        )
        
    def take_screenshot(self): 
        """Takes a screenshot of the glued signal graph, saves it to a file, and appends it to the screenshots list along with the glued signal data."""

        # Create a QImage with the same size as the glued signal graph widget
        screenshot = QImage(self.graphWidget_glued.size(), QImage.Format_RGB32)

        # Render the glued signal graph widget onto the QImage
        painter = QPainter(screenshot)
        self.graphWidget_glued.render(painter)
        painter.end()

        # Define the file name and path
        screenshot_path = os.path.join(os.getcwd(), f"screenshot_{len(self.screenshots) + 1}.png")
        
        # Save the screenshot to a file
        screenshot.save(screenshot_path, "PNG")

        # Append the screenshot and glued signal data to lists
        self.screenshots.append(screenshot)
        self.signal_data.append(self.glued_signal)  # Store the glued signal data

        print(f"Screenshot saved as {screenshot_path}. Total screenshots: {len(self.screenshots)}")

        # make the alert for the screenshot
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Screenshot saved successfully.")

        msg.setWindowTitle("Screenshot")
        msg.exec_()


    def export_pdf(self):
        """Exports all stored screenshots and stats tables to a PDF with a timestamped filename."""
        if not self.screenshots:
            print("No screenshots to export.")
            return

        # Create a timestamped PDF filename
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        pdf_path = f"Signal_Report_{timestamp}.pdf"

        # Generate temporary file paths for screenshots
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_files = []
            for i, screenshot in enumerate(self.screenshots):
                temp_path = os.path.join(temp_dir, f"screenshot_{i + 1}.png")  # Use i+1 for naming
                screenshot.save(temp_path)
                temp_files.append(temp_path)

            # Create the PDF and add screenshots with statistics tables
            c = canvas.Canvas(pdf_path, pagesize=A4)
            for i, temp_file in enumerate(temp_files):
                # Load the screenshot and determine its original dimensions
                img = QImage(temp_file)
                width, height = img.width(), img.height()

                # Define desired maximum width and height to scale the image
                max_img_width = A4[0] * 0.68  # Increase to 80% of the page width
                max_img_height = A4[1] * 1.6  # Set height to 1/3 of the page height

                # Calculate the scaling factor to fit the image within these dimensions
                scale_factor = min(max_img_width / width, max_img_height / height)

                # Calculate positions to center the image horizontally and position it near the top
                centered_x_position = (A4[0] - (width * scale_factor)) / 2
                image_y_position = A4[1] - (height * scale_factor) - 80  # Position with 30 points from the top

                # Draw the centered and scaled image on the PDF
                c.drawImage(temp_file, centered_x_position, image_y_position,
                            width=width * scale_factor, height=height * scale_factor)

                # Generate and add the statistics table below the image
                stats_table = self.create_stats_table(self.signal_data[i], f"Graph {i + 1}")
                table_y_position = image_y_position - (0.6 * (height * scale_factor)) - 200 # Adjust table position under image

                # Set the table width to match the scaled width of the image
                table_width = width * scale_factor  # Table width matches scaled image width

                # Draw table flowables
                for flowable in stats_table:
                    flowable.wrapOn(c, table_width, A4[1] / 2)  # Set table width to match image width
                    flowable.drawOn(c, centered_x_position, table_y_position)  # Center the table under the image

                c.showPage()

            c.save()
            print(f"PDF exported as '{pdf_path}'.")
            
            # make the alert for the pdf
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("PDF exported successfully.")

            msg.setWindowTitle("PDF Export")
            msg.exec_()
            

    def create_stats_table(self, signal_data, graph_label):
        """Create a table for signal statistics such as mean, std, min, max, and duration."""
        if signal_data is None:
            return [Paragraph(f"No data available for {graph_label}", getSampleStyleSheet()['Normal'])]

        # Calculate statistics
        mean_val = np.mean(signal_data)
        std_val = np.std(signal_data)
        min_val = np.min(signal_data)
        max_val = np.max(signal_data)
        duration = len(signal_data)  # Assuming each point represents a time unit

        # Create a table with stats
        data = [
            ["Statistic", "Value"],
            ["Mean", f"{mean_val:.2f}"],
            ["Standard Deviation", f"{std_val:.2f}"],
            ["Min Value", f"{min_val:.2f}"],
            ["Max Value", f"{max_val:.2f}"],
            ["Duration", f"{duration} "]
        ]

        # Define desired table width and set column widths
        desired_table_width = 400  # Set this to your desired width
        col_widths = [desired_table_width * 0.5, desired_table_width * 0.5]  # Example: equally divide width between columns

        # Format the table
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))

        return [table, Spacer(1, 12)]
