from .schedule_strategy_interface import IScheduleStrategy
from typing import List

class AllStrategy(IScheduleStrategy):
    def generate_schedules(self, courses: List[Course]) -> List[Schedule]:
        """
        Generates all possible valid schedules from the given list of courses.
        """
        pass  # To be implemented