from src.services.schedule_api import ScheduleAPI
from src.models.course import Course
from typing import List, Optional
from src.models.time_slot import TimeSlot
from PyQt5.QtCore import QObject, pyqtSignal # Import QObject and pyqtSignal

class CourseController(QObject): # Inherit from QObject to use signals
    courses_updated = pyqtSignal(list) # Signal to notify about updated course list

    def __init__(self, api: ScheduleAPI):
        super().__init__() # Call QObject constructor
        self.api = api
        self.courses: List[Course] = [] # List to store all loaded courses
        self.selected_courses: List[Course] = [] # List to store selected courses
        self.forbidden_slots: List[TimeSlot] = []  # List to store forbidden time slots

    def get_courses_names(self, file_path: str) -> List[Course]:
        """
        Loads the courses from the file path using the ScheduleAPI.
        Emits a signal when courses are loaded.
        """
        self.courses = self.api.get_courses(file_path) # Load courses from API
        self.courses_updated.emit(self.courses) # Emit signal when courses are loaded
        return self.courses

    def set_selected_courses(self, selected: List[Course], forbidden_slots: Optional[List[TimeSlot]] = None) -> None:
        """
        Saves the selected courses and forbidden slots for future use.
        """
        self.selected_courses = selected # Store selected courses
        self.forbidden_slots = forbidden_slots or [] # Store forbidden slots, default to empty list

    def get_selected_courses(self) -> List[Course]:
        """
        Returns the courses selected by the user.
        """
        return self.selected_courses

    def get_forbidden_slots(self) -> List[TimeSlot]:
        """
        Returns the forbidden time slots.
        """
        return self.forbidden_slots

    def add_or_update_course(self, course: Course):
        """
        Adds a new course or updates an existing one based on its course code.
        Emits a signal when the course list changes.
        """
        found = False
        for i, existing_course in enumerate(self.courses):
            if existing_course.course_code == course.course_code:
                self.courses[i] = course # Update existing course
                found = True
                break
        if not found:
            self.courses.append(course) # Add new course
        
        self.courses_updated.emit(self.courses) # Notify listeners that the course list has changed