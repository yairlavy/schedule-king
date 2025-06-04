# src/models/preference.py

from enum import Enum, auto
from typing import List
from src.models.lecture_group import LectureGroup
from src.models.schedule import Schedule

class Metric(Enum):
    ACTIVE_DAYS = auto()
    GAP_COUNT = auto()
    TOTAL_GAP_TIME = auto()
    AVG_START_TIME = auto()
    AVG_END_TIME = auto()

class Preference:
    """
    Represents a user-defined preference for sorting schedules.
    """
    def __init__(self, metric: Metric, ascending: bool = True):
        self.metric = metric
        self.ascending = ascending

    def key_function(self):
        """
        Returns a key function for sorting a list of Schedule objects
        based on the selected metric.
        """
        if self.metric == Metric.ACTIVE_DAYS:
            return lambda s: s.active_days
        elif self.metric == Metric.GAP_COUNT:
            return lambda s: s.gap_count
        elif self.metric == Metric.TOTAL_GAP_TIME:
            return lambda s: s.total_gap_time
        elif self.metric == Metric.AVG_START_TIME:
            return lambda s: s.avg_start_time
        elif self.metric == Metric.AVG_END_TIME:
            return lambda s: s.avg_end_time
        else:
            raise ValueError("Unsupported metric selected")
    def evaluate(self, lecture_groups: List[LectureGroup]) -> float:
        """
        Evaluates a list of LectureGroups (a schedule) based on the selected metric.

        :param lecture_groups: List of LectureGroup instances forming a schedule.
        :return: A numeric score, higher is better (for max-heap use).
        """
        schedule = Schedule(lecture_groups)
        schedule.generate_metrics()

        # Extract the value of the metric
        value = self.key_function()(schedule)

        # If ascending, lower values are better -> invert
        return -value if self.ascending else value