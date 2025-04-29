# views/course_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QWidget, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from src.componnents.CourseSelector import CourseSelector
from src.models.course import Course
from typing import List, Callable

class CourseWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Courses")
        self.showMaximized()

        # Course selection list
        self.courseSelector = CourseSelector([])

        # Buttons
        self.load_button = QPushButton("Load Courses")
        self.load_button.setFixedSize(150, 50)

        self.next_button = QPushButton("Generate Schedules")
        self.next_button.setFixedSize(150, 50)

        # Connect signals
        self.load_button.clicked.connect(self.load_courses_from_file)
        self.next_button.clicked.connect(self.navigateToSchedulesWindow)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.load_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.courseSelector)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.next_button, alignment=Qt.AlignCenter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # External callbacks (set by controller)
        self.on_courses_loaded: Callable[[str], None] = lambda path: None
        self.on_continue: Callable[[List[Course]], None] = lambda selected: None

    def displayCourses(self, courses: List[Course]):
        """
        Display courses in the selector.
        """
        self.courseSelector.load_courses(courses)

    def handleSelection(self) -> List[Course]:
        """
        Return selected courses from the selector.
        """
        return self.courseSelector.get_selected_courses()

    def navigateToSchedulesWindow(self):
        """
        Move to the ScheduleWindow with selected courses.
        """
        selected = self.handleSelection()
        self.on_continue(selected)

    def load_courses_from_file(self):
        """
        Open file dialog and load courses.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Course File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.on_courses_loaded(file_path)
