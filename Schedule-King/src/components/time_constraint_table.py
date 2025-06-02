from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from src.models.time_slot import TimeSlot

class TimeConstraintTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        self.setRowCount(12)
        self.setVerticalHeaderLabels([f"{hour}:00-{hour+1}:00" for hour in range(8, 20)])
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

        # Store forbidden cells as set of (row, col)
        self.forbidden = set()

        # Adjust look
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(38)

        self.setMinimumSize(900, 500)
        self.setShowGrid(True)

        # Connect click handler
        self.cellClicked.connect(self.toggle_constraint)

    def toggle_constraint(self, row, col):
        """Toggle forbidden/allowed state visually and in self.forbidden"""
        key = (row, col)
        if key in self.forbidden:
            self.forbidden.remove(key)
            self.setItem(row, col, QTableWidgetItem(""))  # Clear cell
        else:
            self.forbidden.add(key)
            item = QTableWidgetItem("")
            item.setBackground(QBrush(QColor(255, 105, 97, 160)))  # Soft red
            item.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, col, item)

    def set_forbidden_cell(self, row, col):
        """Set a cell as forbidden without toggling (for initialization)"""
        key = (row, col)
        self.forbidden.add(key)
        item = QTableWidgetItem("")
        item.setBackground(QBrush(QColor(255, 105, 97, 160)))  # Soft red
        item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, col, item)

    def clear_constraints(self):
        """Clear all constraints visually and internally"""
        self.forbidden.clear()
        self.clearContents()

    def get_forbidden_timeslots(self):
        """Export forbidden slots as a list of TimeSlot"""
        slots = []
        for row, col in self.forbidden:
            day_index = col + 1  # Sunday=1
            start_time = f"{8+row:02d}:00"
            end_time   = f"{8+row+1:02d}:00"
            slots.append(TimeSlot(day=str(day_index), start_time=start_time, end_time=end_time, room="", building=""))
        return slots 