from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox,
    QHBoxLayout, QLabel, QFrame, QSplitter
)
from PyQt5.QtCore import Qt
from src.componnents.Navigator import Navigator
from src.componnents.ScheduleTable import ScheduleTable
from src.models.schedule import Schedule
from src.controllers.ScheduleController import ScheduleController
from typing import List, Callable

class ScheduleWindow(QMainWindow):
    """
    A window for displaying and managing generated schedules.
    Allows navigation through schedules, exporting them to a file,
    and returning to the course selection window.
    """
    def __init__(self, schedules: List[Schedule], controller: ScheduleController):
        """
        Initializes the ScheduleWindow.

        Args:
            schedules (List[Schedule]): List of schedules to display.
            controller (ScheduleController): Controller for schedule operations.
        """
        super().__init__()
        self.setObjectName("ScheduleWindow")  # Set object name for styling
        self.setWindowTitle("Generated Schedules")
        self.showMaximized()
        self.controller = controller  # Controller for handling schedule-related operations
        self.schedules = schedules  # List of schedules to display

        # Create the main container widget and layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Top section: Header and action buttons
        top_section = QHBoxLayout()
        
        # Header area (left side of top section)
        header_area = QVBoxLayout()
        
        # Add headline and subtitle
        self.headline = QLabel("Schedule King")  # Main headline label
        self.headline.setObjectName("headline_label")
        self.headline.setAlignment(Qt.AlignLeft)
        
        self.subtitle = QLabel("Plan Your Study Schedule Like a King")  # Subtitle label
        self.subtitle.setObjectName("subtitle_label")
        self.subtitle.setAlignment(Qt.AlignLeft)
        
        header_area.addWidget(self.headline)
        header_area.addWidget(self.subtitle)
        header_area.addStretch()
        
        # Action buttons area (right side of top section)
        buttons_area = QHBoxLayout()
        buttons_area.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Buttons for exporting schedules and navigating back
        self.export_button = QPushButton("Export to TXT File")  # Export button
        self.export_button.setObjectName("top_action_button")
        
        self.back_button = QPushButton("Back to Course Selection")  # Back button
        self.back_button.setObjectName("top_action_button")
        
        # Connect button signals to their respective slots
        self.export_button.clicked.connect(self.export_to_file)  # Export schedules
        self.back_button.clicked.connect(self.navigateToCourseWindow)  # Navigate back
        
        # Add buttons to the action area
        buttons_area.addWidget(self.export_button)
        buttons_area.addWidget(self.back_button)
        
        # Combine header and buttons in the top section
        top_section.addLayout(header_area, 2)
        top_section.addLayout(buttons_area, 1)
        
        # Add the top section to the main layout
        self.main_layout.addLayout(top_section)
        
        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)  # Horizontal line
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("separator_line")
        self.main_layout.addWidget(line)
        
        # Create the navigator for navigating through schedules - more compact
        self.navigator = Navigator(schedules)
        self.navigator.setObjectName("compact_navigator")
        self.navigator.setMaximumHeight(100)  # Limit the height
        
        # Add navigator to the main layout
        self.main_layout.addWidget(self.navigator)
        
        # Create the schedule table for displaying schedule details
        self.schedule_table = ScheduleTable()
        self.schedule_table.setObjectName("enhanced_table")
        
        # Connect navigator's schedule_changed signal to update the table
        self.navigator.schedule_changed.connect(self.on_schedule_changed)
        
        # Add the schedule table with expanded size
        self.main_layout.addWidget(self.schedule_table, 1)
        
        # Set the central widget
        self.setCentralWidget(self.central_widget)

        # Callback for navigating back to the course selection window
        self.on_back: Callable[[], None] = lambda: None
        
        # Display the first schedule if available
        if schedules:
            self.on_schedule_changed(0)

    def on_schedule_changed(self, index: int):
        """
        Updates the schedule table when the selected schedule changes.
        
        Args:
            index (int): The index of the selected schedule.
        """
        if 0 <= index < len(self.schedules):  # Ensure the index is valid
            self.schedule_table.display_schedule(self.schedules[index])  # Display the selected schedule

    def displaySchedules(self, schedules: List[Schedule]):
        """
        Updates the navigator and table with new schedules and displays the first one.

        Args:
            schedules (List[Schedule]): List of schedules to display.
        """
        self.schedules = schedules  # Update the schedules list
        self.navigator.set_schedules(schedules)  # Update the navigator with new schedules
        if schedules:
            self.on_schedule_changed(0)  # Display the first schedule
        else:
            self.schedule_table.clearContents()  # Clear the table if no schedules are available

    def navigateToCourseWindow(self):
        """
        Triggers the callback to navigate back to the course selection window.
        """
        self.on_back()  # Call the callback function

    def export_to_file(self):
        """
        Opens a file dialog and saves the schedules to the selected file using the controller.
        """
        # Open a file dialog to select the save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Schedules", "", "Text Files (*.txt)"
        )
        if file_path:  # If a file path is selected
            try:
                # Use the controller to export schedules to the selected file
                self.controller.export_schedules(file_path)
                QMessageBox.information(
                    self, "Export Successful",
                    f"Schedules were saved successfully to:\n{file_path}"
                )
            except Exception as e:
                # Show an error message if the export fails
                QMessageBox.critical(
                    self, "Export Failed",
                    f"Failed to export schedules:\n{str(e)}"
                )