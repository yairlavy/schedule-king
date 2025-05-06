# schedule_table.py

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from src.models.schedule import Schedule
from collections import defaultdict

class ScheduleTable(QTableWidget):
    def __init__(self):
        super().__init__()
        # Set the number of columns to represent days of the week (Sunday to Friday)
        self.setColumnCount(6)
        # Set the column headers to the days of the week
        self.setHorizontalHeaderLabels(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri"])
        # Set the number of rows to represent time slots (e.g., 12 rows for 12 hours)
        self.setRowCount(12)
        # Enable word wrapping for table cells
        self.setWordWrap(True)
        # Set the vertical labels to represent time slots (e.g., 8:00-9:00, 9:00-10:00, etc.)
        time_labels = [f"{hour}:00-{hour + 1}:00" for hour in range(8, 20)]
        self.setVerticalHeaderLabels(time_labels)
        self.setWordWrap(True)

        

    def display_schedule(self, schedule: Schedule):
        """
        Populate the table with schedule data.

        Args:
            schedule (Schedule): The schedule object containing events to display.
        """
        # Clear the table contents before populating it
        self.clearContents()
        # Extract events grouped by day from the schedule
        day_map = schedule.extract_by_day()

        # Iterate through each day and its associated events
        for day_str, events in day_map.items():
            # Convert day string to an integer (0-based index for the table)
            day = int(day_str) - 1
            for event_type, course_name, code, slot in events:
                # Calculate the row index based on the event's start time
                row = slot.start_time.hour - 8

                # Create the text to display in the table cell
                item_text = (
                    f"{event_type}\n"
                    f"{course_name} ({code})\n"
                    f"Room {slot.room}, Bldg {slot.building}"
                )

                # Create a table widget item with the event details
                item = QTableWidgetItem(item_text)
                # Align the text to the top-left corner of the cell
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                # Set a tooltip with the same text for additional context
                item.setToolTip(item_text)

                # Apply styling to the text
                font = item.font()
                font.setBold(True)  # Make the text bold
                font.setPointSize(7)  # Set font size
                item.setFont(font)

                # Add the item to the table at the calculated row and day column
                self.setItem(row, day, item)

        # Adjust row heights to fit the content
        self.resizeRowsToContents()
