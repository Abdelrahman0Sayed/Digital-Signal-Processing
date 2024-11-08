from scipy.interpolate import CubicSpline
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QListWidget, QHBoxLayout, QFileDialog, QPushButton , QComboBox, QDialog, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon, QFont, QPixmap, QColor, QDoubleValidator
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import pyqtSignal
import csv
import os
from datetime import datetime
from collections import deque
from dataclasses import dataclass
from typing import List, Any
import json

@dataclass
class Command:
    action: str  # 'add', 'delete', 'edit'
    signals: List[Any]
    properties: List[Any]
    indices: List[int]
    signal_names: List[str]  # Add this field

def generate_signal(self, signal_type, amplitude, frequency, phase_shift, duration=1, sample_rate=7000):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    phase_shift_rad = np.deg2rad(phase_shift)
    if signal_type == "Sin":
        return amplitude * np.sin(2 * np.pi * frequency * t + phase_shift_rad)
    elif signal_type == "Cos":
        return amplitude * np.cos(2 * np.pi * frequency * t + phase_shift_rad)

def generate_default_name(self, signal_type, frequency, amplitude):
    return f"{signal_type}_{frequency}Hz_{amplitude}A"

def add_signal(self, add_command_bool= False):
    signal_type = self.comboBox.currentText()
    amplitude = float(self.lineEdit.text())
    frequency = float(self.lineEdit_2.text())
    phase_shift = float(self.lineEdit_4.text())
    signal_name = self.lineEdit_3.text().strip()

    if frequency > 50:
        QtWidgets.QMessageBox.warning(self, "Invalid Input", "Frequency cannot exceed 50.")
        return

    # Generate default name if empty
    if not signal_name or 'untitled' in signal_name:
        signal_name = generate_default_name(self,signal_type, frequency, amplitude)
        self.lineEdit_3.setText(signal_name)

    if hasattr(self, 'selected_example_signal') and self.selected_example_signal is not None:
        signal = self.selected_example_signal
        signal_name = self.selected_example_name
        # Clear the example signal after use
        del self.selected_example_signal
        del self.selected_example_name
    else : 
        signal = generate_signal(self,signal_type, amplitude, frequency, phase_shift)
    # Store signal info for command
    signal_props = {
        'type': signal_type,
        'amplitude': amplitude,
        'frequency': frequency,
        'phase_shift': phase_shift,
        'name': signal_name
    }

    # Create command for undo/redo
    command = Command(
        action='add',
        signals=[signal],
        properties=[signal_props],
        indices=[len(self.signals)],  # Index where signal will be added
        signal_names=[signal_name]
    )
    if add_command_bool:
        add_command(self,command)
    


    # Add signal
    self.signals.append(signal)
    self.signal_properties.append(signal_props)
    self.listWidget.addItem(signal_name)

    if not add_command_bool:
        update_plot(self, update_on_sampling=True)
    
    # Clear signal name
    self.lineEdit_3.setText("untitled")

    self.is_previewing = False
    self.preview_signal = None

    

def edit_signal(self, update_on_sampling=False):
    if self.selected_signal_index >= 0:
        signal_type = self.comboBox.currentText()
        amplitude = float(self.lineEdit.text())
        frequency = float(self.lineEdit_2.text())
        phase_shift = float(self.lineEdit_4.text())
        signal_name = self.lineEdit_3.text().strip()

        # Generate default name if empty
        if not signal_name or 'untitled' in signal_name:
            signal_name = self.generate_default_name(signal_type, frequency, amplitude)
            self.lineEdit_3.setText(signal_name)

        if hasattr(self, 'selected_example_signal') and self.selected_example_signal is not None:
            self.signals[self.selected_signal_index]  = self.selected_example_signal
            signal_name = self.selected_example_name
            # Clear the example signal after use
            del self.selected_example_signal
            del self.selected_example_name
            
        else : 
            self.signals[self.selected_signal_index] = generate_signal(self,signal_type, amplitude, frequency, phase_shift)

        self.signal_properties[self.selected_signal_index] = {
            'type': signal_type,
            'amplitude': amplitude,
            'frequency': frequency,
            'phase_shift': phase_shift,
            'name': signal_name
        }
        self.listWidget.item(self.selected_signal_index).setText(signal_name)
        self.addComponent.setText("Add Component")
        self.selected_signal_index = -1
        update_plot(self, update_on_sampling)

