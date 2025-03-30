from abc import ABC, abstractmethod
from typing import List

class IFormatter(ABC):
    @abstractmethod
    def format(self, schedules: List[Schedule]) -> str:
        pass
