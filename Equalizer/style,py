


# Add theme switching capability
THEMES = {
    'DARK': {
        'background': '#1E1E2E',
        'secondary': '#252535',
        'accent': '#7AA2F7',
        'text': '#CDD6F4'
    },
    'LIGHT': {
        'background': '#FFFFFF',
        'secondary': '#F0F0F0', 
        'accent': '#2962FF',
        'text': '#000000'
    }
}

# Add these color constants at the start of setupUi
COLORS = {
    'background': '#1E1E2E', 
    'secondary': '#252535',  
    'accent': '#7AA2F7',   
    'text': '#CDD6F4',      
    'button': '#394168',   
    'button_hover': '#4A5178'
}

# Add these style constants
STYLES = {
    'BUTTON': f"""
        QPushButton {{
            background-color: {COLORS['button']};
            color: {COLORS['text']};
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 500;
            transition: background-color 0.3s;
        }}
        QPushButton:hover {{
            background-color: {COLORS['button_hover']};
        }}
        QPushButton:pressed {{
            background-color: {COLORS['accent']};
        }}
    """,
    
    'COMBOBOX': f"""
        QComboBox {{
            background-color: {COLORS['secondary']};
            color: {COLORS['text']};
            border: 2px solid {COLORS['accent']};
            border-radius: 6px;
            padding: 5px 10px;
            min-width: 150px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox::down-arrow {{
            image: url(images/dropdown.png);
            width: 12px;
            height: 12px;
        }}
    """,
    
    'SLIDER': f"""
        QSlider::groove:horizontal {{
            border: none;
            height: 6px;
            background: {COLORS['secondary']};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {COLORS['accent']};
            border: none;
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {COLORS['button_hover']};
        }}
    """,
    
    'GRAPH': f"""
        border: 2px solid {COLORS['accent']};
        border-radius: 10px;
        padding: 10px;
        background-color: {COLORS['background']};
    """,
    
    'CHECKBOX': f"""
        QCheckBox {{
            color: {COLORS['text']};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {COLORS['accent']};
            border-radius: 4px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {COLORS['accent']};
        }}
    """
}


STYLES['COMBOBOX'] = f"""
    QComboBox {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['accent']};
        border-radius: 6px;
        padding: 5px 10px;
        min-width: 150px;
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox::down-arrow {{
        image: url(images/dropdown.png);
        width: 12px;
        height: 12px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        selection-background-color: {COLORS['accent']};
        selection-color: {COLORS['text']};
        border: 1px solid {COLORS['accent']};
        border-radius: 4px;
    }}
"""
STYLES['COMBOBOX'] = f"""
    QComboBox {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['accent']};
        border-radius: 6px;
        padding: 5px 10px;
        min-width: 150px;
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox::down-arrow {{
        image: url(images/dropdown.png);
        width: 12px;
        height: 12px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        selection-background-color: {COLORS['accent']};
        selection-color: {COLORS['text']};
        border: 1px solid {COLORS['accent']};
        border-radius: 4px;
    }}
"""

STYLES['SPECTROGRAM'] = f"""
    border: 2px solid {COLORS['accent']};
    border-radius: 10px;
    padding: 5px;
    background-color: {COLORS['secondary']};
"""

# First, update the STYLES and COLORS constants at the top of the file

# Update font constants
FONT_STYLES = {
    'REGULAR': {
        'family': 'Segoe UI',
        'size': 10,
        'weight': 'normal'
    },
    'HEADING': {
        'family': 'Segoe UI',
        'size': 12,
        'weight': 'bold'
    },
    'BUTTON': {
        'family': 'Segoe UI',
        'size': 10,
        'weight': 'bold'
    }
}

# Update the ComboBox style
STYLES['COMBOBOX'] = f"""
    QComboBox {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['accent']};
        border-radius: 8px;
        padding: 8px 15px;
        min-width: 200px;
        min-height: 40px;
        font-family: {FONT_STYLES['REGULAR']['family']};
        font-size: 14px;
        font-weight: bold;
    }}
    
    QComboBox:hover {{
        border-color: {COLORS['button_hover']};
    }}
    
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    
    QComboBox::down-arrow {{
        image: url(images/dropdown.png);
        width: 16px;
        height: 16px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        selection-background-color: {COLORS['accent']};
        selection-color: {COLORS['text']};
        border: 1px solid {COLORS['accent']};
        border-radius: 4px;
        padding: 4px;
        font-size: 14px;
    }}
"""

