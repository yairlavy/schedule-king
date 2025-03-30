from .parser_interface import IParser
from typing import List


class TextParser(IParser):
    def parse(self, raw_data: str) -> tuple[List[Course], List[LectureGroup]]:
        """
        Parses the given raw text data and returns courses and lecture groups.
        """
        pass  # To be implemented