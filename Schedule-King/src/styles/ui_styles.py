"""
Stylesheet definitions for UI elements.
This module centralizes styling to avoid hardcoded styles in component classes.
"""

# Button Styles
def red_button_style():
    """Return stylesheet for red buttons (e.g. Clear, Delete, Cancel)."""
    return """
        QPushButton {
            background-color: #F44336;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-size: 12pt;
            font-weight: bold;
            min-width: 120px;
        }
        QPushButton:hover {
            background-color: #D32F2F;
        }
        QPushButton:pressed {
            background-color: #B71C1C;
        }
    """

def green_button_style():
    """Return stylesheet for green buttons (e.g. Submit, Generate, Confirm)."""
    return """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-size: 12pt;
            font-weight: bold;
            min-width: 180px;
        }
        QPushButton:hover {
            background-color: #388E3C;
        }
        QPushButton:pressed {
            background-color: #1B5E20;
        }
    """

def blue_button_style():
    """Return stylesheet for blue buttons (e.g. Load, Info, Secondary actions)."""
    return """
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-size: 12pt;
            font-weight: bold;
            min-width: 150px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #0D47A1;
        }
    """

def disabled_button_style():
    """Return stylesheet for disabled buttons."""
    return """
        QPushButton {
            background-color: #9E9E9E;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-size: 12pt;
            font-weight: bold;
            min-width: 180px;
        }
    """

# Label Styles
def title_label_style():
    """Return stylesheet for title labels."""
    return """
        QLabel {
            color: #1A237E;
            font-size: 34px;
            font-weight: 800;
            font-family: 'Segoe UI', sans-serif;
            border-bottom: 3px solid #C5CAE9;
            padding-bottom: 12px;
        }
    """

def warning_label_style():
    """Return stylesheet for warning labels."""
    return "color: #F44336; font-size: 11pt; font-weight: bold;"

def success_label_style():
    """Return stylesheet for success labels."""
    return "color: #4CAF50; font-size: 11pt; font-weight: bold;"

def instruction_label_style():
    """Return stylesheet for instruction labels."""
    return "color: #3A3A3A; font-size: 12pt; font-style: italic;"

def footer_label_style():
    """Return stylesheet for footer labels."""
    return "color: #78909C; font-size: 10pt; margin-top: 20px;"

def headline_label_style():
    """Return stylesheet for main headline labels."""
    return """
        QLabel {
            color: #1A237E;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
        }
    """

def subtitle_label_style():
    """Return stylesheet for subtitle labels."""
    return """
        QLabel {
            color: #3A3A3A;
            font-size: 16px;
            font-family: 'Segoe UI', sans-serif;
        }
    """

# Background Styles
def course_selector_background():
    """Return stylesheet for the course selector background."""
    return "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E3F2FD, stop:1 #F0F7FF); border-radius: 10px;"

def schedule_background():
    """Return stylesheet for the schedule window background."""
    return "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #F5F5F5, stop:1 #FFFFFF);"

# Table Styles
def table_cell_style(event_class, bg_color, border_color, is_start=False, is_end=False):
    """Generate table cell style for schedule events."""
    border_style = ""
    if is_start:
        border_style = f"border-top-left-radius: 4px; border-top-right-radius: 4px;"
    if is_end:
        border_style += f"border-bottom-left-radius: 4px; border-bottom-right-radius: 4px;"
    
    return f"""
        QLabel {{
            background-color: {bg_color};
            border-left: 4px solid {border_color};
            {border_style}
            padding: 3px;
        }}
    """ 