def add_command(self, command: Command):
    self.undo_stack.append(command)
    self.redo_stack.clear()  # Clear redo stack when new action is performed
    update_undo_redo_buttons(self)

def undo(self):
    if not self.undo_stack:
        return
        
    command = self.undo_stack.pop()
    self.redo_stack.append(command)
    
    if command.action == 'add':
        # Remove added signals
        for index in reversed(command.indices):
            self.listWidget.takeItem(index)
            del self.signals[index]
            del self.signal_properties[index]
    elif command.action == 'delete':
        # Restore deleted signals
        for i, (signal, props, name) in enumerate(zip(command.signals, command.properties, command.signal_names)):
            self.signals.insert(command.indices[i], signal)
            self.signal_properties.insert(command.indices[i], props)
            self.listWidget.insertItem(command.indices[i], name)  # Use stored name
    
    update_plot(self)
    update_undo_redo_buttons(self)

    if not self.signals:
        self.selected_signal_index = -1
        self.addComponent.setText("Add Component")

def redo(self):
    if not self.redo_stack:
        return
        
    command = self.redo_stack.pop()
    self.undo_stack.append(command)
    
    if command.action == 'add':
        # Restore added signals
        for i, (signal, props, name) in enumerate(zip(command.signals, command.properties, command.signal_names)):
            self.signals.insert(command.indices[i], signal)
            self.signal_properties.insert(command.indices[i], props)
            self.listWidget.insertItem(command.indices[i], name)  # Use stored name
    elif command.action == 'delete':
        # Re-delete signals
        for index in reversed(command.indices):
            self.listWidget.takeItem(index)
            del self.signals[index]
            del self.signal_properties[index]
    
    update_plot(self)
    update_undo_redo_buttons(self)

    if not self.signals:
        self.selected_signal_index = -1
        self.addComponent.setText("Add Component")

def update_undo_redo_buttons(self):
    # Update button states and styles
    has_undo = bool(self.undo_stack)
    has_redo = bool(self.redo_stack)
    
    self.undo_button.setEnabled(has_undo)
    self.redo_button.setEnabled(has_redo)
    
    # Update visual styles
    self.undo_button.setStyleSheet(
        self.button_styles['enabled'] if has_undo 
        else self.button_styles['disabled']
    )
    self.redo_button.setStyleSheet(
        self.button_styles['enabled'] if has_redo 
        else self.button_styles['disabled']
    )

def delete_signal(self, add_command_bool= False):
    selected_items = self.listWidget.selectedItems()
    if not selected_items:
        return
            
    deleted_signals = []
    deleted_properties = []
    deleted_indices = []
    deleted_names = []
    
    # First collect all items to delete
    for item in selected_items:
        index = self.listWidget.row(item)
        deleted_signals.append(self.signals[index])
        deleted_properties.append(self.signal_properties[index])
        deleted_indices.append(index)
        deleted_names.append(item.text())
    
    # Create command for undo/redo
    command = Command(
        action='delete',
        signals=deleted_signals,
        properties=deleted_properties,
        indices=deleted_indices,
        signal_names=deleted_names
    )
    if add_command_bool:
        add_command(self,command)

    # Actually remove the items (in reverse order to maintain correct indices)
    for index in sorted(deleted_indices, reverse=True):
        self.listWidget.takeItem(index)
        del self.signals[index]
        del self.signal_properties[index]

    # Update UI state
    if not self.signals:
        self.selected_signal_index = -1
        self.addComponent.setText("Add Component")
    
    # reset input boxes if self.signals is empty
    if not self.signals:
            
        self.comboBox.setCurrentText("Sin")
        self.lineEdit.setText("0")
        self.lineEdit_2.setText("0")
        self.lineEdit_3.setText("untitled")
        self.lineEdit_4.setText("0")


    # Update plot
    update_plot(self, update_on_sampling=not add_command_bool)

