from typing import List
from itertools import product
from src.core.schedule_strategy_interface import IScheduleStrategy
from src.data.models.schedule import Schedule
from .conflict_checker import ConflictChecker
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup # Assuming this is the correct import path for LectureGroup

class AllStrategy(IScheduleStrategy):
    def __init__(self, selected: List[Course], checker: ConflictChecker):
        """
        Initialize the strategy with selected courses and a conflict checker.
        """
        if len(selected) > 7:
            raise ValueError("Cannot select more than 7 courses.")
        self._selected = selected
        self._checker = checker

def generate_schedules(self, courses: List[Course]) -> List[Schedule]:
    """
    Generates all possible valid schedules from the given list of courses.

    Note: uses the courses provided during construction (self._selected),
    and ignores the `courses` parameter to match the original UML.

    Returns:
        List[Schedule]: All valid (conflict-free) schedules.
    """
    valid_schedules = []

    # Generate all possible combinations of lecture groups (one per course)
    all_combinations = self._generate_all_lecture_group_combinations(self._selected)

    for combination in all_combinations:
        # Extract unique course codes from the combination
        unique_courses = {group.course_code for group in combination}

        # Ensure no more than 7 different courses in a schedule
        if len(unique_courses) > 7:
            continue  # Skip invalid combinations

        # Check for time/room conflicts
        if not self._has_conflict(combination):
            # Valid schedule found, add to results
            valid_schedules.append(Schedule(combination))

    return valid_schedules

    def _has_conflict(self, groups: List[LectureGroup]) -> bool:
        """
        Check for any time or room conflicts among the lecture groups.

        Returns:
            bool: True if there is a conflict, otherwise False.
        """
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                a, b = groups[i], groups[j]

                for slot_type in ["lecture", "tirguls", "maabadas"]:
                    slot_a = getattr(a, slot_type)
                    slot_b = getattr(b, slot_type)

                    if self._checker.check_time_conflict(slot_a, slot_b) or \
                        self._checker.check_room_conflict(slot_a, slot_b):
                        return True
        return False

    def _generate_all_lecture_group_combinations(self, courses: List[Course]) -> List[List[LectureGroup]]:
        """
        Create all combinations of lecture groups (one per course).
        """
        all_groups = []

        for course in courses:
            course_groups = [
                LectureGroup(
                    course_name=course.name,
                    course_code=course.course_code,
                    instructor=course.instructor,
                    lecture=lec,
                    tirguls=tir,
                    maabadas=lab
                )
                for lec, tir, lab in product(course.lectures, course.tirguls, course.maabadas)
            ]
            all_groups.append(course_groups)

        return [list(combo) for combo in product(*all_groups)]
