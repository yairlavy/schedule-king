from PyQt5.QtWidgets import (
    QListWidget, QAbstractItemView, QListWidgetItem, QVBoxLayout,
    QPushButton, QWidget, QHBoxLayout, QSizePolicy, QLabel, QFrame
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from typing import List
from src.models.course import Course

class CourseSelector(QWidget):
    coursesSelected = pyqtSignal(list)
    coursesSubmitted = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Title
        self.title_label = QLabel("Available Courses")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.layout.addWidget(self.separator)

        # Course list
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSpacing(6)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        font = QFont("Segoe UI", 12)
        font.setWeight(QFont.Medium)
        self.list_widget.setFont(font)

        self.layout.addWidget(self.list_widget)

        # Buttons layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)

        self.submit_button = QPushButton("Submit Selection")
        self.submit_button.setCursor(Qt.PointingHandCursor)

        self.clear_button = QPushButton("Clear All")
        self.clear_button.setCursor(Qt.PointingHandCursor)

        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.submit_button)

        self.layout.addLayout(self.button_layout)

        # Internal course list
        self.courses = []

        # Connect signals
        self.list_widget.itemSelectionChanged.connect(self._handle_selection_changed)
        self.submit_button.clicked.connect(self._handle_submit)
        self.clear_button.clicked.connect(self._handle_clear)

    def populate_courses(self, courses: List[Course]):
        self.list_widget.clear()
        self.courses = courses

        for course in courses:
            item = QListWidgetItem(f"{course.course_code} - {course.name}")
            item.setData(Qt.UserRole, self.courses.index(course))
            self.list_widget.addItem(item)

        self.title_label.setText(f"Available Courses ({len(courses)})")

    def _handle_selection_changed(self):
        selected_courses = self.get_selected_courses()
        if selected_courses:
            self.title_label.setText(f"Available Courses ({len(selected_courses)} selected)")
        else:
            self.title_label.setText(f"Available Courses ({len(self.courses)} total)")
        self.coursesSelected.emit(selected_courses)

    def _handle_submit(self):
        selected_courses = self.get_selected_courses()
        self.coursesSubmitted.emit(selected_courses)

    def _handle_clear(self):
        self.list_widget.clearSelection()
        self.title_label.setText(f"Available Courses ({len(self.courses)} total)")
        self.coursesSelected.emit([])

    def get_selected_courses(self) -> List[Course]:
        selected_courses = []
        for item in self.list_widget.selectedItems():
            index = item.data(Qt.UserRole)
            if 0 <= index < len(self.courses):
                selected_courses.append(self.courses[index])
        return selected_courses

    def set_selected_courses(self, course_numbers: List[str]):
        self.list_widget.clearSelection()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            index = item.data(Qt.UserRole)
            if 0 <= index < len(self.courses):
                course = self.courses[index]
                if course.number in course_numbers:
                    item.setSelected(True)
        selected_count = len(self.get_selected_courses())
        if selected_count > 0:
            self.title_label.setText(f"Available Courses ({selected_count} selected)")
