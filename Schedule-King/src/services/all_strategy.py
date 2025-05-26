from typing import List, Iterator, Optional
from itertools import product
from src.interfaces.schedule_strategy_interface import IScheduleStrategy
from src.models.schedule import Schedule
from src.models.course import Course
from src.models.lecture_group import LectureGroup
from .MatrixConflicChecker import MatrixConflictChecker
from src.models.time_slot import TimeSlot

class AllStrategy(IScheduleStrategy):
    def __init__(self, selected: List[Course], forbidden: Optional[List[TimeSlot]] = None):
        """
        Initialize the AllStrategy with a list of selected courses.
        :param selected: List of courses to be included in the strategy.
        :raises ValueError: If more than 7 courses are selected.
        """
        if len(selected) > 7:
            raise ValueError("Cannot select more than 7 courses.")
        self._selected = selected
        self._checker = MatrixConflictChecker()
        self._Isfobidden = None # Flag to indicate if there are forbidden slots

        # Pre-fill forbidden slots if exists
        if forbidden:
            self._Isfobidden = True
            for slot in forbidden:
                self._checker.place(slot)

    def generate(self) -> Iterator[Schedule]:
        """
        Lazily generate all valid, conflict-free schedules via matrix checker.
        """
        if not self._selected:
            return # empty iterator
        yield from self._build_valid_combinations(0, [])

    def _build_valid_combinations(
        self, index: int, current: List[LectureGroup]) -> Iterator[Schedule]:
        """
        Recursive generator for valid combinations of LectureGroups.
        :param index: The index of the current course in self._selected.
        :param current: A list of LectureGroups representing the current combination.
        :param result: A list of Schedules to which the valid combinations will be appended.
        :return: Iterator[Schedule]: A generator yielding valid Schedule objects.
        """
        # Base case: if we've selected a group for every course, yield a Schedule
        if index == len(self._selected):
            if current:  # we only yield non-empty schedules
                yield Schedule(current.copy())
            return

        # Get the current course
        course = self._selected[index]
        # Use [None] if tirguls or maabadas are empty, to allow for courses without these groups
        tirguls = course.tirguls or [None]
        maabadas = course.maabadas or [None]

        found_valid_group = False

        # Iterate over all possible combinations of lecture, tirgul, and maabada for this course
        for lec, tir, lab in product(course.lectures, tirguls, maabadas):
            slots = [s for s in (lec, tir, lab) if s is not None]

            # Skip this group if any slot is forbidden or has a conflict
            if not all(self._checker.can_place(s) for s in slots):
                continue

            found_valid_group = True

            for s in slots:
                self._checker.place(s)
            current.append(LectureGroup(
                            course_name=course.name,
                            course_code=course.course_code,
                            instructor=course.instructor,
                            lecture=lec,
                            tirguls=tir,
                            maabadas=lab
                            ))

            # Recursively build combinations for the next course
            yield from self._build_valid_combinations(index + 1, current)

            # Backtrack: remove the last group and unmark the slots
            current.pop()
            for s in slots:
                self._checker.remove(s)
            
        # If no valid groups were found for this course and there is forbidden slots, we still need to recurse
        if not found_valid_group and self._Isfobidden:
            # Recurse without adding any group for this course 
            yield from self._build_valid_combinations(index + 1, current)