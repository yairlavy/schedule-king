from src.services.schedule_api import ScheduleAPI
from src.models.course import Course
from typing import List, Optional
from src.models.time_slot import TimeSlot

class CourseController:
    def __init__(self, api: ScheduleAPI):
        self.api = api
        self.courses: List[Course] = []
        self.selected_courses: List[Course] = []
        self.forbidden_slots: List[TimeSlot] = []  # Add storage for forbidden slots

    def get_courses_names(self, file_path: str) -> List[Course]:
        """
        Loads the courses from the file path using the ScheduleAPI.
        """
        self.courses = self.api.get_courses(file_path)
        return self.courses

    def set_selected_courses(self, selected: List[Course],forbidden_slots: Optional[List[TimeSlot]] = None) -> None:
        """
        Saves the selected courses for future use.
        """
        self.selected_courses = selected
        self.forbidden_slots = forbidden_slots or []

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