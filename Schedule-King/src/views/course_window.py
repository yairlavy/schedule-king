from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout,
    QHBoxLayout, QWidget, QSizePolicy, QMessageBox,
    QPushButton, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from typing import List, Callable
from src.models.course import Course
from src.components.course_selector import CourseSelector
from src.components.constraint_dialog import ConstraintDialog
import os
from src.models.time_slot import TimeSlot
from src.styles.ui_styles import red_button_style, blue_button_style

class CourseWindow(QMainWindow):
    def __init__(self, maximize_on_start=True):
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

        # === Time Constraints Section ===
        # Store forbidden time slots
        self.forbidden_slots = set()
        
        # Create constraint button and add it to the CourseSelector's button layout
        self.constraintBtn = QPushButton("Set Time Constraints")
        self.constraintBtn.clicked.connect(self._open_constraint_dialog)
        self.constraintBtn.setCursor(Qt.PointingHandCursor)
        self.constraintBtn.setStyleSheet(blue_button_style())
        
        # Add the constraint button to the CourseSelector's existing button layout
        self.courseSelector.button_layout.addWidget(self.constraintBtn)

        # Wrap the layout in a container widget
        container = QWidget()
        container.setLayout(outer_layout)
        self.setCentralWidget(container)  # Set the container as the central widget

        # Set full-screen display
        # Optionally set full-screen display (disabled during tests to prevent access violations on Windows)
        if maximize_on_start:
            self.showMaximized()

        # External callbacks for handling events
        self.on_courses_loaded: Callable[[str], None] = lambda path: None  # Callback for when courses are loaded
        self.on_continue: Callable[[List[Course]], None] = lambda selected: None  # Callback for when user continues

        # Note: The courseSelector.clear_button only clears course selections, not time constraints
        # Time constraints are managed independently through the constraint dialog

    def _open_constraint_dialog(self):
        """Open the constraint selection dialog"""
        dialog = ConstraintDialog(self, self.forbidden_slots)
        if dialog.exec_() == QDialog.Accepted:
            forbidden_cells = dialog.get_constraints()
            self.forbidden_slots = forbidden_cells
            # Update button text to show number of constraints
            count = len(self.forbidden_slots)
            if count > 0:
                self.constraintBtn.setText(f"Time Constraints ({count} slots)")
            else:
                self.constraintBtn.setText("Set Time Constraints")


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
                    
        # Convert forbidden cells to TimeSlot objects
        forbidden = []
        for row, col in self.forbidden_slots:
            day_index = col + 1  # Sunday=1
            start_time = f"{8+row:02d}:00"
            end_time = f"{8+row+1:02d}:00"
            forbidden.append(TimeSlot(day=str(day_index), start_time=start_time, end_time=end_time, room="", building=""))

        if forbidden:
            self.on_continue(selected, forbidden)
        else:
            self.on_continue(selected)

    def load_courses_from_file(self):
        """
        Open a file dialog to allow the user to select a course file.
        """
        if hasattr(self.courseSelector, 'close_progress_bar'):
            self.courseSelector.close_progress_bar()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Course File",
            "",
            "Text Files (*.txt);;Excel Files (*.xlsx);;All Files (*)"
        )
        if file_path:
            self.courseSelector.close_progress_bar()
            self.courseSelector._handle_clear()
            self.on_courses_loaded(file_path)  # Trigger the courses loaded callback with the file path