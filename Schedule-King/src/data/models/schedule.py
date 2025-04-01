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
        # Creating a list of course codes from each LectureGroup object and print them
        course_codes = [lecture_group.course_code for lecture_group in self.lecture_groups]
        return f"Schedule({', '.join(course_codes)})"