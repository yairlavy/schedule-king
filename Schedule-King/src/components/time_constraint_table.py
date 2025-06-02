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

        self.forbidden = set()

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(38)

        self.setMinimumSize(900, 500)
        self.setShowGrid(True)

        # Dragging state
        self.dragging = False
        self.drag_mode = None  # 'add' or 'remove'
        self.drag_start_cell = None

        # Mouse event hooks
        self.cellPressed.connect(self._start_drag)
        self.cellEntered.connect(self._drag_enter_cell)
        self.cellReleased = False

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.dragging:
            self.dragging = False
            self.drag_mode = None
            self.drag_start_cell = None

    def _start_drag(self, row, col):
        key = (row, col)
        self.dragging = True
        self.drag_start_cell = (row, col)
        # Decide mode: add or remove
        self.drag_mode = 'remove' if key in self.forbidden else 'add'
        # Apply to first cell
        self._set_cell(row, col, self.drag_mode)

        # Enable cellEntered events while dragging
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        # To trigger cellEntered even when mouse button held
        self.viewport().installEventFilter(self)

    def _drag_enter_cell(self, row, col):
        if self.dragging and self.drag_mode:
            self._set_cell(row, col, self.drag_mode)

    def _set_cell(self, row, col, mode):
        key = (row, col)
        if mode == 'add':
            if key not in self.forbidden:
                self.forbidden.add(key)
                item = QTableWidgetItem("")
                item.setBackground(QBrush(QColor(255, 105, 97, 160)))
                item.setTextAlignment(Qt.AlignCenter)
                self.setItem(row, col, item)
        elif mode == 'remove':
            if key in self.forbidden:
                self.forbidden.remove(key)
                self.setItem(row, col, QTableWidgetItem(""))

    def set_forbidden_cell(self, row, col):
        key = (row, col)
        self.forbidden.add(key)
        item = QTableWidgetItem("")
        item.setBackground(QBrush(QColor(255, 105, 97, 160)))
        item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, col, item)

    def clear_constraints(self):
        self.forbidden.clear()
        self.clearContents()

    def get_forbidden_timeslots(self):
        slots = []
        for row, col in self.forbidden:
            day_index = col + 1  # Sunday=1
            start_time = f"{8+row:02d}:00"
            end_time = f"{8+row+1:02d}:00"
            slots.append(TimeSlot(day=str(day_index), start_time=start_time, end_time=end_time, room="", building=""))
        return slots

    # Add this to ensure cellEntered works even during drag
    def eventFilter(self, source, event):
        if self.dragging and event.type() == event.MouseMove and source is self.viewport():
            index = self.indexAt(event.pos())
            if index.isValid():
                self._drag_enter_cell(index.row(), index.column())
        return super().eventFilter(source, event)
