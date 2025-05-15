import os
from typing import List
from .file_handler import FileHandler
from .scheduler import Scheduler
from .all_strategy import AllStrategy
from src.models.course import Course
from src.models.schedule import Schedule

class ScheduleAPI:
    def __init__(self):
        """
        Initialize ScheduleAPI with a format/parse handler.
        """
        self.file_handler = FileHandler()

    def get_courses(self, source: str) -> List[Course]:
        """
        Parse and return all courses from the given source file.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"The source file '{source}' does not exist.")
        try:
            return self.file_handler.parse(source)
        except ValueError as e:
            print(f"Error parsing courses: {e}. Please check the input format.")
            return []

    def process(self, selected_courses: List[Course]) -> List[Schedule]:
        """
        Generate schedules based on selected courses.
        """
        scheduler = Scheduler(selected_courses, AllStrategy(selected_courses))
        return list(scheduler.generate())

    def export(self, schedules: List[Schedule], destination: str) -> None:
        """
        Export the given schedules to the destination file.
        """
        try:
            self.file_handler.format(schedules, destination)
            print(f"Schedules successfully exported to {destination}.")
        except ValueError as e:
            print(f"Error exporting schedules: {e}.")
