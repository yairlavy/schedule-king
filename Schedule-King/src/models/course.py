from typing import List
from .time_slot import TimeSlot
class Course:
    """
    Represents a course with its details including lectures, tutorials, and labs.
    """
    def __init__(self, course_name: str, course_code: str, instructor: str, category: str = "default", is_detailed: bool = True,
                  lectures: List[TimeSlot] = None, tirguls: List[TimeSlot] = None, maabadas: List[TimeSlot] = None):
        self._name = course_name
        self._course_code = course_code
        self._instructor = instructor
        self._category = category
        self._is_detailed = is_detailed
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
    def category(self):
        return self._category
    @property
    def is_detailed(self):
        return self._is_detailed
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


    def copy(self, course):
        self._name = course.name
        self._instructor = course.instructor
        self._category = course.category
        self._is_detailed = course.is_detailed
        self._lectures = course.lectures
        self._tirguls = course.tirguls
        self._maabadas = course.maabadas
