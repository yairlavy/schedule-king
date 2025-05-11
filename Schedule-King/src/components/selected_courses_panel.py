from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from typing import List
from src.models.course import Course

class SelectedCoursesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create label
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
        
        layout.addWidget(self.label)

    def update_selection(self, selected_courses: List[Course]):
        if selected_courses:
            course_lines = [
                f"<b>{course.course_code}</b>: {course.name} <i>({course.instructor})</i>"
                for course in selected_courses
            ]
            self.label.setText("<br><br>".join(course_lines))
        else:
            self.label.setText("<b>Selected Courses:</b>")

    def clear(self):
        self.label.setText("<b>Selected Courses:</b>") 