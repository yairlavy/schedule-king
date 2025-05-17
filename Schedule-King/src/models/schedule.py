from .lecture_group import LectureGroup
from typing import List
from dataclasses import dataclass
from collections import defaultdict
from src.models.lecture_group import LectureGroup


DAY_NAMES = {
    "1": "Sunday",
    "2": "Monday",
    "3": "Tuesday",
    "4": "Wednesday",
    "5": "Thursday",
    "6": "Friday",
    "7": "Saturday"
}

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
    

    def extract_by_day(self):
        day_map = defaultdict(list)

        for lg in self.lecture_groups:
            # Add lecture groups
            day_map[lg.lecture.day].append(("Lecture", lg.course_name, lg.course_code, lg.lecture))
            # Add tirgul
            if lg.tirguls:
                day_map[lg.tirguls.day].append(("Tirgul", lg.course_name, lg.course_code, lg.tirguls))
            # Add maabada
            if lg.maabadas:
                day_map[lg.maabadas.day].append(("Maabada", lg.course_name, lg.course_code, lg.maabadas))

        return day_map