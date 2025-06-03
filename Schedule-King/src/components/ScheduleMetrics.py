from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from src.models.schedule import Schedule

class ScheduleMetrics(QFrame):
    def __init__(self, schedule: Schedule, parent=None):
        """
        Initialize the ScheduleMetrics widget.

        Args:
            schedule (Schedule): The schedule object containing metrics.
            parent: The parent widget (optional).
        """
        super().__init__(parent)
        self.schedule = schedule
        self.setObjectName("ScheduleMetrics")
        self.init_ui()

    def init_ui(self):
        """
        Set up the UI layout and add metric labels.
        """
        layout = QVBoxLayout()
        layout.setSpacing(2)  
        layout.setContentsMargins(10, 10, 10, 10)
        self.setFixedHeight(150)

        # Title label
        title = QLabel("Schedule Metrics")
        title.setObjectName("metrics_title_label")
        title.setFont(QFont("Arial", 8, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Add metric labels
        layout.addWidget(self._create_metric_label("Active Days", self.schedule.active_days, "active_days_label"))
        layout.addWidget(self._create_metric_label("Gap Count", self.schedule.gap_count, "gap_count_label"))
        layout.addWidget(self._create_metric_label("Total Gap Time (hours)", self.schedule.total_gap_time, "total_gap_time_label"))
        layout.addWidget(self._create_metric_label("Average Start Time", self._format_time(self.schedule.avg_start_time), "avg_start_time_label"))
        layout.addWidget(self._create_metric_label("Average End Time", self._format_time(self.schedule.avg_end_time), "avg_end_time_label"))

        self.setLayout(layout)
        self.setFixedWidth(250) 

    def _create_metric_label(self, name, value, obj_name):
        """
        Helper to create a QLabel for a metric.

        Args:
            name (str): The name of the metric.
            value: The value to display.
            obj_name (str): The object name for styling.

        Returns:
            QLabel: The configured label.
        """
        label = QLabel(f"{name}: {value}")
        label.setObjectName(obj_name)
        label.setFont(QFont("Arial", 9))
        return label

    def _format_time(self, time_value: float) -> str:
        """
        Format time from integer format (e.g., 900) to HH:MM.

        Args:
            time_value (float): The time value to format.

        Returns:
            str: The formatted time string.
        """
        if time_value == 0:
            return "N/A"
        
        # Convert the time format (e.g., 900) to total minutes
        total_minutes = Schedule.time_format_to_minutes(int(time_value))

        # Now format the total minutes as HH:MM
        h = total_minutes // 60
        m = total_minutes % 60
        return f"{h:02}:{m:02}"
