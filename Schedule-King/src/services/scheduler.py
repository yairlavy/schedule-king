# src/core/scheduler.py

from typing import List
from src.models.course import Course
from src.models.schedule import Schedule
from src.interfaces.schedule_strategy_interface import IScheduleStrategy

class Scheduler:
    """
    Central class responsible for generating course schedules using a flexible strategy.
    """

    def __init__(self, selected: List[Course], strategy: IScheduleStrategy):
        """
        Initialize the scheduler with selected courses and a strategy.

        :param selected: List of courses selected by the user.
        :param strategy: Any strategy that implements IScheduleStrategy (e.g., AllStrategy, SmartStrategy).
        """
        self.selected = selected
        self.strategy = strategy

    def generate(self) -> List[Schedule]:
        """
        Generate all valid schedules using the provided strategy.

        :return: A list of valid, conflict-free schedules.
        """
        return self.strategy.generate()