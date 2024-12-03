import cv2
import numpy as np
from scipy.interpolate import CubicSpline
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider
from PyQt5.QtGui import QIcon , QFont, QPixmap, QColor # Package to set an icon , fonts and images
from PyQt5.QtCore import Qt , QTimer  # used for alignments.
from PyQt5.QtWidgets import QLayout , QVBoxLayout , QHBoxLayout, QGridLayout ,QWidget, QFileDialog, QPushButton, QColorDialog, QInputDialog, QComboBox, QDialog, QDoubleSpinBox
import pyqtgraph as pg
import random
import pandas as pd
from scipy.signal import find_peaks
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem
from scipy import signal
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PIL import Image, ImageQt





def convert_data_to_image(imageData):
    try:
        # Convert the image data to a QImage
        height, width, channel = imageData.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(imageData.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        qImg = qImg.rgbSwapped()
        grayscale_qImg = qImg.convertToFormat(QtGui.QImage.Format_Grayscale8)

        return grayscale_qImg
    except Exception as e:
        print(e)



def loadImage(viewer):
    filename, _ = QFileDialog.getOpenFileName(viewer, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
    if filename:
        # Read image in grayscale
        imageData = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        if imageData is None:
            return None, None
            
        # Convert to QImage
        height, width = imageData.shape
        bytesPerLine = width
        qImage = QImage(imageData.data, width, height, bytesPerLine, QImage.Format_Grayscale8)
        
        return qImage, imageData
    return None, None

def imageFourierTransform(viewer, imageData):
    if imageData is not None:
        try:
            print("Computing Fourier transform...")
            # Convert to grayscale if needed
            if len(imageData.shape) > 2:
                imageData = cv2.cvtColor(imageData, cv2.COLOR_BGR2GRAY)
                
            # Apply 2D FFT
            f_transform = np.fft.fft2(imageData)
            f_transform_shifted = np.fft.fftshift(f_transform)
            
            # Store components
            viewer.ft_components = f_transform_shifted.copy()  # Store copy
            viewer.ft_magnitude = np.abs(f_transform_shifted)
            viewer.ft_phase = np.angle(f_transform_shifted)
            viewer.ft_real = np.real(f_transform_shifted)
            viewer.ft_imaginary = np.imag(f_transform_shifted)
            
            print("Fourier transform computed successfully")
            return True
            
        except Exception as e:
            print(f"Error in Fourier transform: {str(e)}")
            return False
    return False

def displayFrequencyComponent(viewer, component_type):
    if not hasattr(viewer, 'ft_components') or viewer.ft_components is None:
        return
        
    # Get the appropriate component
    if component_type == 'FT Magnitude':
        display_data = np.log(1 + np.abs(viewer.ft_magnitude))
    elif component_type == 'FT Phase':
        display_data = viewer.ft_phase
    elif component_type == 'FT Real':
        display_data = np.log(1 + np.abs(viewer.ft_real))
    elif component_type == 'FT Imaginary':
        display_data = np.log(1 + np.abs(viewer.ft_imaginary))
    
    # Normalize to 0-255 range
    display_data = ((display_data - display_data.min()) * 255 
                   / (display_data.max() - display_data.min()))
    display_data = display_data.astype(np.uint8)
    
    # Convert to QImage - Fix: Convert numpy array to bytes
    height, width = display_data.shape
    bytes_per_line = width
    
    # Create QImage from the numpy array's buffer
    qImage = QImage(display_data.tobytes(), 
                   width, 
                   height,
                   bytes_per_line,
                   QImage.Format_Grayscale8)
    
    # Display in the FT component label
    pixmap = QPixmap.fromImage(qImage)
    viewer.ftComponentLabel.setPixmap(pixmap.scaled(
        viewer.ftComponentLabel.size(),
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
    ))
    
def convert_from_pil_to_qimage(pilImage):
        img_data = pilImage.tobytes()
        qimage = QImage(img_data, pilImage.width, pilImage.height, pilImage.width * 3, QImage.Format_RGB888)
        return qimage
