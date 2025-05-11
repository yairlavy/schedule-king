from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush
from src.models.schedule import Schedule

class ScheduleTable(QTableWidget):
    """
    A custom table widget for displaying schedules in a grid format.
    
    Features:
    - Grid layout with days as columns and time slots as rows
    - Color-coded events for different types of classes
    - Custom styling for better readability
    - Tooltips with detailed event information
    """
    def __init__(self):
        super().__init__()
        # --- TABLE STRUCTURE ---
        # Set up 6 columns for days (Sunday to Friday)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        
        # Set up 12 rows for time slots (8:00 to 19:00)
        self.setRowCount(12)
        self.setWordWrap(True)  # Enable text wrapping in cells
        
        # Create time slot labels (8:00-9:00, 9:00-10:00, etc.)
        time_labels = [f"{hour}:00-{hour + 1}:00" for hour in range(8, 20)]
        self.setVerticalHeaderLabels(time_labels)
        
        # --- TABLE APPEARANCE ---
        # Configure grid and visual settings
        self.setShowGrid(True)  # Show grid lines
        self.setGridStyle(Qt.DotLine)  # Use dotted lines for grid
        self.setAlternatingRowColors(True)  # Alternate row colors for readability
        
        # Configure horizontal header (days)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns to fit width
        header.setDefaultAlignment(Qt.AlignCenter)  # Center day names
        header.setFixedHeight(70)  # Fixed height for day headers
        
        # Configure vertical header (time slots)
        vertical_header = self.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.Fixed)  # Fixed width for time column
        vertical_header.setDefaultSectionSize(100)  # Fixed height for time slots
        vertical_header.setFixedWidth(120)  # Fixed width for time column
        
        # --- TABLE BEHAVIOR ---
        # Configure selection and editing behavior
        self.setSelectionMode(QTableWidget.SingleSelection)  # Single cell selection
        self.setSelectionBehavior(QTableWidget.SelectItems)  # Select individual items
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable cell editing
        
        # Set minimum size to ensure visibility
        self.setMinimumSize(900, 600)
        
        # --- EVENT STYLING ---
        # Define colors for different event types with transparency
        self.event_colors = {
            "Lecture": QColor(173, 216, 230, 180),  # Light blue for lectures
            "Tirgul": QColor(255, 218, 185, 180),   # Peach for tirguls
            "Maabada": QColor(144, 238, 144, 180)   # Light green for labs
        }

    def display_schedule(self, schedule: Schedule):
        """
        Populate the table with schedule data.
        
        This method:
        1. Clears existing content
        2. Groups events by day
        3. Creates styled cells for each event
        4. Adds tooltips with event details
        
        Args:
            schedule (Schedule): The schedule object containing events to display.
        """
        # Clear existing content
        self.clearContents()
        
        # Get events grouped by day
        day_map = schedule.extract_by_day()

        # Process each day's events
        for day_str, events in day_map.items():
            # Convert day string to column index (0-based)
            day = int(day_str) - 1
            
            # Process each event in the day
            for event_type, course_name, code, slot in events:
                # Calculate row based on event start time
                row = slot.start_time.hour - 8
                
                # Determine event styling based on type
                if "Lecture" in event_type:
                    event_class = "Lecture"
                    border_color = "#1976D2"  # Blue border for lectures
                elif "Maabada" in event_type:
                    event_class = "Maabada"
                    border_color = "#4CAF50"  # Green border for labs
                else:
                    event_class = "Tirgul"
                    border_color = "#FF9800"  # Orange border for others
                
                # Get background color for this event type
                bg_color = self.event_colors.get(event_class, QColor(240, 240, 240, 180))
                
                # Create HTML content for the cell
                item_text = (
                    f'<div style="padding: 2px;">'
                    f'<div style="font-size: 18px; font-weight: bold; color: #333;">{course_name} ({code})</div>'
                    f'<div style="color: #555; font-size: 18px;">Room: {slot.room} | Building: {slot.building}</div>'
                    f'</div>'
                )
                
                # Create tooltip with plain text
                tooltip_text = f"{course_name} ({code})\nRoom: {slot.room} | Building: {slot.building}"
                
                # Create table item with metadata
                item = QTableWidgetItem()
                item.setData(Qt.UserRole, f"{event_class}|{code}")  # Store event type and code
                item.setToolTip(tooltip_text)
                
                # Add item to table
                self.setItem(row, day, item)
                
                # Create styled label for the cell
                label = QLabel(item_text)
                label.setObjectName(f"course_label_{event_class}")
                label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                label.setWordWrap(True)
                label.setContentsMargins(8, 8, 8, 8)
                
                # Apply custom styling to the label
                label.setStyleSheet(f"""
                    QLabel {{
                        background-color: {bg_color.name(QColor.HexArgb)};
                        border-left: 4px solid {border_color};
                        border-radius: 4px;
                        padding: 3px;
                    }}
                """)
                
                # Set the label as the cell widget
                self.setCellWidget(row, day, label)

        # Set fixed row heights for consistency
        for row in range(self.rowCount()):
            self.setRowHeight(row, 100)