def select_signal(self, update_on_sampling=False):
    self.selected_signal_index = self.listWidget.currentRow()
    if self.selected_signal_index >= 0:
        props = self.signal_properties[self.selected_signal_index]
        print(props)
        self.comboBox.setCurrentText(props['type'])
        self.lineEdit.setText(str(f"{props['amplitude']:.2f}"))
        self.lineEdit_2.setText(str(f"{props['frequency']:.2f}"))
        self.lineEdit_3.setText(props['name'])
        self.lineEdit_4.setText(str(f"{props['phase_shift']:.2f}"))
        self.addComponent.setText("Exit Edit Mode")
        update_plot(self, update_on_sampling=update_on_sampling)

        # Clear preview signal
        self.is_previewing = False
        self.preview_signal = None
        



def handle_component_button(self, update_on_sampling=False):
    if self.addComponent.text() == "Add Component":
        add_signal(self, not update_on_sampling)
    else:
        edit_signal(self, update_on_sampling)

def update_signal_real_time(self, input_box):
    if self.selected_signal_index >= 0:
        try:
            signal_type = self.comboBox.currentText()
            amplitude = float(self.lineEdit.text() or 0)
            frequency = float(self.lineEdit_2.text() or 0)
            phase_shift = float(self.lineEdit_4.text() or 0)
            
            #Update signal
            if hasattr(self, 'selected_example_signal') and self.selected_example_signal is not None:
                signal  = self.selected_example_signal
                signal_name = self.selected_example_name
                # Clear the example signal after use
                del self.selected_example_signal
                del self.selected_example_name
            else : 
                signal = generate_signal(self,signal_type, amplitude, frequency, phase_shift)
            self.signals[self.selected_signal_index] = signal
            
            # Update properties

            if input_box == 1:
                self.signal_properties[self.selected_signal_index]['amplitude'] = amplitude
            elif input_box == 2:
                self.signal_properties[self.selected_signal_index]['frequency'] = frequency
            elif input_box == 3:
                self.signal_properties[self.selected_signal_index]['name'] = self.lineEdit_3.text().strip()
            elif input_box == 4:
                self.signal_properties[self.selected_signal_index]['phase_shift'] = phase_shift
            
            # Update plot
            update_plot(self)
        except ValueError:
            pass  # Handle incomplete/invalid input gracefully

def update_plot(self, update_on_sampling=False, not_real_time=True):
    self.signalViewer.clear()
    if update_on_sampling:
        self.t_orig = np.linspace(0, 1, 7000, endpoint=False)

        if len(self.signals) == 0:
            self.samplingGraph.clear()
            self.differenceGraph.clear()
            self.frequencyDomainGraph.clear()
            
            return
    
    if self.signals:
        # Plot all signals in white

        
        
        combined_signal = np.sum(self.signals, axis=0)
        if update_on_sampling:
            
            self.signalViewer.plot(self.t_orig,combined_signal, pen='w')
        else:
            self.signalViewer.plot(combined_signal, pen='w')

        if update_on_sampling:
            self.signalData = combined_signal
            

        
        # Plot selected signal in red
        if self.selected_signal_index >= 0:
            selected_signal = self.signals[self.selected_signal_index]
            if update_on_sampling:
                self.signalViewer.plot(self.t_orig,selected_signal, pen='r')
            else:

                self.signalViewer.plot(selected_signal, pen='r')

    # Draw preview signal in green if previewing
    if self.is_previewing and self.preview_signal is not None:
        if update_on_sampling:
            self.signalViewer.plot(self.t_orig, self.preview_signal, pen='g')
        else:
            self.signalViewer.plot(self.preview_signal, pen='g')

    # Draw preview total in purple if previewing
    if self.is_previewing and self.preview_total is not None:
        if update_on_sampling:
            self.signalViewer.plot(self.t_orig, self.preview_total, pen='m')
        else:
            self.signalViewer.plot(self.preview_total, pen='m')
    
    if not_real_time:
        if update_on_sampling and self.signalData is not None:
            # Generate time array
            self.t_orig = np.linspace(0, 1, 7000, endpoint=False)
            
            # Generate and store noisy signal
            snr_db = self.snr_slider.value()
            self.noisy_signal = self.add_noise(self.signalData, snr_db, self.samplingType.currentText())
            
            # Perform sampling on noisy signal
            self.startSampling(self.t_orig, self.noisy_signal)

    # Move plotting outside the update_on_sampling condition
    if hasattr(self, 't_orig') and hasattr(self, 'signalData'):
        # Plot original signal
        self.signalViewer.plot(self.t_orig, self.signalData, pen='w', 
                            name=f'Original Signal\nSampling Freq: {self.samplingFactor * self.f_max:.2f} Hz\nMax Freq: {self.f_max:.2f} Hz')

    if hasattr(self, 't_orig') and hasattr(self, 'noisy_signal'):
        # Plot noisy signal
        self.signalViewer.plot(self.t_orig, self.noisy_signal, pen='y', 
                            name='Noisy Signal')

    if hasattr(self, 't_sampled') and hasattr(self, 'sampled_signal'):
        # Plot sampled points
        self.signalViewer.plot(self.t_sampled, self.sampled_signal, 
                            pen=None, symbol='o', symbolPen='b', 
                            symbolBrush='b', symbolSize=6, 
                            name='Sampled Points')

