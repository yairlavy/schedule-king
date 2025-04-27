from typing import List
from src.data.models.course import Course
from src.data.models.schedule import Schedule
from src.data.parsers.text_parser import TextParser
from src.data.formatters.text_formatter import TextFormatter
import os

class FileHandler:
    def __init__(self, source: str, destination: str):
        """
        Initialize the FileHandler with a parser and a formatter.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"The source file '{source}' does not exist.")
        self.parser = TextParser(source)
        self.formatter = TextFormatter(destination)

    def parse(self) -> List[Course]:
        """
        Parses the input data into courses and lecture groups.

        :param raw_data: Raw text input from file or user
        :return: Tuple (List[Course], List[LectureGroup])
        """
        return self.parser.parse()

    def format(self, schedules: List[Schedule]) -> str:
        """
        Formats a list of schedules into string representation and exports the file.
        :param schedules: List of Schedule objects
        :return: Formatted string
        """
        # First generate the formatted text
        formatted_text = self.formatter.formatText(schedules)
        # Export the formatted text to the destination file
        self.formatter.export(schedules, file_path=self.formatter.path)
        # Return the formatted text so that process() does not return None.
        return formatted_text