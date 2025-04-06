from typing import List
from src.data.models.course import Course
from src.data.models.schedule import Schedule
from src.data.parsers.text_parser import TextParser
from src.data.formatters.text_formatter import TextFormatter

class FileHandler:
    def __init__(self , source: str, destination: str):
        """
        Initialize the FileHandler with a parser and a formatter.
        """
        self.parser = TextParser(source)
        self.formatter = TextFormatter(destination)

    def parse(self) -> List[Course]:
        """
        Parses the input data into courses and lecture groups.

        :param raw_data: Raw text input from file or user
        :return: Tuple (List[Course], List[LectureGroup])
        """
        return self.parser.parse()

    def format(self, schedules: List[Schedule]) :
        """
        Formats a list of schedules into string representation.

        :param schedules: List of Schedule objects
        :return: Formatted string
        """
        self.formatter.format(schedules)
