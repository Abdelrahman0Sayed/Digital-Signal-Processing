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


def loadImage(self):
    try:
        filePath, _ = QFileDialog.getOpenFileName(None, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if filePath:
            # Load the image
            self.imageData = cv2.imread(filePath)
            
            # Convert to grayscale
            grayScaledImage = cv2.cvtColor(self.imageData, cv2.COLOR_BGR2GRAY)
            
            # height, width = grayScaledImage.shape[:2]
            # image_size = (width, height)
            
            # print(f"{image_size}")
            
            # if self.minimum_size == (0, 0):
            #     # Set the minimum size for the first image
            #     print("This is the First Image, setting new Minimum Size")
            #     self.minimum_size = image_size
            #     print(f"Minimum Size set to: {self.minimum_size}")

            # # Check and update minimum size
            # if image_size < self.minimum_size and image_size != 0:
            #     print("Updating Minimum Size based on the new image")
            #     self.minimum_size = image_size

            unify_images(self, self.viewers)
            self.imageData = cv2.resize(self.imageData, (300,300))
        
            return grayScaledImage, self.imageData
        return 
    except Exception as e:
        print(f"Error: {e}")


def unify_images(self, viewers):
    print("Unifying Images")
    for viewer in viewers:
        if viewer.imageData is not None:
            # Resize the image using cv2.resize
            target_size = (self.minimum_size, self.minimum_size)  # Assuming square resizing
            viewer.imageData = cv2.resize(viewer.imageData, target_size)
            print(f"Image resized to: {viewer.imageData.shape}")



    
def convert_data_to_image(imageData):
    try:
        # Convert the image data to a QImage
        height, width, channel = imageData.shape
        bytesPerLine = 3 * width
        qImg = QtGui.QImage(imageData.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        if qImg is None:
            print("Error in converting image data to QImage")
    
        qImg = qImg.rgbSwapped()
        grayscale_qImg = qImg.convertToFormat(QtGui.QImage.Format_Grayscale8)
        
        return grayscale_qImg
    except Exception as e:
        print(e)


def imageFourierTransform(self, imageData):
    fftComponents = np.fft.fft2(imageData)
    fftComponentsShifted = np.fft.fftshift(fftComponents)
    self.fftComponents= fftComponentsShifted
    # Get Magnitude and Phase
    self.ftMagnitudes = np.abs(fftComponentsShifted)
    self.ftPhase = np.angle(fftComponentsShifted)
    # Get the Real and Imaginary parts
    self.ftReal = np.real(fftComponentsShifted)
    self.ftImaginary = np.imag(fftComponentsShifted)
    


def displayFrequencyComponent(self, PlottedComponent):
    
    if PlottedComponent == "FT Magnitude":
        print("Plotting Magnitude")
        # Take the Magnitude as log scale
        ftLog = 15 * np.log(self.ftMagnitudes + 1e-10).astype(np.uint8)
        ftNormalized = ftLog / ftLog.max() * 255
        pil_image = Image.fromarray(np.uint8(ftNormalized)) 
        qimage = convert_from_pil_to_qimage(pil_image)
        qimage = qimage.convertToFormat(QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        label_height = self.ftComponentLabel.height()
        label_width = self.ftComponentLabel.width()
        
        pixmap = pixmap.scaled(label_height, label_width, Qt.KeepAspectRatio)
        self.ftComponentLabel.setPixmap(pixmap)
        
    elif PlottedComponent == "FT Phase":
        print("Plotting Phase")
        # Ensure phase is within -pi to pi range and Ajdust for visualization (between 0 - 255)
        f_wrapped = np.angle(np.exp(1j * self.ftPhase))  
        f_normalized = (f_wrapped + np.pi) / (2 * np.pi) * 255
        
        pil_image = Image.fromarray(np.uint8(f_normalized)) 
        qimage = convert_from_pil_to_qimage(pil_image)
        qimage = qimage.convertToFormat(QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        label_height = self.ftComponentLabel.height()
        label_width = self.ftComponentLabel.width()
        
        pixmap = pixmap.scaled(label_height, label_width, Qt.KeepAspectRatio)
        self.ftComponentLabel.setPixmap(pixmap)
    
    elif PlottedComponent == "FT Real":
        print("Plotting Real")
        
        # Normalization and Adjustment for visualization
        ftNormalized = np.abs(self.ftReal)
        
        
        pil_image = Image.fromarray(np.uint8(ftNormalized)) 
        qimage = convert_from_pil_to_qimage(pil_image)
        qimage = qimage.convertToFormat(QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        label_height = self.ftComponentLabel.height()
        label_width = self.ftComponentLabel.width()
        
        pixmap = pixmap.scaled(label_height, label_width, Qt.KeepAspectRatio)
        self.ftComponentLabel.setPixmap(pixmap)
    elif PlottedComponent == "FT Imaginary":
        print("FT Imaginary")
        
        ftNormalized = np.abs(self.ftImaginary)
        
        
        pil_image = Image.fromarray(np.uint8(ftNormalized)) 
        qimage = convert_from_pil_to_qimage(pil_image)
        qimage = qimage.convertToFormat(QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        label_height = self.ftComponentLabel.height()
        label_width = self.ftComponentLabel.width()
        
        pixmap = pixmap.scaled(label_height, label_width, Qt.KeepAspectRatio)
        self.ftComponentLabel.setPixmap(pixmap)
    



def convert_from_pil_to_qimage(pilImage):
        img_data = pilImage.tobytes()
        qimage = QImage(img_data, pilImage.width, pilImage.height, pilImage.width * 3, QImage.Format_RGB888)
        return qimage


def convet_mixed_to_qImage(imageData):
    try:
        # Convert the image data to a QImage
        height, width, channel = imageData.shape
        bytesPerLine = 3 * width
        
        # Convert memoryview to bytes
        image_bytes = imageData.tobytes()
        
        # Create the QImage
        qImg = QtGui.QImage(image_bytes, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
        
        if qImg.isNull():  # Check if the QImage is valid
            print("Error in converting image data to QImage")
        else:
            # Convert to grayscale if needed
            qImg = qImg.rgbSwapped()
            grayscale_qImg = qImg.convertToFormat(QtGui.QImage.Format_Grayscale8)
            return grayscale_qImg
        
    except Exception as e:
        print(e)