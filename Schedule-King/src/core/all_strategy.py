from typing import List
from src.core.schedule_strategy_interface import IScheduleStrategy
from src.data.models.schedule import Schedule
from .conflict_checker import ConflictChecker
from src.data.models.course import Course
class AllStrategy(IScheduleStrategy):
    def __init__(self, selected: List[Course], checker: ConflictChecker):
        """
        Initialize the strategy with selected courses and a conflict checker.
        """
        self._selected = selected
        self._checker = checker
    def generate_schedules(self, courses: List[Course]) -> List[Schedule]:
        """
        Generates all possible valid schedules from the given list of courses.
        """
        pass  # To be implemented