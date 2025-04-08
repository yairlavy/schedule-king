from abc import ABC, abstractmethod
from typing import List
from src.data.models.schedule import Schedule


class IFormatter(ABC):
    @abstractmethod
    def format(self, schedules: List[Schedule]):
        pass