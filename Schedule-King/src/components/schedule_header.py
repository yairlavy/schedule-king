from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QPixmap
from src.components.export_controls import ExportControls
from src.controllers.ScheduleController import ScheduleController
import os

class ScheduleHeader(QWidget):
    """
    Header component for the schedule window containing:
    - Back button
    - Title with crown icon
    - Export controls
    """
    def __init__(self, controller : ScheduleController ,export_handler):
        super().__init__()
        self.export_handler = export_handler
        self.controller = controller  # Reference to the controller for handling back navigation
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize and setup the header UI components"""
        # Main layout (this will be removed or modified in ScheduleWindow)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        self.setLayout(header_layout) # Keep this for now, will be replaced when components are moved out
        
        # Back button (make public)
        self.back_button = QPushButton("  Back to Course Selection")
        self.back_button.setObjectName("top_action_button")
        back_icon = QIcon(os.path.join(os.path.dirname(__file__), "../assets/back.png"))
        if not back_icon.isNull():
            self.back_button.setIcon(back_icon)
            self.back_button.setText(" Back to Course Selection")
        else:
            self.back_button.setText("← Back to Course Selection")
            
        # Title container (make public)
        self.title_container = QWidget()
        self.title_container.setObjectName("title_container")
        title_layout = QVBoxLayout(self.title_container)
        title_layout.setContentsMargins(15, 10, 15, 10)
        title_layout.setSpacing(0)
        
        # Crown icon
        crown_label = QLabel()
        crown_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "../assets/king.png"))
        if not crown_pixmap.isNull():
            crown_label.setPixmap(crown_pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            crown_label = QLabel("👑")
            crown_label.setFont(QFont("Segoe UI Emoji", 36))
        
        crown_label.setAlignment(Qt.AlignCenter)
        crown_label.setMaximumWidth(60)
        
        # Title text
        title_text_layout = QVBoxLayout()
        self.headline = QLabel("Schedule King")
        self.headline.setObjectName("headline_label")
        self.headline.setFont(QFont("Arial", 24, QFont.Bold))
        
        self.subtitle = QLabel("Plan Your Study Schedule Like a King")
        self.subtitle.setObjectName("subtitle_label")
        self.subtitle.setFont(QFont("Arial", 16))
        
        title_text_layout.addWidget(self.headline)
        title_text_layout.addWidget(self.subtitle)
        
        # Combine crown and text
        title_row = QHBoxLayout()
        title_row.addWidget(crown_label)
        title_row.addLayout(title_text_layout)
        title_row.addStretch(1)
        title_layout.addLayout(title_row)
        
        # Export controls (make public)
        self.export_controls = ExportControls( self.controller , self.export_handler)
        self.export_controls.setObjectName("export_controls_widget")

        # Assemble header - This part will be removed in ScheduleWindow's layout setup
        # header_layout.addWidget(self.back_button)
        # header_layout.addStretch(1)
        # header_layout.addWidget(self.title_container)
        # header_layout.addStretch(1)
        # header_layout.addWidget(self.export_controls)
