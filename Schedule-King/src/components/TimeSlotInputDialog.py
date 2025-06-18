from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox,
    QTimeEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QTime
from src.models.time_slot import TimeSlot
from datetime import time
from typing import Optional

class TimeSlotInputDialog(QDialog):
    def __init__(self, parent=None, initial_time_slot: TimeSlot = None):
        super().__init__(parent)
        self.setWindowTitle("Add Time Slot")
        # Remove the help button from the dialog window
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self.time_slot_data = None

        layout = QFormLayout()

        # Day selection dropdown
        self.day_combo = QComboBox()
        # Map display day names to numeric string values
        self.day_map = {
            "Sunday": "1", "Monday": "2", "Tuesday": "3",
            "Wednesday": "4", "Thursday": "5", "Friday": "6", "Saturday": "7"
        }
        for display_day in self.day_map.keys():
            self.day_combo.addItem(display_day)
        layout.addRow("Day:", self.day_combo)

        # Start Time input (defaults to 08:00)
        self.start_time_edit = QTimeEdit(QTime(8, 0))
        self.start_time_edit.setDisplayFormat("HH:mm")
        layout.addRow("Start Time:", self.start_time_edit)

        # End Time input (defaults to 09:00)
        self.end_time_edit = QTimeEdit(QTime(9, 0))
        self.end_time_edit.setDisplayFormat("HH:mm")
        layout.addRow("End Time:", self.end_time_edit)

        # Room input field
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("Example: 101")
        layout.addRow("Room:", self.room_input)

        # Building input field
        self.building_input = QLineEdit()
        self.building_input.setPlaceholderText("Example: Engineering")
        layout.addRow("Building:", self.building_input)

        # If editing an existing time slot, populate fields with its data
        if initial_time_slot:
            self._populate_fields(initial_time_slot)

        # Dialog buttons (OK and Cancel)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def _populate_fields(self, time_slot: TimeSlot):
        # Set the day dropdown to the correct value based on the time slot's day
        day_display = next((key for key, value in self.day_map.items() if value == time_slot.day), None)
        if day_display:
            self.day_combo.setCurrentText(day_display)
        
        # Set start and end times
        self.start_time_edit.setTime(QTime(time_slot.start_time.hour, time_slot.start_time.minute))
        self.end_time_edit.setTime(QTime(time_slot.end_time.hour, time_slot.end_time.minute))
        # Set room and building fields
        self.room_input.setText(time_slot.room)
        self.building_input.setText(time_slot.building)

    def get_time_slot_data(self) -> Optional[TimeSlot]:
        # Return the time slot data after dialog is accepted
        return self.time_slot_data

    def accept(self):
        # Gather input values from the dialog
        selected_day_display = self.day_combo.currentText()
        day = self.day_map.get(selected_day_display)
        start_time_str = self.start_time_edit.time().toString("HH:mm")
        end_time_str = self.end_time_edit.time().toString("HH:mm")
        room = self.room_input.text().strip()
        building = self.building_input.text().strip()

        # Validate that all fields are filled
        if not day or not start_time_str or not end_time_str or not room or not building:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return

        try:
            # Validate that start time is before end time
            start_time_obj = QTime.fromString(start_time_str, "HH:mm")
            end_time_obj = QTime.fromString(end_time_str, "HH:mm")
            if start_time_obj >= end_time_obj:
                QMessageBox.warning(self, "Time Error", "Start time must be before end time.")
                return

            # Create a TimeSlot object and store it in a list
            # (wrapped in a list for compatibility with ALL_STRATEGY)
            self.time_slot_data = [TimeSlot(
                day=day,
                start_time=start_time_str,
                end_time=end_time_str,
                room=room,
                building=building
            )]
            super().accept()
        except Exception as e:
            # Show error message if something goes wrong
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            self.time_slot_data = None
            super().reject()