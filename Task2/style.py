# Define color palette
COLORS = {
    'background': '#1e1e1e',
    'surface': '#252526',
    'primary': '#007ACC',
    'secondary': '#3E3E42',
    'text': '#CCCCCC',
    'border': '#323232'
}

# Add to COLORS dictionary
COLORS.update({
    'hover': '#404040',
    'success': '#4CAF50',
    'warning': '#FFA726',
    'info': '#29B6F6'
})

BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['primary']};
        border-color: {COLORS['primary']};
    }}
    QPushButton:pressed {{
        background-color: {COLORS['hover']};
    }}
"""

LIST_STYLE = f"""
    QListWidget {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 4px;
    }}
    QListWidget::item:selected {{
        background-color: {COLORS['primary']};
        color: white;
    }}
"""

COMBO_STYLE = f"""
    QComboBox {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 4px 8px;
        min-width: 100px;
    }}
    QComboBox:hover {{
        border-color: {COLORS['primary']};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
"""

LINE_EDIT_STYLE = f"""
    QLineEdit {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 14px;    
    }}
    QLineEdit:focus {{
        border-color: {COLORS['primary']};
    }}
"""


BROWSE_BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['primary']};
        border-radius: 8px;
        font-weight: bold;
        font-size: 15px;
        padding: 10px 20px;
        margin: 5px;
        text-align: center;
        min-width: 120px;
    }}
    QPushButton:hover {{
        background-color: {COLORS['primary']};
        color: white;
    }}
    QPushButton:pressed {{
        background-color: {COLORS['hover']};
    }}
"""

OPTIONS_GROUP_STYLE = f"""
    QGroupBox {{
        color: {COLORS['text']};
        border: 2px solid {COLORS['primary']};
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
        font-size: 16px;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        padding: 0 8px;
        color: {COLORS['primary']};
    }}
"""

SLIDER_STYLE = f"""
    QSlider::groove:horizontal {{
        border: 1px solid {COLORS['border']};
        height: 4px;
        background: {COLORS['surface']};
        margin: 2px 0;
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {COLORS['primary']};
        border: none;
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 8px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {COLORS['hover']};
        width: 18px;
        height: 18px;
        margin: -7px 0;
    }}
"""

MAIN_WINDOW_STYLE = f"""
            QMainWindow {{
                background: {COLORS['background']};
            }}
            QWidget#container {{
                background: {COLORS['background']};
                border: 1px solid {COLORS['border']};
            }}
            QWidget {{
                background: {COLORS['background']};
                color: {COLORS['text']};
            }}
            
            /* Enhanced Button Styling */
            QPushButton {{
                background: {COLORS['secondary']};
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                color: {COLORS['text']};
                transition: background 0.3s;
            }}
            QPushButton:hover {{
                background: {COLORS['primary']};
                color: white;
            }}
            QPushButton:pressed {{
                background: #005999;
            }}
            
            /* Window Control Buttons */
            QPushButton#windowControl {{
                background: transparent;
                border-radius: 0px;
                padding: 4px 8px;
            }}
            QPushButton#windowControl:hover {{
                background: #3E3E42;
            }}
            QPushButton#closeButton:hover {{
                background: #E81123;
                color: white;
            }}
            
            /* Enhanced ComboBox */
            QComboBox {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
                padding: 5px;
                color: {COLORS['text']};
                min-width: 100px;
            }}
            QComboBox:hover {{
                border: 1px solid {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }}
            
            /* Enhanced GroupBox */
            QGroupBox {{
                border: 1px solid {COLORS['border']};
                color: {COLORS['text']};
                margin-top: 12px;
                font-weight: bold;
                padding-top: 10px;
            }}
            QGroupBox:title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: {COLORS['primary']};
            }}
            
            /* Enhanced Slider */
            QSlider::groove:horizontal {{
                background: {COLORS['surface']};
                height: 4px;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: {COLORS['primary']};
                width: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #2299FF;
                width: 18px;
                margin: -7px 0;
            }}
            
            /* Enhanced Progress Bar */
            QProgressBar {{
                background: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                color: {COLORS['text']};
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                        stop:0 {COLORS['primary']}, 
                                        stop:1 #2299FF);
                border-radius: 3px;
            }}
            
            /* Image Display Enhancement */
            QLabel#imageDisplay {{
                background-color: {COLORS['background']};
                border: 2px solid {COLORS['border']};
                border-radius: 6px;
                padding: 2px;
            }}
            QLabel#imageDisplay:hover {{
                border: 2px solid {COLORS['primary']};
            }}
        """
