from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from src.componnents.ScheduleTable import ScheduleTable
from src.models.schedule import Schedule
from typing import List

class Navigator(QWidget):
    # Signal emitted when the schedule changes
    schedule_changed = pyqtSignal(int)

    def __init__(self, schedules: List[Schedule]):
        super().__init__()
        self.schedules = schedules  # List of schedules to navigate
        self.current_index = 0  # Index of the currently displayed schedule

        # Main layout for the widget
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Info label to show the current schedule index and total schedules
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        # Controls layout: previous button, input field, and next button
        controls_layout = QHBoxLayout()

        # Button to navigate to the previous schedule
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setFixedSize(150, 50)

        # Input field to enter a specific schedule number
        self.schedule_num = QLineEdit()
        self.schedule_num.setFixedSize(100, 50)
        self.schedule_num.setPlaceholderText("Go to...")

        # Button to navigate to the next schedule
        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedSize(150, 50)

        # Add controls to the layout
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.schedule_num)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.next_btn)
        controls_layout.setAlignment(Qt.AlignCenter)

        # Connect button clicks and input field to their respective methods
        self.prev_btn.clicked.connect(self.go_to_previous)
        self.next_btn.clicked.connect(self.go_to_next)
        self.schedule_num.returnPressed.connect(self.on_schedule_num_entered)

        # Add the controls layout to the main layout
        self.layout.addLayout(controls_layout)

        # Schedule display table to show the current schedule
        self.table = ScheduleTable()
        self.layout.addWidget(self.table)

        # Display the first schedule by default
        self.display_schedule(0)

    def display_schedule(self, index: int):
        """
        Display the schedule at the given index.
        Updates the table, info label, and input field.
        Emits the schedule_changed signal.
        """
        if 0 <= index < len(self.schedules):
            self.current_index = index
            self.table.display_schedule(self.schedules[index])  # Update the table
            self.schedule_num.setText(str(index + 1))  # Update the input field
            self.info_label.setText(f"Schedule {index + 1} / {len(self.schedules)}")  # Update the info label
            self.schedule_changed.emit(index)  # Emit the signal

    def go_to_next(self):
        """
        Navigate to the next schedule if it exists.
        """
        if self.current_index + 1 < len(self.schedules):
            self.display_schedule(self.current_index + 1)

    def go_to_previous(self):
        """
        Navigate to the previous schedule if it exists.
        """
        if self.current_index - 1 >= 0:
            self.display_schedule(self.current_index - 1)

    def on_schedule_num_entered(self):
        """
        Handle the event when the user enters a schedule number in the input field.
        Validates the input and navigates to the corresponding schedule.
        """
        try:
            index = int(self.schedule_num.text()) - 1  # Convert input to zero-based index
            if 0 <= index < len(self.schedules):
                self.display_schedule(index)  # Display the schedule if valid
            else:
                # Show a warning if the number is out of range
                QMessageBox.warning(
                    self,
                    "Invalid Schedule Number",
                    f"Please enter a number between 1 and {len(self.schedules)}."
                )
                self.schedule_num.setText(str(self.current_index + 1))  # Reset input field
        except ValueError:
            # Show a warning if the input is not a valid number
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a valid number."
            )
            self.schedule_num.setText(str(self.current_index + 1))  # Reset input field
