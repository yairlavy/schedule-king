from typing import List
from itertools import product
from src.interfaces.schedule_strategy_interface import IScheduleStrategy
from src.models.schedule import Schedule
from .conflict_checker import ConflictChecker
from src.models.course import Course
from src.models.lecture_group import LectureGroup


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
        
        # return empty list if no courses provided
        if not self._selected:
            return []
        
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
        courses = []

        for group in groups:
            mock_course = Course(
                course_name=group.course_name,
                course_code=group.course_code,
                instructor=group.instructor,
                lectures=[group.lecture] if group.lecture else [],
                tirguls=[group.tirguls] if group.tirguls else [],
                maabadas=[group.maabadas] if group.maabadas else [],
            )
            courses.append(mock_course)

        return self._checker.find_conflicting_courses(courses)
    def _generate_all_lecture_group_combinations(self, courses: List[Course]) -> List[List[LectureGroup]]:
        """
        Create all combinations of lecture groups (one per course),
        where each group must include one lecture,
        and if tirguls or maabadas exist, then exactly one of each must be selected.
        """
        all_groups = []

        for course in courses:
            if not course.lectures:
                raise ValueError(f"Course '{course.course_code}' must have at least one lecture.")

            # if tirguls exist, we must choose exactly one, else None
            tirguls = course.tirguls if course.tirguls else [None]

            # if maabadas exist, we must choose exactly one, else None
            maabadas = course.maabadas if course.maabadas else [None]

            course_groups = [
                LectureGroup(
                    course_name=course.name,
                    course_code=course.course_code,
                    instructor=course.instructor,
                    lecture=lec,
                    tirguls=tir,
                    maabadas=lab
                )
                for lec, tir, lab in product(course.lectures, tirguls, maabadas)
            ]

            all_groups.append(course_groups)

        return [list(combo) for combo in product(*all_groups)]