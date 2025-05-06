# views/schedule_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox,
    QSpacerItem, QSizePolicy, QHBoxLayout
)
from PyQt5.QtCore import Qt
from src.componnents.Navigator import Navigator
from src.models.schedule import Schedule
from typing import List, Callable
from src.services.schedule_api import ScheduleAPI

class ScheduleWindow(QMainWindow):
    """
    A window for displaying and managing generated schedules.
    Allows navigation through schedules, exporting them to a file,
    and returning to the course selection window.
    """
    def __init__(self, schedules: List[Schedule], api: ScheduleAPI):
        """
        Initializes the ScheduleWindow.

        Args:
            schedules (List[Schedule]): List of schedules to display.
            api (ScheduleAPI): API for exporting schedules.
        """
        super().__init__()
        self.setWindowTitle("Generated Schedules")
        self.showMaximized()
        self.api = api

        # Navigator for displaying schedules
        self.navigator = Navigator(schedules)

        # Buttons
        self.export_button = QPushButton("Export to TXT File")
        self.export_button.setFixedSize(150, 50)  # Set fixed size for export button

        self.back_button = QPushButton("Back to Course Selection")
        self.back_button.setFixedSize(150, 50)  # Set fixed size for back button

        # Connect button signals to their respective slots
        self.export_button.clicked.connect(self.export_to_file)
        self.back_button.clicked.connect(self.navigateToCourseWindow)

        # Layouts
        main_layout = QVBoxLayout()  # Main vertical layout
        buttons_layout = QHBoxLayout()  # Horizontal layout for buttons

        # Add buttons to the layout with spacing and alignment
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addSpacing(20)
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addStretch()

        # Add navigator and button layout to the main layout
        main_layout.addWidget(self.navigator)
        main_layout.addLayout(buttons_layout)

        # Set the main layout as the central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Callback for navigating back to the course selection window
        self.on_back: Callable[[], None] = lambda: None

    def displaySchedules(self, schedules: List[Schedule]):
        """
        Updates the navigator with new schedules and displays the first one.

        Args:
            schedules (List[Schedule]): List of schedules to display.
        """
        self.navigator.schedules = schedules
        self.navigator.display_schedule(0)

    def navigateToCourseWindow(self):
        """
        Triggers the callback to navigate back to the course selection window.
        """
        self.on_back()

    def export_to_file(self):
        """
        Opens a file dialog and saves the schedules to the selected file.
        """
        # Open a file dialog to select the save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Schedules", "", "Text Files (*.txt)"
        )
        if file_path:
            try:
                # Use the API to export schedules to the selected file
                self.api.export(self.navigator.schedules, file_path)
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
