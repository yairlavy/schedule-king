from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox,
    QHBoxLayout, QLabel, QFrame, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap, QFont
from src.componnents.Navigator import Navigator
from src.componnents.ScheduleTable import ScheduleTable
from src.models.schedule import Schedule
from src.controllers.ScheduleController import ScheduleController
from typing import List, Callable

class ScheduleWindow(QMainWindow):
    """
    An improved window for displaying and managing generated schedules.
    Features a modern UI with icons, better layout, and enhanced visual design.
    """
    def __init__(self, schedules: List[Schedule], controller: ScheduleController):
        """
        Initializes the ScheduleWindow with enhanced UI.

        Args:
            schedules (List[Schedule]): List of schedules to display.
            controller (ScheduleController): Controller for schedule operations.
        """
        super().__init__()
        # Set window properties
        self.setObjectName("ScheduleWindow")
        self.setWindowTitle("Schedule King")
        self.showMaximized()  # Start maximized for better visibility
        self.controller = controller  # Store controller for operations
        self.schedules = schedules    # Store list of schedules

        # --- MAIN LAYOUT SETUP ---
        # Create the main container widget and layout with proper spacing
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(15)  # Space between major sections
        self.main_layout.setContentsMargins(20, 20, 20, 20)  # Margins around the window
        
        # --- HEADER SECTION ---
        # The header is divided into three sections: back button (left), title (center), export button (right)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # Left section: Back button with icon
        self.back_button = QPushButton("  Back to Course Selection")
        self.back_button.setObjectName("top_action_button")
        back_icon = QIcon("icons/back.png")
        if not back_icon.isNull():
            self.back_button.setIcon(back_icon)
        else:
            # Fallback to text-based icon if image not found
            self.back_button.setText("← Back to Course Selection")
        
        # Center section: Title with crown icon and subtitle
        title_container = QWidget()
        title_container.setObjectName("title_container")
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(15, 10, 15, 10)
        title_layout.setSpacing(0)
        
        # Create crown icon (or emoji fallback) for the title
        crown_label = QLabel()
        crown_pixmap = QPixmap("icons/crown.png")
        if not crown_pixmap.isNull():
            crown_label.setPixmap(crown_pixmap.scaled(38, 38, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            crown_label = QLabel("👑")
            crown_label.setFont(QFont("Segoe UI Emoji", 28))
        
        crown_label.setAlignment(Qt.AlignCenter)
        crown_label.setMaximumWidth(45)  # Larger crown
        
        # Title and subtitle
        title_text_layout = QVBoxLayout()
        self.headline = QLabel("Schedule King")
        self.headline.setObjectName("headline_label")
        
        self.subtitle = QLabel("Plan Your Study Schedule Like a King")
        self.subtitle.setObjectName("subtitle_label")
        
        title_text_layout.addWidget(self.headline)
        title_text_layout.addWidget(self.subtitle)
        
        # Add crown and text to title container
        title_row = QHBoxLayout()
        title_row.addWidget(crown_label)
        title_row.addLayout(title_text_layout)
        title_row.addStretch(1)
        title_layout.addLayout(title_row)
        
        # Export button (right side)
        self.export_button = QPushButton("  Export to TXT File")
        self.export_button.setObjectName("top_action_button")
        export_icon = QIcon("icons/export.png")
        if not export_icon.isNull():
            self.export_button.setIcon(export_icon)
        else:
            # Use text-based icon as fallback
            self.export_button.setText("📥 Export to TXT File")
        
        # Assemble header with proper alignment
        header_layout.addWidget(self.back_button)  # Left aligned
        header_layout.addStretch(1)  # Push to left
        header_layout.addWidget(title_container)  # Center
        header_layout.addStretch(1)  # Push to right
        header_layout.addWidget(self.export_button)  # Right aligned
        
        self.main_layout.addLayout(header_layout)
        
        # Connect button actions
        self.export_button.clicked.connect(self.export_to_file)
        self.back_button.clicked.connect(self.navigateToCourseWindow)
        
        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("separator_line")
        self.main_layout.addWidget(line)
        
        # --- NAVIGATION SECTION ---
        # Create the navigator component for browsing through schedules
        self.navigator = Navigator(schedules)
        self.navigator.setObjectName("compact_navigator")
        
        # Add navigation icons (with fallbacks)
        prev_icon = QIcon("icons/prev.png")
        next_icon = QIcon("icons/next.png")
        
        if not prev_icon.isNull():
            self.navigator.prev_btn.setIcon(prev_icon)
            self.navigator.prev_btn.setText("◀")
        else:
            self.navigator.prev_btn.setText("◀")
            
        if not next_icon.isNull():
            self.navigator.next_btn.setIcon(next_icon)
            self.navigator.next_btn.setText("▶")
        else:
            self.navigator.next_btn.setText("▶")
        
        # Connect navigator's schedule change signal to update the table
        self.navigator.schedule_changed.connect(self.on_schedule_changed)
        
        # Add the navigator to the main layout
        self.main_layout.addWidget(self.navigator)
        
        # --- SCHEDULE TABLE ---
        # Create the main schedule display table
        self.schedule_table = ScheduleTable()
        self.schedule_table.setObjectName("enhanced_table")
        
        # Add the schedule table to the main layout with stretch factor 1
        # This makes it take up most of the available vertical space
        self.main_layout.addWidget(self.schedule_table, 1)

        # Set up navigation callback
        self.on_back: Callable[[], None] = lambda: None
        
        # Set the central widget - THIS WAS MISSING!
        self.setCentralWidget(self.central_widget)
        
        # Display the first schedule if available
        if schedules:
            self.on_schedule_changed(0)

    def on_schedule_changed(self, index: int):
        """
        Updates the schedule table when the selected schedule changes.
        This is called when the user navigates to a different schedule.
        """
        if 0 <= index < len(self.schedules):
            self.schedule_table.display_schedule(self.schedules[index])

    def displaySchedules(self, schedules: List[Schedule]):
        """Updates the navigator and table with new schedules."""
        self.schedules = schedules
        self.navigator.set_schedules(schedules)
        if schedules:
            self.on_schedule_changed(0)
        else:
            self.schedule_table.clearContents()

    def navigateToCourseWindow(self):
        """Navigates back to the course selection window."""
        self.on_back()

    def export_to_file(self):
        """
        Exports all schedules to a text file.
        Shows success/error messages to the user.
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Schedules", "", "Text Files (*.txt)"
        )
        if file_path:
            try:
                # Use the controller to handle the export
                self.controller.export_schedules(file_path)
                QMessageBox.information(
                    self, "Export Successful",
                    f"Schedules were saved successfully to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Failed",
                    f"Failed to export schedules:\n{str(e)}"
                )