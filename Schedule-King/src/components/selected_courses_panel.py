from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QScrollArea
from PyQt5.QtCore import Qt
from typing import List
from src.models.course import Course

class SelectedCoursesPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # === Outer layout ===
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # === Scroll Area ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # === Inner widget to hold label ===
        inner_widget = QWidget()
        self.inner_layout = QVBoxLayout(inner_widget)
        self.inner_layout.setContentsMargins(0, 0, 0, 0)

        # === Label showing selected courses ===
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
            }
        """)

        self.inner_layout.addWidget(self.label)
        scroll_area.setWidget(inner_widget)
        outer_layout.addWidget(scroll_area)

        # Optionally limit the height so it doesn't expand infinitely
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
