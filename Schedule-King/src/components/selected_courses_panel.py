from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from typing import List
from src.models.course import Course

class SelectedCoursesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create the main vertical layout for the panel
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create and configure the label that displays selected courses
        self.label = QLabel("<b>Selected Courses:</b>")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignTop)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                border: 1px solid #BBDEFB;
                padding: 12px;
                font-size: 11pt;
                border-radius: 6px;
                color: #0D47A1;
                min-width: 300px;
            }
        """)
        
        # Add the label to the layout
        layout.addWidget(self.label)

    def update_selection(self, selected_courses: List[Course]):
        """
        Update the label to show the currently selected courses.
        If the list is empty, show the default label text.
        """
        if selected_courses:
            # Format each course as a line with code, name, and instructor
            course_lines = [
                f"<b>{course.course_code}</b>: {course.name} <i>({course.instructor})</i>"
                for course in selected_courses
            ]
            # Join all course lines with line breaks and set as label text
            self.label.setText("<br><br>".join(course_lines))
        else:
            # If no courses are selected, show the default text
            self.label.setText("<b>Selected Courses:</b>")

    def clear(self):
        """
        Reset the label to the default text (no courses selected).
        """
        self.label.setText("<b>Selected Courses:</b>") 