def on_parameter_changed(self):
    # Get current parameter values
    if self.selected_signal_index == -1:
        amplitude = float(self.lineEdit.text())
        frequency = float(self.lineEdit_2.text())
        phase = float(self.lineEdit_4.text())
        signal_type = self.comboBox.currentText()

        # Generate preview signal (green)
        self.preview_signal = generate_signal(self,signal_type, amplitude, frequency, phase)
        
        # Calculate preview total (purple)
        self.preview_total = np.zeros_like(self.preview_signal)
        for signal in self.signals:
            self.preview_total += signal
        self.preview_total += self.preview_signal
        
        self.is_previewing = True
        update_plot(self)

def start_sampling(self):
    if not self.signals:
        return
        
    try:
        # Generate unique filename with proper path
        filename = self.generate_filename(self.signal_properties)
        filepath = os.path.join(os.getcwd(), filename)  # Use proper path join
        
        # Save signal 
        self.save_signals_to_csv(filepath)
        self.emit_signals(filepath)

        # save the self.signals array as json and self.signal_properties to a file to reload later
        save_signals_to_json(self.signals, self.signal_properties)

        self.clear_data()
        self.close()
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Sampling failed: {str(e)}")

def save_signals_to_json(signals, signal_properties):
    # Save signals and properties to JSON
    data = {
        'signals': signals,
        'properties': signal_properties
    }
    # object with type 'ndarray' is not JSON serializable
    for i in range(len(data['signals'])):
        data['signals'][i] = data['signals'][i].tolist()

        
    
    with open('signals.json', 'w') as file:
        json.dump(data, file)

def load_signals_from_json():
    # Load signals and properties from JSON
    with open('signals.json', 'r') as file:
        data = json.load(file)
    return data['signals'], data['properties']

def open_examples_dialog(self, add_command_bool= False):
    dialog = QDialog(self)
    dialog.setWindowTitle("Choose an Example")
    layout = QVBoxLayout()

    examples = ["Lec Example", "Amplitude Modulation", "Constructive Interference", "Beats"]

    for example in examples:
        button = self.createButton(example)
        button.clicked.connect(lambda checked, name=example: select_example(self,name, dialog, add_command_bool))
        layout.addWidget(button)

    dialog.setLayout(layout)
    dialog.exec_()

def select_example(self, example_name, dialog, add_command_bool= False):
    signal = None  # Initialize a signal variable

    if example_name == "Lec Example":
        signal = generate_signal(self,"Sin", 1, 2, 0) + generate_signal(self,"Sin", 1, 6, 0)
    elif example_name == "Amplitude Modulation":
        signal = generate_signal(self,"Sin", 1, 50, 0) + generate_signal(self,"Sin", 0.5, 5, 0)
    elif example_name == "Constructive Interference":
        signal = generate_signal(self,"Sin", 1, 5, 0) + generate_signal(self,"Sin", 1, 5, 0)
    elif example_name == "Beats":
        signal = generate_signal(self,"Sin", 1, 10, 0) + generate_signal(self,"Sin", 1, 11, 0)
    
    if signal is not None:
        # Store the signal and example name in instance variables
        self.selected_example_signal = signal
        self.selected_example_name = example_name
        if add_command_bool:
            add_signal(self, add_command_bool=True)
            update_plot(self)
        else:
            add_signal(self, add_command_bool=False)
            update_plot(self, update_on_sampling=True)
        dialog.accept()  # Close the dialog