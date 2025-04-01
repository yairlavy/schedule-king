from .parser_interface import IParser
from typing import List
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup 

class TextParser(IParser):
    def parse(self, raw_data: str) -> tuple[List[Course], List[LectureGroup]]:
        """
        Parses the given raw text data and returns courses and lecture groups.
        """
        pass  # To be implemented