from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from src.models.time_slot import TimeSlot

class TimeConstraintTable(QTableWidget):
    def __init__(self):
        super().__init__()
        # Set up columns for days of the week (Sunday to Friday)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        # Set up rows for time slots (8:00-20:00, 12 slots)
        self.setRowCount(12)
        self.setVerticalHeaderLabels([f"{hour}:00-{hour+1}:00" for hour in range(8, 20)])
        # Disable selection and editing
        self.setSelectionMode(QTableWidget.NoSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

        # Store forbidden cells as a set of (row, col) tuples
        self.forbidden = set()

        # Stretch columns to fill width, fix row height
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(38)

        # Set minimum size and show grid lines
        self.setMinimumSize(900, 500)
        self.setShowGrid(True)

        # Dragging state variables
        self.dragging = False
        self.drag_mode = None  # 'add' or 'remove'
        self.drag_start_cell = None

        # Connect mouse event hooks
        self.cellPressed.connect(self._start_drag)
        self.cellEntered.connect(self._drag_enter_cell)
        self.cellReleased = False  # Not used, but defined

    def mouseReleaseEvent(self, event):
        # Stop dragging when mouse is released
        super().mouseReleaseEvent(event)
        if self.dragging:
            self.dragging = False
            self.drag_mode = None
            self.drag_start_cell = None

    def _start_drag(self, row, col):
        # Start drag operation from a cell
        key = (row, col)
        self.dragging = True
        self.drag_start_cell = (row, col)
        # Decide whether to add or remove forbidden cell
        self.drag_mode = 'remove' if key in self.forbidden else 'add'
        # Apply mode to the first cell
        self._set_cell(row, col, self.drag_mode)

        # Enable mouse tracking for drag
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        # Install event filter to capture mouse move events
        self.viewport().installEventFilter(self)

    def _drag_enter_cell(self, row, col):
        # Called when mouse enters a new cell during drag
        if self.dragging and self.drag_mode:
            self._set_cell(row, col, self.drag_mode)

    def _set_cell(self, row, col, mode):
        # Add or remove a forbidden cell
        key = (row, col)
        if mode == 'add':
            if key not in self.forbidden:
                self.forbidden.add(key)
                item = QTableWidgetItem("")
                # Set background color to indicate forbidden
                item.setBackground(QBrush(QColor(255, 105, 97, 160)))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)
        elif mode == 'remove':
            if key in self.forbidden:
                self.forbidden.remove(key)
                # Clear the cell
                self.setItem(row, col, QTableWidgetItem(""))

    def set_forbidden_cell(self, row, col):
        # Mark a cell as forbidden (used externally)
        key = (row, col)
        self.forbidden.add(key)
        item = QTableWidgetItem("")
        item.setBackground(QBrush(QColor(255, 105, 97, 160)))
        item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, col, item)

    def clear_constraints(self):
        # Clear all forbidden cells
        self.forbidden.clear()
        self.clearContents()

    def get_forbidden_timeslots(self):
        # Return forbidden cells as a list of TimeSlot objects
        slots = []
        for row, col in self.forbidden:
            day_index = col + 1  # Sunday=1
            start_time = f"{8+row:02d}:00"
            end_time = f"{8+row+1:02d}:00"
            slots.append(TimeSlot(day=str(day_index), start_time=start_time, end_time=end_time, room="", building=""))
        return slots

    def eventFilter(self, source, event):
        # Ensure cellEntered works even during drag by handling mouse move events
        if self.dragging and event.type() == event.MouseMove and source is self.viewport():
            index = self.indexAt(event.pos())
            if index.isValid():
                self._drag_enter_cell(index.row(), index.column())
        return super().eventFilter(source, event)
