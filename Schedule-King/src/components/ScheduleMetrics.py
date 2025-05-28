from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from src.models.schedule import Schedule

class ScheduleMetrics(QFrame):
    def __init__(self, schedule: Schedule, parent=None):
        super().__init__(parent)
        self.schedule = schedule
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(2)  
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("Schedule Metrics")
        title.setFont(QFont("Arial", 8, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(self._create_metric_label("Active Days", self.schedule.active_days))
        layout.addWidget(self._create_metric_label("Gap Count", self.schedule.gap_count))
        layout.addWidget(self._create_metric_label("Total Gap Time (min)", self.schedule.total_gap_time))
        layout.addWidget(self._create_metric_label("Average Start Time", self._format_time(self.schedule.avg_start_time)))
        layout.addWidget(self._create_metric_label("Average End Time", self._format_time(self.schedule.avg_end_time)))

        self.setLayout(layout)
        self.setFixedWidth(200) 
        self.setStyleSheet("""
            ScheduleMetrics {
                background-color: #007BFF;
                color: black;
                border-radius: 10px;
            }
            QLabel {
                color: black;
                font-size: 10pt;
            }
        """)

    def _create_metric_label(self, name, value):
        label = QLabel(f"{name}: {value}")
        label.setFont(QFont("Arial", 9))
        return label

    def _format_time(self, minutes: float) -> str:
        if minutes == 0:
            return "N/A"
        h = int(minutes) // 60
        m = int(minutes) % 60
        return f"{h:02}:{m:02}"
