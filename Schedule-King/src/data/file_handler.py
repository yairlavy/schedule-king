from typing import List, Tuple
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup
from src.data.models.schedule import Schedule
from src.data.parsers.parser_interface import IParser
from src.data.formatters.formatter_interface import IFormatter

class FileHandler:
    def __init__(self, parser: IParser, formatter: IFormatter):
        """
        Initialize the FileHandler with a parser and a formatter.
        """
        self.parser = parser
        self.formatter = formatter

    def parse(self, raw_data: str) -> Tuple[List[Course], List[LectureGroup]]:
        """
        Parses the input data into courses and lecture groups.

        :param raw_data: Raw text input from file or user
        :return: Tuple (List[Course], List[LectureGroup])
        """
        return self.parser.parse(raw_data)

    def format(self, schedules: List[Schedule]) -> str:
        """
        Formats a list of schedules into string representation.

        :param schedules: List of Schedule objects
        :return: Formatted string
        """
        return self.formatter.format(schedules)
