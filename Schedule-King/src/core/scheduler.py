# src/core/scheduler.py

from typing import List
from src.data.models.course import Course
from src.data.models.schedule import Schedule
from src.core.all_strategy import StrategyAll
from src.core.conflict_checker import ConflictChecker
from src.core.schedule_strategy_interface import ISchedulerStrategy

class Scheduler:
    """
    Central class responsible for creating schedules using a scheduling strategy.
    """

    def __init__(self, selected: List[Course]):
        """
        Initialize the scheduler with the selected courses.

        Automatically uses StrategyAll and ConflictChecker internally.

        :param selected: List of courses selected by the user.
        """
        self.selected = selected
        self.strategy: ISchedulerStrategy = StrategyAll(selected, ConflictChecker())

    def generate(self) -> List[Schedule]:
        """
        Generate all valid course schedules using the assigned strategy.

        :return: List of valid, non-conflicting schedules.
        """
        return self.strategy.generate()
