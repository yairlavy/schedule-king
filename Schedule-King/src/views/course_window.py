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
from src.models.time_slot import TimeSlot
from PyQt5.QtWidgets import QGroupBox, QComboBox, QTimeEdit, QPushButton, QListWidget, QHBoxLayout
from PyQt5.QtCore import QTime
from src.styles.ui_styles import red_button_style

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

        # === Constraints Group ===
        self.constraintsBox = QGroupBox("Time Constraints (Select Day and Time you dont want to have classes on)")
        c_layout = QHBoxLayout()
        self.dayCombo = QComboBox()
        self.dayCombo.addItems(["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"])
       
        self.startTime = QTimeEdit(); self.startTime.setDisplayFormat("HH")
        self.startTime.setMinimumTime(QTime(8, 0))
        self.startTime.setMaximumTime(QTime(19, 0))

        self.endTime   = QTimeEdit(); self.endTime.setDisplayFormat("HH")
        self.endTime.setMinimumTime(QTime(9, 0))
        self.endTime.setMaximumTime(QTime(20, 0))

        self.addConstraintBtn = QPushButton("Add Constraint")
        self.removeConstraintBtn = QPushButton("Remove Selected Constraint")
        self.removeConstraintBtn.setStyleSheet(red_button_style())

        # Add buttons vertically
        btn_layout = QVBoxLayout()        
        btn_layout.addWidget(self.addConstraintBtn)
        btn_layout.addWidget(self.removeConstraintBtn)

        self.constraintsList = QListWidget()  # List to display constraints

        # Add the rest of the widgets to c_layout
        c_layout.addWidget(self.dayCombo)
        c_layout.addWidget(self.startTime)
        c_layout.addWidget(self.endTime)
        c_layout.addLayout(btn_layout)  # Add the vertical button layout
        c_layout.addWidget(self.constraintsList)

        self.constraintsBox.setLayout(c_layout)
        outer_layout.insertWidget(1, self.constraintsBox)

        # Hook button
        self.addConstraintBtn.clicked.connect(self._on_add_constraint)
        self.removeConstraintBtn.clicked.connect(self._on_remove_constraint)
        self.courseSelector.clear_button.clicked.connect(self.constraintsList.clear)

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

    def _on_add_constraint(self):
        start = self.startTime.time().toString("HH:mm")
        end   = self.endTime.time().toString("HH:mm")
        name  = self.dayCombo.currentText()
        text  = f"{name} {start}-{end}"

        if start >= end:
            QMessageBox.warning(self, "Invalid Time", "Start time must be before end time.")
            return

        # Check for duplicates by comparing text
        for i in range(self.constraintsList.count()):
            if self.constraintsList.item(i).text() == text:
                return  # Already exists, do not add again

        self.constraintsList.addItem(text)
    
    def _on_remove_constraint(self):
        # Remove selected constraints from the list
        selected_items = self.constraintsList.selectedItems()
        for item in selected_items:
            self.constraintsList.takeItem(self.constraintsList.row(item))

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
                    
        # gather forbidden TimeSlots:
        forbidden = []
        for i in range(self.constraintsList.count()):
            text = self.constraintsList.item(i).text()
            # "Sunday 14:00–16:00"
            day_name, times = text.split(' ',1)
            start, end = times.split('-')
            day_index = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"].index(day_name) + 1
            forbidden.append(TimeSlot(day=str(day_index), start_time=start, end_time=end, room="", building=""))

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