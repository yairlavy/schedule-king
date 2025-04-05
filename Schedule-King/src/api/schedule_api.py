from src.data.file_handler import FileHandler
from src.core.scheduler import Scheduler
from src.data.models.schedule import Schedule
from src.data.parsers.text_parser import TextParser
from src.data.formatters.text_formatter import TextFormatter
from src.core.all_strategy import AllStrategy
from src.core.conflict_checker import ConflictChecker

class ScheduleAPI:
    DEFAULT_SOURCE = r"C:\Users\User\Documents\Projects\Schedule-King\Software-for-building-a-student-study-schedule\Schedule-King\tests\test_files\V1.0CourseDB.txt"
    DEFAULT_DESTINATION = r"C:\Users\User\Documents\Projects\Schedule-King\Software-for-building-a-student-study-schedule\Schedule-King\tests\test_files\output.txt"

    def __init__(self):
        """
        Initialize the ScheduleAPI with a FileHandler and a Scheduler.
        """
        self.file_handler = FileHandler(self.DEFAULT_SOURCE, self.DEFAULT_DESTINATION)

    def process(self) -> str:
        """
        Main entry point: parses data, generates schedules, and returns formatted output.

        :param raw_data: Input text (e.g., from uploaded file or raw content)
        :return: Formatted string with valid generated schedules
        """
        # Parse the input
        courses = self.file_handler.parse()
        # Initialize the scheduler with parsed courses
        self.scheduler = Scheduler(courses, AllStrategy(courses))
        # Generate schedules
        schedules = self.scheduler.generate()
        # Format schedules for output
        self.file_handler.format(schedules)
