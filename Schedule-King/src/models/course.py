from typing import List
from .time_slot import TimeSlot

class Course:
    """
    Represents a course with its details including lectures, tutorials, and labs.
    """
    def __init__(self, course_name: str, course_code: str, instructor: str,
                  lectures: List[TimeSlot] = None, tirguls: List[TimeSlot] = None, maabadas: List[TimeSlot] = None):
        
        self._name = course_name
        self._course_code = course_code
        self._instructor = instructor
        self._lectures = lectures if lectures is not None else []
        self._tirguls = tirguls if tirguls is not None else []
        self._maabadas = maabadas if maabadas is not None else []

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
    
    def add_lecture(self, lecture: TimeSlot):
        self._lectures.append(lecture)
    def add_tirgul(self, tirgul: TimeSlot):
        self._tirguls.append(tirgul)
    def add_maabada(self, maabada: TimeSlot):
        self._maabadas.append(maabada)


    def is_detailed(self):
        """Return True if the course has any lectures, tirguls, or maabadas."""
        return bool(self.lectures or self.tirguls or self.maabadas)