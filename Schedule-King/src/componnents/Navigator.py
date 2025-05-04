from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox
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

        # Info label to show "Schedule X / Y"
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.info_label)

        # Controls: previous, input, next
        controls_layout = QHBoxLayout()

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.setFixedSize(150, 50)

        self.schedule_num = QLineEdit()
        self.schedule_num.setFixedSize(100, 50)
        self.schedule_num.setPlaceholderText("Go to...")

        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedSize(150, 50)

        controls_layout.addWidget(self.prev_btn)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.schedule_num)
        controls_layout.addSpacing(10)
        controls_layout.addWidget(self.next_btn)
        controls_layout.setAlignment(Qt.AlignCenter)

        self.prev_btn.clicked.connect(self.go_to_previous)
        self.next_btn.clicked.connect(self.go_to_next)
        self.schedule_num.returnPressed.connect(self.on_schedule_num_entered)

        self.layout.addLayout(controls_layout)

        # Schedule display table
        self.table = ScheduleTable()
        self.layout.addWidget(self.table)

        self.display_schedule(0)

    def display_schedule(self, index: int):
        if 0 <= index < len(self.schedules):
            self.current_index = index
            self.table.display_schedule(self.schedules[index])
            self.schedule_num.setText(str(index + 1))
            self.info_label.setText(f"Schedule {index + 1} / {len(self.schedules)}")
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
                QMessageBox.warning(
                    self,
                    "Invalid Schedule Number",
                    f"Please enter a number between 1 and {len(self.schedules)}."
                )
                self.schedule_num.setText(str(self.current_index + 1))
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a valid number."
            )
            self.schedule_num.setText(str(self.current_index + 1))
