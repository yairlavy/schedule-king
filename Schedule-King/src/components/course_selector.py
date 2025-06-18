from PyQt5.QtWidgets import (
    QVBoxLayout, QPushButton, QWidget, QHBoxLayout,
    QSizePolicy, QLabel, QFrame, QMessageBox, QProgressDialog
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPixmap
from typing import List
from src.models.course import Course
from src.components.course_list import CourseList
from src.components.selected_courses_panel import SelectedCoursesPanel
from src.components.search_bar import SearchBar
from src.styles.ui_styles import (
    red_button_style, green_button_style, blue_button_style, 
    disabled_button_style, title_label_style, warning_label_style,
    success_label_style, instruction_label_style, footer_label_style,
    course_selector_background
)

class CourseSelector(QWidget):
    # Signals for communicating with parent widgets
    coursesSelected = pyqtSignal(list)
    coursesSubmitted = pyqtSignal(list)
    loadRequested = pyqtSignal()
    MAX_COURSES = 7  # Maximum number of courses allowed

    def __init__(self, parent=None):
        super().__init__(parent)
        # Set background style
        self.setStyleSheet(course_selector_background())
        
        # Initialize layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 30, 40, 30)
        self.layout.setSpacing(16)
        
        # Initialize UI components in separate methods
        self._setup_header()
        self._setup_search_bar()
        self._setup_course_panels()
        self._setup_buttons()
        self._setup_footer()
        
        # Progress dialog for schedule generation
        self.progress_bar = None
        
        # Initialize submit button state
        # The _update_submit_button_state expects a list of selected courses
        self._update_submit_button_state(self.get_selected_courses()) 
        
    def _setup_header(self):
        """Setup header components including title and instruction labels."""
        # === Banner Image ===
        banner = QLabel()
        banner.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(banner)

        # === Title ===
        self.title_label = QLabel("Available Courses")
        self.title_label.setStyleSheet(title_label_style())
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # === Course Limit Label ===
        self.limit_label = QLabel(f"Maximum {self.MAX_COURSES} courses allowed")
        self.limit_label.setStyleSheet(warning_label_style())
        self.limit_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.limit_label)

        # === Instruction Label ===
        instruction = QLabel("Select your desired courses from the list below and click 'Generate Schedules'")
        instruction.setStyleSheet(instruction_label_style())
        instruction.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(instruction)
        
    def _setup_search_bar(self):
        """Setup the search bar component."""
        self.search_bar = SearchBar()
        self.search_bar.searchTextChanged.connect(self._handle_search)
        self.layout.addWidget(self.search_bar)
        
    def _setup_course_panels(self):
        """Setup course list and selected courses panel."""
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
        
    def _setup_buttons(self):
        """Setup action buttons."""
        # === Buttons Layout ===
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(15)
        self.button_layout.setAlignment(Qt.AlignCenter)

        # Clear All button
        self.clear_button = QPushButton("Clear All")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setStyleSheet(red_button_style())

        # Generate Schedules button
        self.submit_button = QPushButton("Generate Schedules")
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setStyleSheet(green_button_style())

        # Load Courses button
        self.load_button = QPushButton("Load Courses")
        self.load_button.setCursor(Qt.PointingHandCursor)
        self.load_button.setStyleSheet(blue_button_style())

        # Add buttons to layout
        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.submit_button)
        self.button_layout.addWidget(self.load_button)
        self.layout.addLayout(self.button_layout)
        
        # Connect button signals to handlers
        self.clear_button.clicked.connect(self._handle_clear)
        self.submit_button.clicked.connect(self._handle_submit)
        self.load_button.clicked.connect(self._handle_load)
        
    def _setup_footer(self):
        """Setup footer with credits."""
        footer = QLabel("\U0001F537 Records made by the Schedule Kings")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(footer_label_style())
        self.layout.addWidget(footer)

    def show_progress_bar(self):
        """Show progress bar while schedules are generating."""
        if self.progress_bar:
            self.progress_bar.close()
        self.progress_bar = QProgressDialog("Generating schedules...", "Cancel", 0, 0, self)
        self.progress_bar.setWindowModality(Qt.WindowModal)
        self.progress_bar.setMinimumDuration(0)
        self.progress_bar.setAutoClose(False)
        self.progress_bar.setAutoReset(False)
        self.progress_bar.setWindowTitle("Generating")
        self.progress_bar.show()

    def close_progress_bar(self):
        """Close the progress bar if active."""
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None
    
    def set_available_courses(self, courses: List[Course]):
        """Populate the course list with available courses."""
        self.course_list.populate_courses(courses)
        self.title_label.setText(f"Available Courses ({len(courses)} total)")

    def get_all_courses(self) -> List[Course]:
        """
        Returns the current list of all available courses.
        This is needed by CourseWindow for the CourseEditorDialog.
        """
        # Assuming course_list stores all available courses after population
        return self.course_list.courses 

    def _handle_search(self, text: str):
        """Filter courses based on search text."""
        self.course_list.filter_courses(text)
        # Update title to show number of selected courses after filtering
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
        # Check if courses are loaded
        if len(self.course_list.courses) == 0:
            QMessageBox.critical(self, "Error", "No courses loaded. Please load courses first.")
            return
        # Check if any courses are selected
        if len(selected) == 0:
            QMessageBox.critical(self, "Error", "No courses selected. Please select courses first.")
            return
        # Check if selection exceeds max allowed
        if len(selected) > self.MAX_COURSES:
            QMessageBox.warning(self, "Course Limit", f"You cannot select more than {self.MAX_COURSES} courses.")
            return
        # Show progress bar and emit signal
        self.show_progress_bar()
        self.coursesSubmitted.emit(selected)

    def _handle_clear(self):
        """Clear all selections and reset UI."""
        self.close_progress_bar()
        self.course_list.clear_selection()
        self.selected_panel.clear()
        self.search_bar.clear()
        self.title_label.setText(f"Available Courses ({len(self.course_list.courses)} total)")

    def _clear_all_selections(self):
        """
        New method to clear all selections, including search and progress bar.
        This is called by CourseWindow.
        """
        self._handle_clear() # Re-use existing clear logic
        # If there were any other internal states to clear specific to filters/search, add here
        # self.search_bar.clear() is already called by _handle_clear

    def _handle_load(self):
        """Emit signal to load courses."""
        self.close_progress_bar()
        self.loadRequested.emit()

    def get_selected_courses(self) -> List[Course]:
        """Return the currently selected courses."""
        return self.course_list.get_selected_courses()

    def _update_submit_button_state(self, selected_courses: List[Course]):
        """Update the submit button state based on the number of selected courses."""
        if len(selected_courses) > self.MAX_COURSES:
            self.submit_button.setEnabled(False)
            self.submit_button.setStyleSheet(disabled_button_style())
            self.limit_label.setStyleSheet(warning_label_style())
        else:
            self.submit_button.setEnabled(True)
            self.submit_button.setStyleSheet(green_button_style())
            self.limit_label.setStyleSheet(success_label_style())

    def select_courses_by_code(self, codes):
        """Select courses in the list by their course codes."""
        # Update the selected_course_codes set directly
        self.course_list.selected_course_codes = set(codes)
        # Refresh the list to reflect selection
        self.course_list._update_course_list(self.course_list.courses)
        self._handle_selection_changed(self.get_selected_courses())