from typing import List, Iterator, Optional
from itertools import product
from src.interfaces.schedule_strategy_interface import IScheduleStrategy
from src.models.schedule import Schedule
from src.models.course import Course
from src.models.lecture_group import LectureGroup
from .MatrixConflicChecker import MatrixConflictChecker
from src.models.time_slot import TimeSlot
from src.models.preferred_schedule_matrix import PreferredScheduleMatrix  

class AllStrategy(IScheduleStrategy):
    def __init__(self, 
                 selected: List[Course],
                 forbidden: Optional[List[TimeSlot]] = None,
                 preferred: Optional[List[TimeSlot]] = None):
        """
        Initialize the AllStrategy with a list of selected courses.
        :param selected: List of courses to be included in the strategy.
        :param forbidden: List of time slots to avoid completely.
        :param preferred: List of preferred time slots (used for scoring schedules).
        :raises ValueError: If more than 7 courses are selected.
        """
        if len(selected) > 7:
            raise ValueError("Cannot select more than 7 courses.")
        
        self._selected = selected
        self._checker = MatrixConflictChecker()
        self._preferred_matrix = None

        # Place forbidden slots in the matrix so they are treated as conflicts
        if forbidden:
            for slot in forbidden:
                self._checker.place(slot)

        # Only add preferred slots to the preference matrix
        # Forbidden slots are handled by conflict checking, not preference scoring
        if preferred:
            self._preferred_matrix = PreferredScheduleMatrix()
            for slot in preferred:
                self._preferred_matrix.add_preferred(slot)
        else:
            self._preferred_matrix = None

    def generate(self) -> Iterator[Schedule]:
        """
        Lazily generate all valid, conflict-free schedules using backtracking.
        :return: Iterator yielding valid Schedule objects.
        """
        if not self._selected:
            return  # Return empty iterator
        yield from self._build_valid_combinations(0, [])

    def _build_valid_combinations(
        self, index: int, current: List[LectureGroup]) -> Iterator[Schedule]:
        """
        Recursive generator that builds all valid lecture group combinations.
        :param index: The current course index.
        :param current: Accumulated lecture groups (one per course).
        :yield: Valid, conflict-free Schedule object.
        """
        # If all courses are assigned, yield a new schedule
        if index == len(self._selected):
            if current:
                schedule = Schedule(current.copy())
                # Score based on preferred matrix if available
                if self._preferred_matrix:
                    schedule.preference_score = schedule.compute_preference_score(self._preferred_matrix)  
                schedule.generate_metrics()
                yield schedule
            return

        # Get current course
        course = self._selected[index]

        # If there are no lectures, tirguls or maabadas, use [None] so we can still loop
        lectures  = [lec for lec in course.lectures  if lec]  or [None]
        tirguls = [t for t in course.tirguls if t] or [None]
        maabadas = [m for m in course.maabadas if m] or [None]
        
        # if all of them are empty, skip this option by advancing the index
        if not lectures and not tirguls and not maabadas:
            yield from self._build_valid_combinations(index + 1, current)
            return
        
        # Try every possible combination of lecture, tirgul, and maabada
        for lecture, tirgul, maabada in product(lectures, tirguls, maabadas):
            # Combine all timeslots into a flat list
            all_slots = [slot for group in (lecture, tirgul, maabada) if group for slot in group]

            # Check for internal conflicts within the same course
            temp_checker = MatrixConflictChecker()
            if not all(temp_checker.can_place(slot) and (temp_checker.place(slot) or True) for slot in all_slots):
                continue

            # Check if these slots conflict with already placed courses
            if not all(self._checker.can_place(slot) for slot in all_slots):
                continue

            # Place slots in the global conflict checker
            for slot in all_slots:
                self._checker.place(slot)

            # so it not crash if any of them is empty
            lec_list    = lecture  or []
            tirgul_list = tirgul   or []
            mabada_list = maabada  or []

            # Add current group to the partial solution
            current.append(LectureGroup(
                course_name=course.name,
                course_code=course.course_code,
                instructor=course.instructor,
                lecture=lec_list,
                tirguls=tirgul_list,
                maabadas=mabada_list
            ))

            # Recursively try to build the rest of the schedule
            yield from self._build_valid_combinations(index + 1, current)

            # Backtrack: remove last group and its times from the matrix
            current.pop()
            for slot in all_slots:
                self._checker.remove(slot)
