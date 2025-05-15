from typing import List, Iterator
from itertools import product
from src.interfaces.schedule_strategy_interface import IScheduleStrategy
from src.models.schedule import Schedule
from .conflict_checker import ConflictChecker
from src.models.course import Course
from src.models.lecture_group import LectureGroup

class AllStrategy(IScheduleStrategy):
    def __init__(self, selected: List[Course]):
        """
        Initialize the AllStrategy with a list of selected courses.
        :param selected: List of courses to be included in the strategy.
        :raises ValueError: If more than 7 courses are selected.
        """
        if len(selected) > 7:
            raise ValueError("Cannot select more than 7 courses.")
        self._selected = selected
        self._checker = ConflictChecker()

    def generate(self) -> Iterator[Schedule]:
        """
        Lazily generate all valid, conflict-free schedules.
        """
        if not self._selected:
            return  # empty iterator
        yield from self._build_valid_combinations(0, [])

    def _build_valid_combinations(
        self, index: int, current: List[LectureGroup]
    ) -> Iterator[Schedule]:
        """
        Recursive generator for valid combinations of LectureGroups.
        :param index: The index of the current course in self._selected.
        :param current: A list of LectureGroups representing the current combination.
        :param result: A list of Schedules to which the valid combinations will be appended.
        :return: Iterator[Schedule]: A generator yielding valid Schedule objects.
        """
        if index == len(self._selected):
            yield Schedule(current.copy())
            return

        course = self._selected[index]
        tirguls = course.tirguls or [None]
        maabadas = course.maabadas or [None]

        for lec, tir, lab in product(course.lectures, tirguls, maabadas):
            group = LectureGroup(
                course_name=course.name,
                course_code=course.course_code,
                instructor=course.instructor,
                lecture=lec,
                tirguls=tir,
                maabadas=lab
            )
            current.append(group)
            if not self._has_conflict(current):
                yield from self._build_valid_combinations(index + 1, current)
            current.pop()

    def _has_conflict(self, groups: List[LectureGroup]) -> bool:
        """
        Build mock Course objects from groups and delegate to ConflictChecker.
        """
        courses = [
            Course(
                course_name=g.course_name,
                course_code=g.course_code,
                instructor=g.instructor,
                lectures=[g.lecture] if g.lecture else [],
                tirguls=[g.tirguls] if g.tirguls else [],
                maabadas=[g.maabadas] if g.maabadas else [],
            )
            for g in groups
        ]
        return self._checker.find_conflicting_courses(courses)
