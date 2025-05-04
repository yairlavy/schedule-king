from src.services.schedule_api import ScheduleAPI
from src.models.schedule import Schedule
from src.models.course import Course
from typing import List

class ScheduleController:
    def __init__(self, api: ScheduleAPI):
        self.api = api
        self.schedules: List[Schedule] = []

    def generate_schedules(self, selected_courses: List[Course]) -> List[Schedule]:
        """
        Generates possible schedules using the API and saves them.
        """
        self.schedules = self.api.process(selected_courses)
        return self.schedules

    def get_schedules(self) -> List[Schedule]:
        """
        Returns the generated schedules.
        """
        return self.schedules
