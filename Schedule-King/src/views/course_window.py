from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout,
    QHBoxLayout, QWidget, QSizePolicy, QMessageBox,
    QPushButton, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from typing import List, Callable, Optional
from src.models.course import Course
from src.components.course_selector import CourseSelector
from src.components.constraint_dialog import ConstraintDialog
import os
from src.models.time_slot import TimeSlot
from src.styles.ui_styles import blue_button_style
from src.components.CourseEditorDialog import CourseEditorDialog

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

        # Add courseSelector directly to the layout
        outer_layout.addWidget(self.courseSelector)

        # === Additional Buttons Layout (for Add/Edit Course) ===
        # This layout is separate from CourseSelector's internal buttons
        additional_buttons_layout = QHBoxLayout()
        additional_buttons_layout.addStretch(1) # Push button to the right

        # Add/Edit Course Button - Text changed to English
        self.add_edit_course_button = QPushButton("Add/Edit Course")
        self.add_edit_course_button.setStyleSheet(blue_button_style())
        self.add_edit_course_button.setCursor(Qt.PointingHandCursor)
        self.add_edit_course_button.clicked.connect(self.open_course_editor_dialog)
        additional_buttons_layout.addWidget(self.add_edit_course_button)

        # Add this new button layout to the main window's layout
        outer_layout.addLayout(additional_buttons_layout)

        # === Time Constraints Section ===
        # Store forbidden time slots as a set of (row, col) tuples
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

        # Set full-screen display if requested
        if maximize_on_start:
            self.showMaximized()

        # External callbacks for handling events
        self.on_courses_loaded: Callable[[str], None] = lambda path: None
        self.on_continue: Callable[[List[Course], Optional[List[TimeSlot]]], None] = lambda selected, forbidden: None
        self.on_course_added_or_updated: Optional[Callable[[Course], None]] = None

    def _open_constraint_dialog(self):
        """Open the constraint selection dialog and update forbidden slots."""
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
        This method is called by the CourseController's courses_updated signal.
        """
        self.courseSelector.set_available_courses(courses)

    def handleSelection(self) -> List[Course]:
        """
        Retrieve the list of selected courses from the course selector.
        """
        return self.courseSelector.get_selected_courses()

    def navigateToSchedulesWindow(self, selected_courses: List[Course]):
        """
        Handle the event when the user submits their course selection.
        This method now receives selected_courses directly from the CourseSelector's signal.
        """
        # Close progress bar if present
        if hasattr(self.courseSelector, 'close_progress_bar'):
            self.courseSelector.close_progress_bar()

        selected = selected_courses 

        # Check if the number of selected courses exceeds the maximum allowed
        if selected:
            if len(selected) > self.courseSelector.MAX_COURSES:
                QMessageBox.warning(self, "Warning", f"You cannot select more than {self.courseSelector.MAX_COURSES} courses.")
                return 
                        
        # Convert forbidden slot cells to TimeSlot objects
        forbidden = []
        for row, col in self.forbidden_slots: 
            day_index = col + 1
            start_time = f"{8+row:02d}:00"
            end_time = f"{8+row+1:02d}:00"
            forbidden.append(TimeSlot(day=str(day_index), start_time=start_time, end_time=end_time, room="", building=""))

        # Call the continue callback with selected courses and forbidden slots
        if self.on_continue:
            self.on_continue(selected, forbidden)

    def load_courses_from_file(self):
        """
        Open a file dialog to allow the user to select a course file.
        """
        # Close progress bar if present
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
            self.courseSelector._clear_all_selections() 
            if self.on_courses_loaded:
                self.on_courses_loaded(file_path)

    def open_course_editor_dialog(self):
        """
        Opens the CourseEditorDialog to add or edit a course.
        """
        all_current_courses = self.courseSelector.get_all_courses()
        
        editor_dialog = CourseEditorDialog(all_current_courses, self)
        editor_dialog.courseEdited.connect(self._handle_course_edited)

        # Show the dialog and handle result
        if editor_dialog.exec_() == QDialog.Accepted:
            pass
        else:
            QMessageBox.information(self, "Cancelled", "Course editing cancelled.")

    def _handle_course_edited(self, edited_course: Course):
        """
        Handles the course that was edited or created in the CourseEditorDialog.
        This method will notify the controller.
        """
        if edited_course:
            QMessageBox.information(self, "Course Saved", f"Course '{edited_course.name}' saved successfully.")
            if self.on_course_added_or_updated:
                self.on_course_added_or_updated(edited_course)