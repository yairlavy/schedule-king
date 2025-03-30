from typing import List
from .time_slot import TimeSlot

class Course:
    def __init__(self, course_name: str, course_code: str, instructor: str,
                  lectures: List[TimeSlot], tutorials: List[TimeSlot], labs: List[TimeSlot]):
        
        self._name = course_name
        self._course_code = course_code
        self._instructor = instructor
        self._lectures = lectures
        self._tutorials = tutorials
        self._labs = labs

    def __str__(self):
        return f"Course({self.course_code}, {self.name}, {self.instructor})"
    
    @property
    def name(self):
        return self._name
    @property
    def course_code(self):
        return self._course_code
    @property
    def instructor(self):
        return self._instructor
    @property
    def lectures(self):
        return self._lectures
    @property
    def tutorials(self):
        return self._tutorials
    @property
    def labs(self):
        return self._labs
    
    