# Update FONT_STYLES with fallback fonts
FONT_STYLES = {
    'REGULAR': {
        'family': 'Segoe UI, Arial, Helvetica, sans-serif',
        'size': 10,
        'weight': 'normal'
    },
    'HEADING': {
        'family': 'Segoe UI, Arial, Helvetica, sans-serif', 
        'size': 12,
        'weight': 'bold'
    },
    'BUTTON': {
        'family': 'Segoe UI, Arial, Helvetica, sans-serif',
        'size': 10,
        'weight': 'bold'
    }
}

COLORS = {
    'background': '#1A1B1E',  # Darker background
    'secondary': '#2A2B2E',   # Slightly lighter than background
    'accent': '#7289DA',      # Discord-like blue accent
    'text': '#FFFFFF',        # Pure white text
    'button': '#404249',      # Button background
    'button_hover': '#5865F2', # Button hover state
    'success': '#43B581',     # Success/positive color
    'error': '#F04747'        # Error/negative color
}

# Update button styles with modern aesthetics
STYLES['BUTTON'] = f"""
    QPushButton {{
        background-color: {COLORS['button']};
        color: {COLORS['text']};
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }}
    QPushButton:hover {{
        background-color: {COLORS['button_hover']};
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }}
    QPushButton:pressed {{
        background-color: {COLORS['accent']};
        transform: translateY(1px);
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    }}
"""

# Enhanced ComboBox styling
STYLES['COMBOBOX'] = f"""
    QComboBox {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['accent']};
        border-radius: 8px;
        padding: 8px 16px;
        min-width: 200px;
        font-size: 14px;
        font-weight: 600;
    }}
    QComboBox:hover {{
        border-color: {COLORS['button_hover']};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox::down-arrow {{
        image: url(images/dropdown.png);
        width: 16px;
        height: 16px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        selection-background-color: {COLORS['accent']};
        selection-color: {COLORS['text']};
        border: 1px solid {COLORS['accent']};
        border-radius: 4px;
    }}
"""

# Add glass-morphism effect to main panels
STYLES['PANEL'] = f"""
    QFrame {{
        background-color: rgba(42, 43, 46, 0.7);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
    }}
"""

# Update graph styling
STYLES['GRAPH'] = f"""
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px;
    background-color: rgba(26, 27, 30, 0.8);
    backdrop-filter: blur(10px);
"""

# Add these new styles for spectrograms and audiogram
STYLES['SPECTROGRAM'] = f"""
    QWidget {{
        background-color: rgba(26, 27, 30, 0.8);
        border: 1px solid {COLORS['accent']};
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        background-color: rgba(26, 27, 30, 0.8);
        backdrop-filter: blur(10px);
    }}
"""

STYLES['AUDIOGRAM'] = f"""
    QWidget {{
        background-color: rgba(26, 27, 30, 0.9);
        border: 2px solid {COLORS['accent']};
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }}
"""

# Add modern toggle button style
STYLES['TOGGLE_BUTTON'] = f"""
    QPushButton {{
        background-color: {COLORS['secondary']};
        color: {COLORS['text']};
        border: 2px solid {COLORS['accent']};
        border-radius: 20px;
        padding: 10px 20px;
        margin: 0px;
        font-size: 14px;
        font-weight: 600;
        min-width: 120px;
    }}
    QPushButton:checked {{
        background-color: {COLORS['accent']};
        color: {COLORS['text']};
    }}
    QPushButton:hover {{
        background-color: {COLORS['button_hover']};
        border-color: {COLORS['button_hover']};
    }}
"""

STYLES['CHECKBOX'] = f"""
    QCheckBox {{
        color: {COLORS['text']};
        font-size: 14px;
        font-weight: 600;
        spacing: 8px;
        padding: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 24px;
        height: 24px;
        border: 2px solid {COLORS['accent']};
        border-radius: 12px;
        background-color: transparent;
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {COLORS['accent']};
        image: url(images/check.png);
    }}
    
    QCheckBox::indicator:unchecked:hover {{
        border-color: {COLORS['button_hover']};
    }}
    
    QCheckBox::indicator:checked:hover {{
        background-color: {COLORS['button_hover']};
    }}
"""

