# schedule_table.py

from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush, QLinearGradient
from src.models.schedule import Schedule
import hashlib

class ScheduleTable(QTableWidget):
    def __init__(self):
        super().__init__()
        # Set the number of columns to represent days of the week (Sunday to Friday)
        self.setColumnCount(6)
        # Set the column headers to the days of the week
        self.setHorizontalHeaderLabels(["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        # Set the number of rows to represent time slots (e.g., 12 rows for 12 hours)
        self.setRowCount(12)
        # Enable word wrapping for table cells
        self.setWordWrap(True)
        # Set the vertical labels to represent time slots (e.g., 8:00-9:00, 9:00-10:00, etc.)
        time_labels = [f"{hour}:00-{hour + 1}:00" for hour in range(8, 20)]
        self.setVerticalHeaderLabels(time_labels)
        
        # Configure table appearance
        self.setShowGrid(True)
        self.setGridStyle(Qt.DotLine)
        self.setAlternatingRowColors(True)
        
        # Set header properties
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setFixedHeight(70)  # Further increased header height
        
        vertical_header = self.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.Fixed)
        vertical_header.setDefaultSectionSize(150)  # Further increased default row height
        vertical_header.setFixedWidth(160)  # Made the time column even wider
        
        # Set table properties
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setSelectionBehavior(QTableWidget.SelectItems)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set minimum size
        self.setMinimumSize(900, 600)
        
        # Dict to store course colors
        self.course_colors = {}

    def get_color_for_course(self, course_code):
        """
        Generate a consistent color for a course based on its code.
        
        Args:
            course_code (str): The course code to generate a color for.
            
        Returns:
            QColor: A color specific to this course.
        """
        if course_code in self.course_colors:
            return self.course_colors[course_code]
            
        # Generate a hash from the course code
        hash_object = hashlib.md5(course_code.encode())
        hex_dig = hash_object.hexdigest()
        
        # Use the first 6 characters of the hash as a color
        color_hex = hex_dig[:6]
        
        # Create a color that's not too dark (for readability)
        r = min(int(color_hex[0:2], 16) + 100, 255)
        g = min(int(color_hex[2:4], 16) + 100, 255)
        b = min(int(color_hex[4:6], 16) + 100, 255)
        
        # Store and return the color
        self.course_colors[course_code] = QColor(r, g, b, 100)  # Semi-transparent
        return self.course_colors[course_code]


    def display_schedule(self, schedule: Schedule):
        """
        Populate the table with schedule data.

        Args:
            schedule (Schedule): The schedule object containing events to display.
        """
        # Clear the table contents and course colors cache before populating it
        self.course_colors = {}
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

                # Create a table widget item with the event details
                item = QTableWidgetItem()
                
                # Get a unique color for this course
                course_color = self.get_color_for_course(code)
                
                # Apply a gradient background based on the event type
                gradient = QLinearGradient(0, 0, 0, 100)
                
                # Base color from course
                gradient.setColorAt(0, course_color)
                
                # Set the background brush with the gradient
                item.setBackground(QBrush(gradient))
                
                # Determine border color based on event type
                if "Lecture" in event_type:
                    border_color = QColor("#1976D2")  # Blue border for lectures
                    event_class = "Lecture"
                elif "Lab" in event_type:
                    border_color = QColor("#4CAF50")  # Green border for labs
                    event_class = "Lab"
                else:
                    border_color = QColor("#FF9800")  # Orange border for others
                    event_class = "Tirgul"

                # Format the cell text with improved styling and layout
                item_text = (
                    f'<div style="padding: 1px; font-family: Arial, sans-serif;">'
                    f'<div style="font-size: 14px; font-weight: bold; color: #333; margin-bottom: 4px;">{course_name} ({code})</div>'
                    f'<div style="color: #777; font-size: 16px; margin-top: 8px;">Room: {slot.room} | Building: {slot.building}</div>'
                    f'</div>'
                )
                
                # Set formatted text
                item.setData(Qt.DisplayRole, "")  # Clear default text
                item.setData(Qt.UserRole, f"{event_type}|{code}")  # Store type and code
                
                # Use HTML formatting for rich text display
                item.setToolTip(item_text.replace("<div", "").replace("</div>", "\n").replace(" style=\"[^\"]*\"", ""))
                
                # Add the item to the table at the calculated row and day column
                self.setItem(row, day, item)
                
                # Create a QLabel with HTML content for each cell
                from PyQt5.QtWidgets import QLabel
                label = QLabel(item_text)
                label.setObjectName(f"course_label_{event_class}_{code}")
                label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                label.setWordWrap(True)
                label.setContentsMargins(14, 14, 14, 14)
                label.setStyleSheet("""
                    QLabel {
                        padding: 8px;
                        line-height: 1.6;
                    }
                """)
                
                # Set the cell widget
                self.setCellWidget(row, day, label)

        # Adjust row heights to fit the content
        self.resizeRowsToContents()
        
        # Set minimum row height
        for row in range(self.rowCount()):
            self.setRowHeight(row, max(150, self.rowHeight(row)))  # Further increased minimum row height