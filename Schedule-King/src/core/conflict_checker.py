# src/core/all_strategy.py

from typing import List
from itertools import product
from src.core.schedule_strategy_interface import IScheduleStrategy
from src.data.models.schedule import Schedule
from .conflict_checker import ConflictChecker
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup


class AllStrategy(IScheduleStrategy):
    def __init__(self, selected: List[Course]):
        """
        Initialize the strategy with selected courses and a conflict checker.
        """
        if len(selected) > 7:
            raise ValueError("Cannot select more than 7 courses.")
        self._selected = selected
        self._checker = ConflictChecker()

    def generate(self) -> List[Schedule]:
        """
        Generates all possible valid schedules from the selected courses.

        Returns:
            List[Schedule]: All valid (conflict-free) schedules.
        """
        valid_schedules = []

        all_combinations = self._generate_all_lecture_group_combinations(self._selected)

        for combination in all_combinations:
            unique_courses = {group.course_code for group in combination}

            if len(unique_courses) > 7:
                continue

            if not self._has_conflict(combination):
                valid_schedules.append(Schedule(combination))

        return valid_schedules

    def _has_conflict(self, groups: List[LectureGroup]) -> bool:
        """
        Check for any time or room conflicts among the lecture groups using ConflictChecker.
        """
        # Convert LectureGroups into temporary Course objects for conflict checking
        mock_courses = []

        for group in groups:
            mock_course = Course(
                name=group.course_name,
                course_code=group.course_code,
                instructor=group.instructor,
                lectures=[group.lecture] if group.lecture else [],
                tirguls=[group.tirguls] if group.tirguls else [],
                maabadas=[group.maabadas] if group.maabadas else [],
            )
            mock_courses.append(mock_course)

        return self._checker.find_conflicting_courses(mock_courses)

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
