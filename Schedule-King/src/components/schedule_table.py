# schedule_table.py

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from src.models.schedule import Schedule
from collections import defaultdict

class ScheduleTable(QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri"])
        self.setRowCount(12)  # נניח 8:00–20:00
        self.setWordWrap(True)

    def display_schedule(self, schedule: Schedule):
        self.clearContents()
        day_map = schedule.extract_by_day()

        for day_str, events in day_map.items():
            day = int(day_str) - 1  # 1 = Sunday → 0
            for event_type, course_name, code, slot in events:
                row = slot.start_time.hour - 8  # שורות מ-8:00

                item_text = (
                    f"{event_type}\n"
                    f"{course_name} ({code})\n"
                    f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}\n"
                    f"Room {slot.room}, Bldg {slot.building}"
                )

                item = QTableWidgetItem(item_text)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                item.setToolTip(item_text)

                self.setItem(row, day, item)

        self.resizeRowsToContents()
