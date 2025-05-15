from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout,
    QHBoxLayout, QWidget, QSizePolicy, QMessageBox
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
        self.setWindowTitle("Select Courses")  # Set the window title


        # Set custom icon for the window
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))

        # === Course Selector ===
        # Initialize the course selector component
        self.courseSelector = CourseSelector()
        self.courseSelector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Connect signals from the course selector to corresponding methods
        self.courseSelector.coursesSubmitted.connect(self.navigateToSchedulesWindow)
        self.courseSelector.loadRequested.connect(self.load_courses_from_file)

        # === Layout Setup ===
        # Create a vertical layout for the main content
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(50, 30, 50, 30)  # Set margins
        outer_layout.setSpacing(20)  # Set spacing between elements

        # Add courseSelector directly without extra stretching
        outer_layout.addWidget(self.courseSelector)

        # Wrap the layout in a container widget
        container = QWidget()
        container.setLayout(outer_layout)
        self.setCentralWidget(container)  # Set the container as the central widget

        # Set full-screen display
        self.showMaximized()
        
        # External callbacks for handling events
        self.on_courses_loaded: Callable[[str], None] = lambda path: None  # Callback for when courses are loaded
        self.on_continue: Callable[[List[Course]], None] = lambda selected: None  # Callback for when user continues

    def displayCourses(self, courses: List[Course]):
        """
        Populate the course selector with a list of courses.
        """
        self.courseSelector.populate_courses(courses)

    def handleSelection(self) -> List[Course]:
        """
        Retrieve the list of selected courses from the course selector.
        """
        return self.courseSelector.get_selected_courses()

    def navigateToSchedulesWindow(self):
        """
        Handle the event when the user submits their course selection.
        """
        if hasattr(self.courseSelector, 'close_progress_bar'):
            self.courseSelector.close_progress_bar()

        selected = self.handleSelection()
        if selected:
            # Check if the number of selected courses exceeds the limit
            if len(selected) > 7:
                # Display a warning message to the user
                QMessageBox.warning(self, "Warning", "You cannot select more than 7 courses.")
                return  # Exit the method to prevent further processing
            self.on_continue(selected)  # Trigger the continue callback with selected courses

    def load_courses_from_file(self):
        """
        Open a file dialog to allow the user to select a course file.
        """
        if hasattr(self.courseSelector, 'close_progress_bar'):
            self.courseSelector.close_progress_bar()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Course File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            self.courseSelector.close_progress_bar()
            self.courseSelector._handle_clear()
            self.on_courses_loaded(file_path)  # Trigger the courses loaded callback with the file path
