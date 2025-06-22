from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
from src.models.time_slot import TimeSlot

class TimeConstraintTable(QTableWidget):
    cell_toggled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        self.setRowCount(12)
        self.setVerticalHeaderLabels([f"{hour}:00-{hour+1}:00" for hour in range(8, 20)])

        self.setSelectionMode(QTableWidget.NoSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.verticalHeader().setDefaultSectionSize(38)
        self.setMinimumSize(900, 500)
        self.setShowGrid(True)

        self.forbidden = set()
        self.preferred = set()
        self.mark_mode = 'forbidden'  # 'forbidden' or 'preferred'

        self.dragging = False
        self.drag_mode = None
        self.drag_start_cell = None

        self.cellPressed.connect(self._start_drag)
        self.cellEntered.connect(self._drag_enter_cell)
        self.setMouseTracking(True)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.dragging:
            self.dragging = False
            self.drag_mode = None
            self.drag_start_cell = None

    def _start_drag(self, row, col):
        key = (row, col)
        self.dragging = True
        self.drag_start_cell = key
        if self.mark_mode == 'forbidden':
            self.drag_mode = 'remove' if key in self.forbidden else 'add'
        else:
            self.drag_mode = 'remove' if key in self.preferred else 'add'
        self._set_cell(row, col, self.drag_mode)

    def _drag_enter_cell(self, row, col):
        if self.dragging and self.drag_mode:
            self._set_cell(row, col, self.drag_mode)

    def _set_cell(self, row, col, mode):
        key = (row, col)

        if self.mark_mode == 'forbidden':
            if mode == 'add' and key not in self.forbidden:
                self.forbidden.add(key)
                self.preferred.discard(key)
                self._color_cell(row, col, QColor(255, 105, 97, 160))  # red
                self.cell_toggled.emit()
            elif mode == 'remove' and key in self.forbidden:
                self.forbidden.remove(key)
                self.clear_cell(row, col)
                self.cell_toggled.emit()

        elif self.mark_mode == 'preferred':
            if mode == 'add' and key not in self.preferred:
                self.preferred.add(key)
                self.forbidden.discard(key)
                self._color_cell(row, col, QColor(144, 238, 144, 160))  # green
                self.cell_toggled.emit()
            elif mode == 'remove' and key in self.preferred:
                self.preferred.remove(key)
                self.clear_cell(row, col)
                self.cell_toggled.emit()

    def _color_cell(self, row, col, color: QColor):
        item = QTableWidgetItem("")
        item.setBackground(QBrush(color))
        item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row, col, item)

    def clear_cell(self, row, col):
        self.setItem(row, col, QTableWidgetItem(""))

    def set_forbidden_cell(self, row, col):
        key = (row, col)
        self.forbidden.add(key)
        self.preferred.discard(key)
        self._color_cell(row, col, QColor(255, 105, 97, 160))

    def set_preferred_cell(self, row, col):
        key = (row, col)
        self.preferred.add(key)
        self.forbidden.discard(key)
        self._color_cell(row, col, QColor(144, 238, 144, 160))

    def clear_constraints(self):
        self.forbidden.clear()
        self.preferred.clear()
        self.clearContents()

    def eventFilter(self, source, event):
        if self.dragging and event.type() == event.MouseMove and source is self.viewport():
            index = self.indexAt(event.pos())
            if index.isValid():
                self._drag_enter_cell(index.row(), index.column())
        return super().eventFilter(source, event)

    def get_forbidden_timeslots(self):
        return self._convert_to_timeslots(self.forbidden)

    def get_preferred_timeslots(self):
        return self._convert_to_timeslots(self.preferred)

    def _convert_to_timeslots(self, cell_set):
        slots = []
        for row, col in cell_set:
            day_index = str(col + 1)  # Sunday=1
            start_time = f"{8+row:02d}:00"
            end_time = f"{8+row+1:02d}:00"
            slots.append(TimeSlot(day=day_index, start_time=start_time, end_time=end_time, room="", building=""))
        return slots
