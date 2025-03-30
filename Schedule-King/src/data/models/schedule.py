from .lecture_group import LectureGroup
from typing import List
from dataclasses import dataclass

@dataclass
class Schedule:
    """
    Represents a schedule.
    """
    lecture_groups: List[LectureGroup]

    def __str__(self):
        return f"Schedule({self.course_code})"