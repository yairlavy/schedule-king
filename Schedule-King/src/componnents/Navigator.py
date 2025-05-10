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
    
   # Update to the Navigator class to show the schedule count below the input field

    def __init__(self, schedules: List[Schedule]):
        """
        Initialize the Navigator widget.

        Args:
            schedules (List[Schedule]): List of schedules to navigate.
        """
        super().__init__()
        self.schedules = schedules  # List of schedules to navigate
        self.current_index = 0  # Index of the currently displayed schedule

        # Main layout for the widget
        self.layout = QHBoxLayout()  # Horizontal layout for more compact design
        self.layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins
        self.layout.setSpacing(10)  # Reduced spacing
        self.setLayout(self.layout)

        # Button to navigate to the previous schedule
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setObjectName("nav_button")
        self.prev_btn.setFixedSize(80, 30)  
        
        # Info label to show the current schedule index and total schedules
        self.info_label = QLabel()
        self.info_label.setObjectName("info_label")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setMinimumWidth(120)  # Set minimum width
        self.info_label.setFixedHeight(35)  # Match button height
        
        # Input field container (vertical layout for input and count label)
        input_container = QVBoxLayout()
        input_container.setSpacing(0)
        input_container.setContentsMargins(0, 0, 0, 0)
        
        # Input field to enter a specific schedule number
        self.schedule_num = QLineEdit()
        self.schedule_num.setObjectName("schedule_num")
        self.schedule_num.setFixedSize(80, 35) 
        self.schedule_num.setPlaceholderText("Go to...")
        self.schedule_num.setAlignment(Qt.AlignCenter)
        
        # Add widgets to the input container
        input_container.addWidget(self.schedule_num)
        
        # Button to navigate to the next schedule
        self.next_btn = QPushButton("Next")
        self.next_btn.setObjectName("nav_button")
        self.next_btn.setFixedSize(80, 30)  

        # Add controls to the horizontal layout
        self.layout.addStretch(1)
        self.layout.addWidget(self.prev_btn)
        self.layout.addWidget(self.info_label)
        self.layout.addLayout(input_container) 
        self.layout.addWidget(self.next_btn)
        self.layout.addStretch(1)
        self.layout.setAlignment(Qt.AlignCenter)

        # Connect button clicks and input field to their respective methods
        self.prev_btn.clicked.connect(self.go_to_previous)
        self.next_btn.clicked.connect(self.go_to_next)
        self.schedule_num.returnPressed.connect(self.on_schedule_num_entered)
        
        # Update the display
        self.update_display()

    def update_display(self):
        """
        Updates the info label and input field based on the current index.
        """
        if self.schedules:
            # Display the current schedule index and total schedules
            self.info_label.setText(f"Schedule {self.current_index + 1} / {len(self.schedules)}")
            self.schedule_num.setText(str(self.current_index + 1))
        else:
            # Display a message if no schedules are available
            self.info_label.setText("No schedules available")
            self.schedule_num.setText("")

    def go_to_next(self):
        """
        Navigate to the next schedule if it exists.
        """
        if self.current_index + 1 < len(self.schedules):
            self.current_index += 1  # Increment the current index
            self.update_display()  # Update the display
            self.schedule_changed.emit(self.current_index)  # Emit the schedule_changed signal

    def go_to_previous(self):
        """
        Navigate to the previous schedule if it exists.
        """
        if self.current_index - 1 >= 0:
            self.current_index -= 1  # Decrement the current index
            self.update_display()  # Update the display
            self.schedule_changed.emit(self.current_index)  # Emit the schedule_changed signal

    def on_schedule_num_entered(self):
        """
        Handle the event when the user enters a schedule number in the input field.
        Validates the input and navigates to the corresponding schedule.
        """
        try:
            # Convert input to zero-based index
            index = int(self.schedule_num.text()) - 1
            if 0 <= index < len(self.schedules):
                # If the index is valid, update the current index
                self.current_index = index
                self.update_display()  # Update the display
                self.schedule_changed.emit(self.current_index)  # Emit the schedule_changed signal
            else:
                # Show a warning if the number is out of range
                QMessageBox.warning(
                    self,
                    "Invalid Schedule Number",
                    f"Please enter a number between 1 and {len(self.schedules)}."
                )
                # Reset input field to the current schedule number
                self.schedule_num.setText(str(self.current_index + 1))
        except ValueError:
            # Show a warning if the input is not a valid number
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a valid number."
            )
            # Reset input field to the current schedule number
            self.schedule_num.setText(str(self.current_index + 1))

    def set_schedules(self, schedules: List[Schedule]):
        """
        Set new schedules and reset the current index.

        Args:
            schedules (List[Schedule]): The new list of schedules.
        """
        self.schedules = schedules
        self.current_index = 0 if schedules else -1  # Reset the current index
        self.update_display()  # Update the display
        if self.schedules:
            self.schedule_changed.emit(self.current_index)  # Emit the schedule_changed signal

    def get_current_schedule(self):
        """
        Get the currently selected schedule.
        
        Returns:
            Schedule or None: The current schedule, or None if no schedules are available.
        """
        if 0 <= self.current_index < len(self.schedules):
            return self.schedules[self.current_index]  # Return the current schedule
        return None  # Return None if no schedules are available