# Update spectrogram and audiogram styles with modern aesthetics
STYLES['SPECTROGRAM'] = f"""
    QWidget {{
        background-color: {COLORS['background']};
        border: 2px solid {COLORS['accent']};
        border-radius: 15px;
        padding: 15px;
    }}
"""

STYLES['SPECTROGRAM_PLOT'] = {
    'facecolor': COLORS['background'],
    'text_color': COLORS['text'],
    'grid_color': f"{COLORS['accent']}33",  # 20% opacity
    'spine_color': COLORS['accent'],
    'title_size': 12,
    'label_size': 10,
    'tick_size': 8
}

STYLES['AUDIOGRAM'] = f"""
    QWidget {{
        background: linear-gradient(135deg, 
            {COLORS['background']}, 
            {COLORS['secondary']});
        border: 2px solid {COLORS['accent']};
        border-radius: 20px;
        padding: 20px;
    }}
    
    QLabel {{
        color: {COLORS['text']};
        font-size: 14px;
        font-weight: bold;
    }}
    
    QPushButton {{
        background-color: {COLORS['button']};
        color: {COLORS['text']};
        border: none;
        border-radius: 10px;
        padding: 8px 15px;
        font-weight: bold;
    }}
    
    QPushButton:hover {{
        background-color: {COLORS['button_hover']};
    }}
"""

STYLES['SPECTROGRAM'] = f"""
    QWidget {{
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        background-color: rgba(26, 27, 30, 0.8);
        backdrop-filter: blur(10px);
    }}
"""

STYLES['SPECTROGRAM_PLOT'] = {
    'facecolor': 'none',  # Transparent background
    'text_color': COLORS['text'],
    'grid_color': f"{COLORS['accent']}33",  # 20% opacity
    'spine_color': COLORS['accent'],
    'title_size': 12,
    'label_size': 10,
    'tick_size': 8
}

# Update spectrogram style to ensure transparency
STYLES['SPECTROGRAM'] = f"""
    QWidget {{
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        background-color: rgba(26, 27, 30, 0.8);
        backdrop-filter: blur(10px);
    }}
"""

STYLES['AUDIOGRAM'] = f"""
    QWidget {{
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        background-color: rgba(26, 27, 30, 0.8);
        backdrop-filter: blur(10px);
    }}
"""

STYLES['SLIDERS_PANEL'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border-radius: 15px;
        border: 1px solid {COLORS['accent']};
        padding: 10px;
    }}
    QLabel {{
        color: {COLORS['text']};
        font-size: 12px;
        font-weight: bold;
        padding: 5px;
    }}
"""

STYLES['SLIDER'] = f"""
    QSlider {{
        margin: 10px;
    }}
    QSlider::groove:horizontal {{
        border: none;
        height: 6px;
        background: {COLORS['background']};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {COLORS['accent']};
        border: none;
        width: 18px;
        height: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {COLORS['button_hover']};
    }}
"""

STYLES['SLIDERS_CONTAINER'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border: 1px solid {COLORS['accent']};
        border-radius: 15px;
        padding: 0px;
        margin: 0px 0px;
    }}
    QLabel {{
        color: {COLORS['text']};
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 5px;
    }}
"""


STYLES['SPECTROGRAM_AXES'] = {
    'grid_alpha': 0.2,
    'grid_color': COLORS['text'],
    'label_color': COLORS['text'],
    'tick_color': COLORS['text'],
    'title_color': COLORS['text'],
    'spine_color': COLORS['accent']
}

STYLES['SLIDERS_CONTAINER'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border: 2px solid {COLORS['accent']};
        border-radius: 20px;
        padding: 15px;
        margin: 10px 0px;
    }}
