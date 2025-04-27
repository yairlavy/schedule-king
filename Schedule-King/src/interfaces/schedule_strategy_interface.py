# src/core/schedule_strategy_interface.py

from abc import ABC, abstractmethod
from typing import List
from src.data.models.schedule import Schedule

class IScheduleStrategy(ABC):
    """
    Abstract base class for schedule generation strategies.
    """

    @abstractmethod
    def generate(self) -> List[Schedule]:
        """
        Generate all possible valid schedules using internal state (e.g. selected courses).

        Returns:
            List[Schedule]: A list of valid, non-conflicting schedules.
        """
        pass
