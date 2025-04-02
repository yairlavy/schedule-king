from abc import ABC, abstractmethod
from typing import List
from src.data.models.schedule import Schedule
from .conflict_checker import ConflictChecker
from src.data.models.course import Course
class IScheduleStrategy(ABC):
    """
    Abstract base class for schedule generation strategies.
    """

    @abstractmethod
    def generate_schedules(self, courses: List[Course]) -> List[Schedule]:
        """
        Generate all possible valid schedules from the given list of courses.

        Args:
            courses (List[Course]): The selected courses for which to generate schedules.

        Returns:
            List[Schedule]: A list of valid schedules with no conflicts.
        """
        pass
