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

        # Pre-fill forbidden slots if exists
        if forbidden:
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
                schedule = Schedule(current.copy())
                schedule.generate_metrics()
                yield schedule
            return

        # Get the current course
        course = self._selected[index]
        
        # Default to [None] if no tirguls or maabadas
        tirguls = course.tirguls or [None]
        maabadas = course.maabadas or [None]

        # Iterate over all possible combinations of lecture, tirgul, and maabada for this course
        for lecture, tirgul, maabada in product(course.lectures, tirguls, maabadas):
            # Flatten the slots into a single list
            all_slots = [slot for group in (lecture, tirgul, maabada) if group for slot in group]

            # Check for internal conflicts using a temporary matrix if it have then skip this group
            temp_checker = MatrixConflictChecker()
            if not all(temp_checker.can_place(slot) and (temp_checker.place(slot) or True) for slot in all_slots):
                continue

            # Skip this group if any slot is forbidden or has a conflict
            if not all(self._checker.can_place(slot) for slot in all_slots):
                continue

            #  Place the slots in the main matrix
            for slot in all_slots:
                self._checker.place(slot)

            # Add the current group to the combination
            current.append(LectureGroup(
                            course_name=course.name,
                            course_code=course.course_code,
                            instructor=course.instructor,
                            lecture=lecture,
                            tirguls=tirgul,
                            maabadas=maabada
                            ))

            # Recursively build combinations for the next course
            yield from self._build_valid_combinations(index + 1, current)

            # Backtrack: remove the last group and unmark the slots
            current.pop()
            for slot in all_slots:
                self._checker.remove(slot)