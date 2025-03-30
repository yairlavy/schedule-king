from abc import ABC, abstractmethod
from typing import List

class IScheduleStrategy(ABC):
    @abstractmethod
    def generate_schedules(self, courses: List[Course]) -> List[Schedule]:
        """
        Generate all possible valid schedules from the given courses.
        """
        pass