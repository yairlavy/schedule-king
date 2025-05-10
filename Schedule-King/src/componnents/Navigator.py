from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List
from src.models.schedule import Schedule

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
        self.info_label.setObjectName("info_label")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        # Controls layout: previous button, input field, and next button
        controls_layout = QHBoxLayout()

        # Button to navigate to the previous schedule
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setFixedSize(150, 50)

        # Input field to enter a specific schedule number
        self.schedule_num = QLineEdit()
        self.schedule_num.setObjectName("schedule_num")
        self.schedule_num.setFixedSize(100, 50)
        self.schedule_num.setPlaceholderText("Go to...")
        self.schedule_num.setAlignment(Qt.AlignCenter)

        # Button to navigate to the next schedule
        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedSize(150, 50)

        # Add controls to the layout
        controls_layout.addStretch(1)
        controls_layout.addWidget(self.prev_btn)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(self.schedule_num)
        controls_layout.addSpacing(20)
        controls_layout.addWidget(self.next_btn)
        controls_layout.addStretch(1)
        controls_layout.setAlignment(Qt.AlignCenter)

        # Connect button clicks and input field to their respective methods
        self.prev_btn.clicked.connect(self.go_to_previous)
        self.next_btn.clicked.connect(self.go_to_next)
        self.schedule_num.returnPressed.connect(self.on_schedule_num_entered)

        # Add the controls layout to the main layout
        self.layout.addLayout(controls_layout)
        
        # Add a separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setObjectName("separator_line")
        self.layout.addWidget(line)
        
        # Update the display
        self.update_display()

    def update_display(self):
        """
        Updates the info label and input field based on the current index.
        """
        if self.schedules:
            self.info_label.setText(f"Schedule {self.current_index + 1} / {len(self.schedules)}")
            self.schedule_num.setText(str(self.current_index + 1))
        else:
            self.info_label.setText("No schedules available")
            self.schedule_num.setText("")

    def go_to_next(self):
        """
        Navigate to the next schedule if it exists.
        """
        if self.current_index + 1 < len(self.schedules):
            self.current_index += 1
            self.update_display()
            self.schedule_changed.emit(self.current_index)

    def go_to_previous(self):
        """
        Navigate to the previous schedule if it exists.
        """
        if self.current_index - 1 >= 0:
            self.current_index -= 1
            self.update_display()
            self.schedule_changed.emit(self.current_index)

    def on_schedule_num_entered(self):
        """
        Handle the event when the user enters a schedule number in the input field.
        Validates the input and navigates to the corresponding schedule.
        """
        try:
            index = int(self.schedule_num.text()) - 1  # Convert input to zero-based index
            if 0 <= index < len(self.schedules):
                self.current_index = index
                self.update_display()
                self.schedule_changed.emit(self.current_index)
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

    def set_schedules(self, schedules: List[Schedule]):
        """
        Set new schedules and reset the current index.
        """
        self.schedules = schedules
        self.current_index = 0 if schedules else -1
        self.update_display()
        if self.schedules:
            self.schedule_changed.emit(self.current_index)

    def get_current_schedule(self):
        """
        Get the currently selected schedule.
        
        Returns:
            Schedule or None: The current schedule, or None if no schedules are available.
        """
        if 0 <= self.current_index < len(self.schedules):
            return self.schedules[self.current_index]
        return None