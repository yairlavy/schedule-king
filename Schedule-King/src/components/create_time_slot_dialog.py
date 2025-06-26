from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QMessageBox
from PyQt5.QtCore import Qt
from typing import Optional, Tuple

class CreateTimeSlotDialog(QDialog):
    '''Dialog for creating a new time slot block with room, building, and slot type inputs.'''
    def __init__(self, parent=None):
        # Initialize the window of the create time slot dialog 
        super().__init__(parent)
        self.setWindowTitle("Create New Time Slot Block")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.time_slot_data: Optional[Tuple[str, str, str]] = None
        layout = QFormLayout()
        
        # Create input fields for room
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("Example: 101")
        layout.addRow("Room:", self.room_input)
        
        # Create input fields for building
        self.building_input = QLineEdit()
        self.building_input.setPlaceholderText("Example: Engineering")
        layout.addRow("Building:", self.building_input)
        
        # Create combo box dropdown for slot type
        self.type_combo = QComboBox()
        self.type_combo.addItem("Lecture", userData="lecture")
        self.type_combo.addItem("Tirgul", userData="tirgul")
        self.type_combo.addItem("Maabada", userData="maabada")
        layout.addRow("Slot Type:", self.type_combo)
        
        # Create dialog buttons for OK and Cancel
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)

    # Returns the time slot data as a tuple of (room, building, slot_type)
    # or None if the dialog was canceled
    def get_time_slot_data(self) -> Optional[Tuple[str, str, str]]:
        return self.time_slot_data

    # When the user clicks OK, validate inputs and store the time slot data
    # If inputs are invalid, show a warning message
    def accept(self):
        room = self.room_input.text().strip()
        building = self.building_input.text().strip()
        slot_type = self.type_combo.currentData()
        if not (room and building and slot_type):
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
            return
        self.time_slot_data = (room, building, slot_type)
        super().accept()