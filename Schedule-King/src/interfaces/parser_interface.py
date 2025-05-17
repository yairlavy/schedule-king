from abc import ABC, abstractmethod
from typing import List
from src.models.course import Course
from src.models.lecture_group import LectureGroup 

class IParser(ABC):
    @abstractmethod
    def parse(self) -> list[Course]:
        """
        Parses the data and returns a list of Course objects.
        (list of Course objects)
        """
        pass