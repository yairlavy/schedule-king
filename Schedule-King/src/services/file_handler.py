from typing import List
from src.models.course import Course
from src.models.schedule import Schedule
from .text_parser import TextParser
from .text_formatter import TextFormatter
import os

class FileHandler:
    def __init__(self, source: str):
        """
        Initialize the FileHandler with a parser and a formatter.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"The source file '{source}' does not exist.")
        self.parser = TextParser(source)
        self.formatter = TextFormatter()

    def parse(self) -> List[Course]:
        """
        Parses the input data into courses and lecture groups.
        :return: List of Course objects
        """
        return self.parser.parse()

    def format(self, schedules: List[Schedule]) -> str:
        """
        Formats a list of schedules into string representation.
        :param schedules: List of Schedule objects
        :return: Formatted string
        """
        formatted_text = self.formatter.formatText(schedules)
        return formatted_text

    def export(self, schedules: List[Schedule], file_path: str) -> None:
        """
        Exports the formatted schedules to a specific file path.
        :param schedules: List of Schedule objects
        :param file_path: Destination file path
        """
        formatted_text = self.format(schedules)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(formatted_text)
