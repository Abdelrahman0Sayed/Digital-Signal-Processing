from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter
from PIL import Image, ImageQt
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QRect, QTimer,  QEvent
import numpy as np
from scipy.fft import fft2, fftshift

# Done by ModernWindow
def draw_rectangle(self, viewers, rect_size):
    for viewer in viewers:
        if viewer.imageData is not None:
            print("There is an image")
            pixmapType = viewer.component_selector.currentText()
            print(f"Current Type is {pixmapType}")
            print(viewer.magnitudeImage)
            if pixmapType == "FT Magnitude":
                original_pixmap = viewer.magnitudeImage 

            elif pixmapType == "FT Phase":
                original_pixmap = viewer.imageWidget.phaseImage

            elif pixmapType == "FT Real":
                original_pixmap = viewer.imageWidget.realImage

            elif pixmapType == "FT Imaginary":
                original_pixmap = viewer.imageWidget.imaginaryImage

            
            if original_pixmap is None:
                print("There is no image to draw a rectangle on")
                continue 
            print("We got an image, Lets draw a Rectangle")
            new_pixmap = original_pixmap.copy() 
            
            painter = QPainter(new_pixmap)
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            self.rect_size = int(3 * rect_size)
            startPoint = int(150 - (rect_size / 2))
            painter.drawRect(QRect(startPoint, startPoint, rect_size, rect_size))
            print("We Drawed a Rectangle")
            painter.end()
            
            viewer.ftComponentLabel.setPixmap(new_pixmap)
            print("It's added to the viewer")


def clear_rectangle(self, viewers):
    for viewer in viewers:
        pixmapType = viewer.component_selector.currentText()
        if pixmapType == "FT Magnitude":
            original_pixmap = viewer.magnitudeImage 

        elif pixmapType == "FT Phase":
            original_pixmap = viewer.imageWidget.phaseImage

        elif pixmapType == "FT Real":
            original_pixmap = viewer.imageWidget.realImage

        elif pixmapType == "FT Imaginary":
            original_pixmap = viewer.imageWidget.imaginaryImage

        if original_pixmap is None:
            continue 

        new_pixmap = original_pixmap.copy() 
        self.region_size.setValue(0)
        viewer.ftComponentLabel.setPixmap(new_pixmap)