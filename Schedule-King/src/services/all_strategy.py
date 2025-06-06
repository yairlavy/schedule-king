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
        # Base case: if we've selected a group for every course, yield a Schedule
        if index == len(self._selected):
            yield Schedule(current.copy())
            return

        # Get the current course
        course = self._selected[index]
        # Use [None] if tirguls or maabadas are empty, to allow for courses without these groups
        tirguls = course.tirguls or [None]
        maabadas = course.maabadas or [None]

        # Iterate over all possible combinations of lecture, tirgul, and maabada for this course
        for lec, tir, lab in product(course.lectures, tirguls, maabadas):
            # Create a LectureGroup for this combination
            group = LectureGroup(
            course_name=course.name,
            course_code=course.course_code,
            instructor=course.instructor,
            lecture=lec,
            tirguls=tir,
            maabadas=lab
            )
            current.append(group)
            # Only proceed if the current combination does not have conflicts
            if not self._checker.has_conflict_groups(current):
            # Recursively build combinations for the next course
                yield from self._build_valid_combinations(index + 1, current)
            # Backtrack: remove the last group to try the next combination
            current.pop()

