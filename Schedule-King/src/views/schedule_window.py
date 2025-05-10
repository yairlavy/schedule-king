# views/schedule_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QMessageBox,
    QSpacerItem, QSizePolicy, QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.components.navigator import Navigator
from src.models.schedule import Schedule
from typing import List, Callable
from src.services.schedule_api import ScheduleAPI

class ScheduleWindow(QMainWindow):
    def __init__(self, schedules: List[Schedule], api: ScheduleAPI):
        super().__init__()
        self.setWindowTitle("Generated Schedules")
        self.showMaximized()
        self.api = api

        self.navigator = Navigator(schedules)

        # Buttons
        self.export_button = QPushButton("Export to TXT File")
        self.export_button.setFixedSize(150, 50)

        self.back_button = QPushButton("Back to Course Selection")
        self.back_button.setFixedSize(150, 50)

        self.export_button.clicked.connect(self.export_to_file)
        self.back_button.clicked.connect(self.navigateToCourseWindow)

        # Layouts
        main_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.export_button)
        buttons_layout.addSpacing(20)
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addStretch()

        main_layout.addWidget(self.navigator)
        main_layout.addLayout(buttons_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.on_back: Callable[[], None] = lambda: None

    def displaySchedules(self, schedules: List[Schedule]):
        self.navigator.schedules = schedules
        self.navigator.display_schedule(0)

    def navigateSchedule(self):
        pass

    def navigateToCourseWindow(self):
        self.on_back()

    def export_to_file(self):
        """
        Opens a file dialog and saves the schedules to the selected file.
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Schedules", "", "Text Files (*.txt)"
        )
        if file_path:
            try:
                self.api.export(self.navigator.schedules, file_path)
                QMessageBox.information(
                    self, "Export Successful",
                    f"Schedules were saved successfully to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Export Failed",
                    f"Failed to export schedules:\n{str(e)}"
                )
