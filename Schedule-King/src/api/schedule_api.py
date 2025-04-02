from src.data.file_handler import FileHandler
from src.core.scheduler import Scheduler
from src.data.models.schedule import Schedule

class ScheduleAPI:
    def __init__(self, file_handler: FileHandler, scheduler: Scheduler):
        """
        Initialize the ScheduleAPI with a FileHandler and a Scheduler.
        """
        self.file_handler = file_handler
        self.scheduler = scheduler

    def process(self, raw_data: str) -> str:
        """
        Main entry point: parses data, generates schedules, and returns formatted output.

        :param raw_data: Input text (e.g., from uploaded file or raw content)
        :return: Formatted string with valid generated schedules
        """
        # Parse the input
        courses, _ = self.file_handler.parse(raw_data)

        # Update scheduler with selected courses
        self.scheduler.selected = courses

        # Generate schedules
        schedules = self.scheduler.generate()

        # Format schedules for output
        return self.file_handler.format(schedules)
