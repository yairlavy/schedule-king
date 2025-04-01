from typing import List
from .time_slot import TimeSlot

class Course:
    """
    Represents a course with its details including lectures, tutorials, and labs.
    """
    def __init__(self, course_name: str, course_code: str, instructor: str,
                  lectures: List[TimeSlot], tirguls: List[TimeSlot], maabadas: List[TimeSlot]):
        
        self._name = course_name
        self._course_code = course_code
        self._instructor = instructor
        self._lectures = lectures
        self._tirguls = tirguls
        self._maabadas = maabadas

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
    def tirguls(self):
        return self._tirguls
    @property
    def maabadas(self):
        return self._maabadas
    
