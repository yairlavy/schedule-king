from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout,
    QHBoxLayout, QWidget, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from typing import List, Callable
from src.models.course import Course
from src.components.course_selector import CourseSelector
import os


class CourseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Courses")

        # Set full-screen display
        self.showMaximized()

        # Set custom icon
        icon_path = os.path.join(os.path.dirname(__file__), "../../assets/schedule_icon.png")
        self.setWindowIcon(QIcon(icon_path))

        # === Course Selector ===
        self.courseSelector = CourseSelector()
        self.courseSelector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Connect signals
        self.courseSelector.coursesSubmitted.connect(self.navigateToSchedulesWindow)
        self.courseSelector.loadRequested.connect(self.load_courses_from_file)

        # === Layout Setup ===
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(50, 30, 50, 30)
        outer_layout.setSpacing(20)

        # Add courseSelector directly without extra stretching
        outer_layout.addWidget(self.courseSelector)

        # Wrap in container
        container = QWidget()
        container.setLayout(outer_layout)
        self.setCentralWidget(container)

        # External callbacks
        self.on_courses_loaded: Callable[[str], None] = lambda path: None
        self.on_continue: Callable[[List[Course]], None] = lambda selected: None

    def displayCourses(self, courses: List[Course]):
        self.courseSelector.populate_courses(courses)

    def handleSelection(self) -> List[Course]:
        return self.courseSelector.get_selected_courses()

    def navigateToSchedulesWindow(self):
        selected = self.handleSelection()
        if selected:
            self.on_continue(selected)

    def load_courses_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Course File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.on_courses_loaded(file_path)
