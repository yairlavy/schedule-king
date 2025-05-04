from src.services.schedule_api import ScheduleAPI
from src.models.course import Course
from typing import List

class CourseController:
    def __init__(self, api: ScheduleAPI):
        self.api = api
        self.courses: List[Course] = []
        self.selected_courses: List[Course] = []

    def get_courses_names(self, file_path: str) -> List[Course]:
        """
        Loads the courses from the file path using the ScheduleAPI.
        """
        self.api.file_handler.file_path = file_path
        self.courses = self.api.get_courses()
        return self.courses

    def set_selected_courses(self, selected: List[Course]) -> None:
        """
        Saves the selected courses for future use.
        """
        self.selected_courses = selected

    def get_selected_courses(self) -> List[Course]:
        """
        Returns the courses selected by the user.
        """
        return self.selected_courses
