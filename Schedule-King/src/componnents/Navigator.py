# navigator.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from src.componnents.ScheduleTable import ScheduleTable
from src.models.schedule import Schedule
from typing import List

class Navigator(QWidget):
    schedule_changed = pyqtSignal(int)

    def __init__(self, schedules: List[Schedule]):
        super().__init__()
        self.schedules = schedules
        self.current_index = 0

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Controls layout
        controls_layout = QHBoxLayout()

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setFixedSize(150, 50)

        self.schedule_label = QLabel("Schedule #:")
        self.schedule_num = QLineEdit()
        self.schedule_num.setPlaceholderText("Enter schedule number")
        self.schedule_num.setFixedSize(100, 50)

        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedSize(150, 50)

        controls_layout.addWidget(self.prev_btn)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.schedule_label)
        controls_layout.addWidget(self.schedule_num)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.next_btn)
        controls_layout.setAlignment(Qt.AlignCenter)

        # Connections
        self.prev_btn.clicked.connect(self.go_to_previous)
        self.next_btn.clicked.connect(self.go_to_next)
        self.schedule_num.returnPressed.connect(self.on_schedule_num_entered)

        # Table
        self.table = ScheduleTable()

        # Add to layout
        self.layout.addLayout(controls_layout)
        self.layout.addWidget(self.table)

        # Initial display
        self.display_schedule(self.current_index)

    def display_schedule(self, index: int):
        if 0 <= index < len(self.schedules):
            self.current_index = index
            self.table.display_schedule(self.schedules[index])
            self.schedule_num.setText(str(index + 1))
            self.schedule_changed.emit(index)

    def go_to_next(self):
        if self.current_index + 1 < len(self.schedules):
            self.display_schedule(self.current_index + 1)

    def go_to_previous(self):
        if self.current_index - 1 >= 0:
            self.display_schedule(self.current_index - 1)

    def on_schedule_num_entered(self):
        try:
            index = int(self.schedule_num.text()) - 1
            if 0 <= index < len(self.schedules):
                self.display_schedule(index)
            else:
                self.schedule_num.setText(str(self.current_index + 1))
        except ValueError:
            self.schedule_num.setText(str(self.current_index + 1))
