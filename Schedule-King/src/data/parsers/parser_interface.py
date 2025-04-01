from abc import ABC, abstractmethod
from typing import List
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup 

class IParser(ABC):
    @abstractmethod
    def parse(self, raw_data: str) -> tuple[list[Course], list[LectureGroup]]:
        """
        Parses raw data and returns a tuple of:
        (list of Course objects, list of LectureGroup objects)
        """
        pass