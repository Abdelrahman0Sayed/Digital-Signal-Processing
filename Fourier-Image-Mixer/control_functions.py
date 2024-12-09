from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter
from PIL import Image, ImageQt
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt, QRect, QTimer,  QEvent
import numpy as np
from scipy.fft import fft2, fftshift

# Done by ModernWindow
def draw_rectangle(self, viewers, rect_size, region):
    if region == "Inner":
        for viewer in viewers:
            if viewer.imageData is not None:
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
                
                painter = QPainter(new_pixmap)
                painter.setPen(QPen(Qt.black, 3, Qt.SolidLine))
                # Draw the brush outside the rectangle
                painter.setBrush(QBrush(Qt.black, Qt.DiagCrossPattern))
                self.rectSize = int(rect_size)
                startPoint = int(150 - (rect_size / 2))
                painter.drawRect(QRect(startPoint, startPoint, rect_size, rect_size))
                painter.end()
                
                viewer.ftComponentLabel.setPixmap(new_pixmap)
    else:
        # Draw the brush inside the rectangle
        for viewer in viewers:
            if viewer.imageData is not None:
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
                
                painter = QPainter(new_pixmap)
                painter.setPen(QPen(Qt.black, 3, Qt.SolidLine))
                painter.setBrush(QBrush(Qt.black, Qt.DiagCrossPattern))
                painter.setBrush(QBrush(Qt.black, Qt.DiagCrossPattern))


                self.rectSize = int(rect_size)
                startPoint = int(150 - (rect_size / 2))
                painter.drawRect(QRect(startPoint, startPoint, rect_size, rect_size))
                painter.end()
                
                viewer.ftComponentLabel.setPixmap(new_pixmap)

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