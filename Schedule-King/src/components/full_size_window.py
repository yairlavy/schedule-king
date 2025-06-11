from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from src.components.schedule_table import ScheduleTable
from src.models.schedule import Schedule
import os

class FullSizeWindow(QMainWindow):
    """
    Full-size window component for displaying a schedule in a maximized window.
    """
    def __init__(self, schedule: Schedule, schedule_number: int):
        super().__init__()
        self.setup_ui(schedule, schedule_number)
        
    def setup_ui(self, schedule: Schedule, schedule_number: int):
        """Initialize and setup the full-size window UI"""
        # Set window properties
        self.setWindowTitle("Schedule King - Full Size View")
        
        # Set window icon
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # Create central widget with layout
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add header with schedule number
        header = QLabel(f"Schedule #{schedule_number + 1}")
        header.setObjectName("headline_label")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create schedule table
        self.schedule_table = ScheduleTable()
        self.schedule_table.setObjectName("enhanced_table")
        
        # Configure table for full size view
        self.schedule_table.horizontalHeader().setStretchLastSection(True)
        self.schedule_table.verticalHeader().setStretchLastSection(True)
        
        # Display the schedule
        self.schedule_table.display_schedule(schedule)
        
        # Add table to layout
        layout.addWidget(self.schedule_table)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Set minimum size
        self.setMinimumSize(800, 600)
        
        # Show window maximized
        self.show()
        self.setWindowState(Qt.WindowMaximized) 