"""

STYLES['SLIDER'] = f"""
    QSlider {{
        height: 50px;
        margin: 10px;
    }}
    
    QSlider::groove:horizontal {{
        border: none;
        height: 4px;
        background: {COLORS['background']};
        border-radius: 2px;
        margin: 0px;
    }}
    
    QSlider::handle:horizontal {{
        background: {COLORS['accent']};
        border: 2px solid {COLORS['accent']};
        width: 16px;
        height: 16px;
        margin: -6px 0;
        border-radius: 10px;
        transition: background-color 0.2s;
    }}
    
    QSlider::handle:horizontal:hover {{
        background: {COLORS['button_hover']};
        border-color: {COLORS['button_hover']};
        transform: scale(1.1);
    }}
    
    QSlider::sub-page:horizontal {{
        background: {COLORS['accent']};
        border-radius: 2px;
    }}
"""

STYLES['SLIDER_LABEL'] = f"""
    QLabel {{
        color: {COLORS['text']};
        font-size: 13px;
        font-weight: bold;
        padding: 5px;
    }}
"""

STYLES['SLIDER_VALUE'] = f"""
    QLabel {{
        color: {COLORS['accent']};
        font-size: 12px;
        font-weight: bold;
        padding: 2px 8px;
        background: rgba(114, 137, 218, 0.1);
        border-radius: 10px;
    }}
"""

STYLES['SLIDERS_CONTAINER'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border: 1px solid {COLORS['accent']};
        border-radius: 12px;
        padding: 0px;
        margin: 2px 0px;
    }}
"""

STYLES['PANEL'] = f"""
    QFrame {{
        background-color: rgba(42, 43, 46, 0.7);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
    }}
"""

STYLES['PANEL'] = f"""
    QFrame {{
        background-color: rgba(42, 43, 46, 0.7);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
    }}
"""

STYLES['SCROLL_AREA'] = f"""
    QScrollArea {{
        border: none;
        background-color: transparent;
        margin: 0px;
        padding: 0px;
    }}
    
    QScrollArea > QWidget > QWidget {{
        background-color: transparent;
    }}
    
    QScrollBar:vertical {{
        border: none;
        background: {COLORS['secondary']};
        width: 6px;
        margin: 0px;
        border-radius: 3px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {COLORS['accent']};
        min-height: 20px;
        border-radius: 3px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {COLORS['button_hover']};
    }}
    
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
    }}
"""

STYLES['SIDEBAR'] = f"""
    QFrame {{
        background-color: {COLORS['secondary']};
        border-radius: 15px;
        padding:5px;
    }}
"""

STYLES['SIDEBAR_SECTION'] = f"""
    QWidget {{
        background-color: {COLORS['secondary']};
        border-radius: 12px;
        padding: 0px;
        margin: 0px 0px;
    }}
"""

STYLES['SECTION_TITLE'] = f"""
    QLabel {{
        color: {COLORS['text']};
        font-size: 16px;
        font-weight: 500;
        letter-spacing: 0.5px;
        padding:0px 0px 0px 0px;
        margin: 0;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
        border-bottom: 1px solid {COLORS['accent']};
        border-bottom:0px;
        border-radius: 0px;
    }}
    QLabel:hover {{
        color: {COLORS['accent']};
    }}
"""

STYLES['DIVIDER'] = f"""
    QFrame {{
        background-color: {COLORS['accent']};
        border: none;
        height: 1px;
        margin: 10px 0px;
    }}
"""

# Add these graph style enhancements
GRAPH_STYLES = {
    'AXIS': {
        'color': COLORS['text'],
        'width': 1.5
    },
    'GRID': {
        'color': f"{COLORS['text']}33",  # 20% opacity
        'width': 0.5
    },
    'CURVE': {
        'original': {'color': '#7289DA', 'width': 2},
        'modified': {'color': '#43B581', 'width': 2}
    },
    'LABELS': {
        'color': COLORS['text'],
        'size': '12pt'
    },
    'BACKGROUND': 'transparent'
}

DOMAIN_GRAPH_STYLES = {
    'TIME': {
        'color': '#7289DA',  # Discord blue for time domain
        'width': 2,
        'fill': '#7289DA33'  # Semi-transparent fill
    },
    'FREQ': {
        'color': '#43B581',  # Discord green for frequency domain
        'width': 2,
        'fill': '#43B58133'  # Semi-transparent fill
    },
    'AXES': {
        'text_color': COLORS['text'],
        'grid_color': f"{COLORS['text']}22",
        'label_size': '11pt',
        'title_size': '12pt'
    },
    'BACKGROUND': 'transparent'
}
