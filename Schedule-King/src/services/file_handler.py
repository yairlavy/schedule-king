import os
from typing import List
from src.interfaces.parser_interface import IParser
from src.interfaces.formatter_interface import IFormatter
from src.models.course import Course
from src.models.schedule import Schedule
from .text_parser import TextParser
from .text_formatter import TextFormatter

class FileHandler:
    """
    FileHandler delegates parsing and formatting based on file extensions.
    Methods are static to allow one-off parsing/formatting without instantiating.
    """
    # Dictionary mapping file extensions to their respective parser classes
    _parsers = {
        '.txt': TextParser,
    }
    # Dictionary mapping file extensions to their respective formatter classes
    _formatters = {
        '.txt': TextFormatter,
    }

    @staticmethod
    def parse(source: str) -> List[Course]:
        """
        Parses the input file into a list of Course objects.

        :param source: path to the source file
        :return: List[Course]
        :raises FileNotFoundError: if the source file does not exist
        :raises ValueError: if no parser is registered for the file extension
        """
        # Check if the source file exists
        if not os.path.exists(source):
            raise FileNotFoundError(f"Source file '{source}' not found.")
        
        # Extract the file extension
        ext = os.path.splitext(source)[1]
        
        # Get the parser class for the file extension
        parser_cls = FileHandler._parsers.get(ext)
        if not parser_cls:
            raise ValueError(f"No parser registered for extension '{ext}'.")
        
        # Instantiate the parser and parse the file
        parser: IParser = parser_cls(source)
        return parser.parse()

    @staticmethod
    def format(schedules: List[Schedule], destination: str) -> None:
        """
        Exports schedules to the specified destination file.

        :param schedules: List of Schedule objects
        :param destination: path to the output file
        :raises ValueError: if no formatter is registered for the file extension
        """
        # Ensure the destination directory exists, create it if necessary
        dest_dir = os.path.dirname(destination)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        
        # Extract the file extension
        ext = os.path.splitext(destination)[1]
        
        # Get the formatter class for the file extension
        formatter_cls = FileHandler._formatters.get(ext)
        if not formatter_cls:
            raise ValueError(f"No formatter registered for extension '{ext}'.")
        
        # Instantiate the formatter and format the schedules
        formatter: IFormatter = formatter_cls(destination)
        formatter.format(schedules)