# views/schedule_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox,
    QHBoxLayout
)
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
        self.setWindowTitle("Generated Schedules")
        self.showMaximized()
        self.controller = controller
        self.schedules = schedules

        # Create the main container widget and layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create the navigator
        self.navigator = Navigator(schedules)
        
        # Create the schedule table
        self.schedule_table = ScheduleTable()
        
        # Connect navigator's schedule_changed signal to update the table
        self.navigator.schedule_changed.connect(self.on_schedule_changed)
        
        # Add navigator to the main layout
        self.main_layout.addWidget(self.navigator)
        
        # Add the schedule table inside a horizontal layout for centering
        table_layout = QHBoxLayout()
        table_layout.addWidget(self.schedule_table)
        self.main_layout.addLayout(table_layout)

        # Buttons
        self.export_button = QPushButton("Export to TXT File")
        self.export_button.setFixedSize(150, 50)  # Set fixed size for export button

        self.back_button = QPushButton("Back to Course Selection")
        self.back_button.setFixedSize(150, 50)  # Set fixed size for back button

        # Connect button signals to their respective slots
        self.export_button.clicked.connect(self.export_to_file)
        self.back_button.clicked.connect(self.navigateToCourseWindow)

        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Add buttons to the layout with spacing and alignment
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addSpacing(20)
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addStretch()

        # Add buttons layout to the main layout
        self.main_layout.addLayout(buttons_layout)

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
        if 0 <= index < len(self.schedules):
            self.schedule_table.display_schedule(self.schedules[index])

    def displaySchedules(self, schedules: List[Schedule]):
        """
        Updates the navigator and table with new schedules and displays the first one.

        Args:
            schedules (List[Schedule]): List of schedules to display.
        """
        self.schedules = schedules
        self.navigator.set_schedules(schedules)
        if schedules:
            self.on_schedule_changed(0)
        else:
            self.schedule_table.clearContents()

    def navigateToCourseWindow(self):
        """
        Triggers the callback to navigate back to the course selection window.
        """
        self.on_back()

    def export_to_file(self):
        """
        Opens a file dialog and saves the schedules to the selected file using the controller.
        """
        # Open a file dialog to select the save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Schedules", "", "Text Files (*.txt)"
        )
        if file_path:
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