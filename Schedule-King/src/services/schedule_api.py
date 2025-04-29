from .file_handler import FileHandler
from .scheduler import Scheduler
from .all_strategy import AllStrategy
from src.models.course import Course

class ScheduleAPI:
    def __init__(self, file_path: str):
        """
        Initialize the ScheduleAPI with input/output file paths.
        """
        try:
            self.file_handler = FileHandler(file_path)
        except FileNotFoundError as e:
            print(f"Error: {e}. Please check the file path and try again.")
            exit(1)

    def get_courses(self) -> list[Course]:
        """
        Returns all courses parsed from the file.
        """
        try:
            return self.file_handler.parse()
        except ValueError as e:
            print(f"Error: {e}. Please check the input file format.")
            return []

    def process(self, selected_courses: list[Course]) -> list:
        """
        Generate schedules based on selected courses.

        :param selected_courses: List of selected Course objects
        :return: List of generated Schedule objects
        """
        scheduler = Scheduler(selected_courses, AllStrategy(selected_courses))
        schedules = scheduler.generate()
        return schedules
    
    def export_schedules(self, schedules: list, file_path: str):
        """
        Export schedules to a simple text file.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                for index, schedule in enumerate(schedules, 1):
                    f.write(f"Schedule {index}:\n")
                    f.write(str(schedule))
                    f.write("\n\n")
        except Exception as e:
            print(f"Error exporting schedules: {e}")
