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
        Initialize the AllStrategy with a list of selected courses.
        :param selected: List of courses to be included in the strategy.
        :raises ValueError: If more than 7 courses are selected.
        """
        if len(selected) > 7: # Assuming a maximum of 7 courses can be selected
            raise ValueError("Cannot select more than 7 courses.")
        self._selected = selected # List of selected courses
        self._checker = ConflictChecker() # ConflictChecker instance to check for course conflicts

    def generate(self) -> List[Schedule]:
        if not self._selected: # If no courses are selected, return an empty list
            return []

        valid_schedules = [] # List to store valid schedules
        self._build_valid_combinations(0, [], valid_schedules) # Start building valid combinations from index 0
        return valid_schedules # Return the list of valid schedules

    def _build_valid_combinations(self, index: int, current: List[LectureGroup], result: List[Schedule]):
        """
        Recursive function to generate all valid combinations of LectureGroups for the selected courses.
        :param index: The index of the current course in self._selected.
        :param current: A list of LectureGroups representing the current combination.
        :param result: A list of Schedules to which the valid combinations will be appended.
        :return: None
        """

        if index == len(self._selected):
            result.append(Schedule(current[:])) # Append a copy of current to result
            return

        course = self._selected[index] # Get the current course
        tirguls = course.tirguls if course.tirguls else [None] # Get the list of tirguls or set to [None] if not available
        maabadas = course.maabadas if course.maabadas else [None] # Get the list of maabadas or set to [None] if not available

        for lec, tir, lab in product(course.lectures, tirguls, maabadas): # Generate combinations of lectures, tirguls, and maabadas
            group = LectureGroup(
                course_name=course.name,
                course_code=course.course_code,
                instructor=course.instructor,
                lecture=lec,
                tirguls=tir,
                maabadas=lab
            )
            current.append(group)

            if not self._has_conflict(current): # Check for conflicts with the current combination
                self._build_valid_combinations(index + 1, current, result) # Recur for the next course

            current.pop() # Backtrack by removing the last added group

    def _has_conflict(self, groups: List[LectureGroup]) -> bool:  # Check for conflicts with the current combination    
        courses = []
        for group in groups: # Iterate through the groups to check for conflicts
            mock_course = Course(
                course_name=group.course_name,
                course_code=group.course_code,
                instructor=group.instructor,
                lectures=[group.lecture] if group.lecture else [],
                tirguls=[group.tirguls] if group.tirguls else [],
                maabadas=[group.maabadas] if group.maabadas else [],
            )
            courses.append(mock_course) # Create a mock course for conflict checking

        return self._checker.find_conflicting_courses(courses) # Check for conflicts using the ConflictChecker
