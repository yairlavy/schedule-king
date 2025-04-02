from src.data.file_handler import FileHandler
from src.core.scheduler import Scheduler
from src.data.models.schedule import Schedule
from src.data.parsers.text_parser import TextParser
from src.data.formatters.text_formatter import TextFormatter
from src.core.all_strategy import AllStrategy
from src.core.conflict_checker import ConflictChecker
class ScheduleAPI:
    def __init__(self):
        """
        Initialize the ScheduleAPI with a FileHandler and a Scheduler.
        """
        parser = TextParser("/home/ido/Downloads/V1.0CourseDB.txt")
        formatter = TextFormatter()
        self.file_handler = FileHandler(parser, formatter)

    def process(self) -> str:
        """
        Main entry point: parses data, generates schedules, and returns formatted output.

        :param raw_data: Input text (e.g., from uploaded file or raw content)
        :return: Formatted string with valid generated schedules
        """
        # Parse the input
        courses = self.file_handler.parse()
        conflict_chcker = ConflictChecker()
        statrategy = AllStrategy(courses, conflict_chcker)
        self.scheduler = Scheduler(courses, statrategy)
        print(courses)
        # Update scheduler with selected courses

        # Generate schedules
        schedules = self.scheduler.generate()
        print(schedules)
        # Format schedules for output
        return self.file_handler.format(schedules)
