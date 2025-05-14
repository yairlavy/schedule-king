from PyQt5.QtWidgets import (
    QVBoxLayout, QPushButton, QWidget, QHBoxLayout,
    QSizePolicy, QLabel, QFrame, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPixmap
from typing import List
from src.models.course import Course
from src.components.course_list import CourseList
from src.components.selected_courses_panel import SelectedCoursesPanel
from src.components.search_bar import SearchBar

class CourseSelector(QWidget):
    # Signals for communicating with parent widgets
    coursesSelected = pyqtSignal(list)
    coursesSubmitted = pyqtSignal(list)
    loadRequested = pyqtSignal()
    MAX_COURSES = 7  # Maximum number of courses allowed

    def __init__(self, parent=None):
        super().__init__(parent)
        # Set background style
        self.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E3F2FD, stop:1 #F0F7FF); border-radius: 10px;")

        # === Main Layout ===
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 30, 40, 30)
        self.layout.setSpacing(16)

        # === Banner Image ===
        banner = QLabel()
        banner.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(banner)

        # === Title ===
        self.title_label = QLabel("Available Courses")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #1A237E;
                font-size: 34px;
                font-weight: 800;
                font-family: 'Segoe UI', sans-serif;
                border-bottom: 3px solid #C5CAE9;
                padding-bottom: 12px;
            }
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # === Course Limit Label ===
        self.limit_label = QLabel(f"Maximum {self.MAX_COURSES} courses allowed")
        self.limit_label.setStyleSheet("color: #F44336; font-size: 11pt; font-weight: bold;")
        self.limit_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.limit_label)

        # === Instruction Label ===
        instruction = QLabel("Select your desired courses from the list below and click 'Generate Schedules'")
        instruction.setStyleSheet("color: #3A3A3A; font-size: 12pt; font-style: italic;")
        instruction.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(instruction)

        # === Search Bar ===
        self.search_bar = SearchBar()
        self.search_bar.searchTextChanged.connect(self._handle_search)
        self.layout.addWidget(self.search_bar)

        # === Side-by-Side Layout for course list and selected panel ===
        self.split_layout = QHBoxLayout()
        self.split_layout.setSpacing(20)
        self.layout.addLayout(self.split_layout)

        # === Course List ===
        self.course_list = CourseList()
        self.course_list.selectionChanged.connect(self._handle_selection_changed)
        self.split_layout.addWidget(self.course_list, 4)

        # === Selected Courses Panel ===
        self.selected_panel = SelectedCoursesPanel()
        self.split_layout.addWidget(self.selected_panel, 2)

        # === Buttons Layout ===
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(15)
        self.button_layout.setAlignment(Qt.AlignCenter)

        # Clear All button
        self.clear_button = QPushButton("Clear All")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setStyleSheet(self._red_button_style())

        # Generate Schedules button
        self.submit_button = QPushButton("Generate Schedules")
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setStyleSheet(self._green_button_style())

        # Load Courses button
        self.load_button = QPushButton("Load Courses")
        self.load_button.setCursor(Qt.PointingHandCursor)
        self.load_button.setStyleSheet(self._blue_button_style())

        # Add buttons to layout
        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.submit_button)
        self.button_layout.addWidget(self.load_button)
        self.layout.addLayout(self.button_layout)

        # === Footer ===
        footer = QLabel("\U0001F537 Records made by the Schedule Kings")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #78909C; font-size: 10pt; margin-top: 20px;")
        self.layout.addWidget(footer)

        # Connect button signals to handlers
        self.clear_button.clicked.connect(self._handle_clear)
        self.submit_button.clicked.connect(self._handle_submit)
        self.load_button.clicked.connect(self._handle_load)

        # Initialize submit button state
        self._update_submit_button_state([])

    def populate_courses(self, courses: List[Course]):
        """Populate the course list with available courses."""
        self.course_list.populate_courses(courses)
        self.title_label.setText(f"Available Courses ({len(courses)} total)")

    def _handle_search(self, text: str):
        """Filter courses based on search text."""
        self.course_list.filter_courses(text)
        self.title_label.setText(f"Available Courses ({len(self.course_list.get_selected_courses())} selected)")

    def _handle_selection_changed(self, selected_courses: List[Course]):
        """Handle course selection changes."""
        if len(selected_courses) > self.MAX_COURSES:
            # Remove the last selected course if over the limit
            self.course_list.selected_course_codes.remove(selected_courses[-1].course_code)
            self.course_list._update_course_list(self.course_list.courses)
            QMessageBox.warning(self, "Course Limit", f"You cannot select more than {self.MAX_COURSES} courses.")
            return

        # Update selected panel and UI
        self.selected_panel.update_selection(selected_courses)
        self.title_label.setText(f"Available Courses ({len(selected_courses)} selected)")
        self._update_submit_button_state(selected_courses)
        self.coursesSelected.emit(selected_courses)

    def _handle_submit(self):
        """Emit the selected courses when submitting."""
        selected = self.course_list.get_selected_courses()
        if len(selected) > self.MAX_COURSES:
            QMessageBox.warning(self, "Course Limit", f"You cannot select more than {self.MAX_COURSES} courses.")
            return
        self.coursesSubmitted.emit(selected)

    def _handle_clear(self):
        """Clear all selections and reset UI."""
        self.course_list.clear_selection()
        self.selected_panel.clear()
        self.search_bar.clear()
        self.title_label.setText(f"Available Courses ({len(self.course_list.courses)} total)")

    def _handle_load(self):
        """Emit signal to load courses."""
        self.loadRequested.emit()

    def get_selected_courses(self) -> List[Course]:
        """Return the currently selected courses."""
        return self.course_list.get_selected_courses()

    def _red_button_style(self):
        """Return stylesheet for red button."""
        return """
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
            QPushButton:pressed {
                background-color: #B71C1C;
            }
        """

    def _green_button_style(self):
        """Return stylesheet for green button."""
        return """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
            QPushButton:pressed {
                background-color: #1B5E20;
            }
        """

    def _blue_button_style(self):
        """Return stylesheet for blue button."""
        return """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """

    def _update_submit_button_state(self, selected_courses: List[Course]):
        """Update the submit button state based on the number of selected courses."""
        if len(selected_courses) > self.MAX_COURSES:
            self.submit_button.setEnabled(False)
            self.submit_button.setStyleSheet(self._disabled_button_style())
            self.limit_label.setStyleSheet("color: #F44336; font-size: 11pt; font-weight: bold;")
        else:
            self.submit_button.setEnabled(True)
            self.submit_button.setStyleSheet(self._green_button_style())
            self.limit_label.setStyleSheet("color: #4CAF50; font-size: 11pt; font-weight: bold;")

    def _disabled_button_style(self):
        """Return stylesheet for disabled button."""
        return """
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
                min-width: 180px;
            }
        """

    def select_courses_by_code(self, codes):
        """Select courses in the list by their course codes."""
        # Update the selected_course_codes set directly
        self.course_list.selected_course_codes = set(codes)
        # Refresh the list to reflect selection
        self.course_list._update_course_list(self.course_list.courses)
        self._handle_selection_changed(self.get_selected_courses())