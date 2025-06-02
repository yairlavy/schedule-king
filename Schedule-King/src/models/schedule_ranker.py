from models.schedule import Schedule
from models.grade_sorter import GradeSorter
from models.Preference import Preference, Metric

class ScheduleRanker:
    """
    This class is responsible for ranking schedules based on user-defined preferences.  
    It uses a GradeSorter to efficiently manage and retrieve schedules based on their grades.
    """
    def __init__(self):
        # List of schedules to be ranked
        self.schedules : list[Schedule] = []
        # Dictionary mapping each metric to its corresponding GradeSorter
        self.sorters: dict[Metric, GradeSorter] = {
            Metric.ACTIVE_DAYS: GradeSorter(7),        # Upper bound for active days is 7
            Metric.GAP_COUNT: GradeSorter(20),         # Upper bound for gap count is 20
            Metric.TOTAL_GAP_TIME: GradeSorter(500),   # Upper bound for total gap time
            Metric.AVG_START_TIME: GradeSorter(1200),  # Upper bound for average start time
            Metric.AVG_END_TIME: GradeSorter(1200)     # Upper bound for average end time
        }
        # Current user preference for sorting - None means all
        self.current_preference: Preference = None

    def set_preference(self, preference: Preference):
        """
        Sets the current user preference for sorting schedules.
        :param preference: A Preference object defining the sorting metric and order.
        """
        # Check if the given preference is valid and supported
        if preference.metric not in self.sorters or not preference:
            raise ValueError(f"Unsupported metric: {preference.metric}")
        # Set the current preference
        self.current_preference = preference
        
    def insert_schedule(self, schedule: Schedule):
        """
        Inserts a schedule into the appropriate GradeSorter based on the current preference.
        :param schedule: The Schedule object to insert.
        """
        # Use the index of the schedule as the item
        item = len(self.schedules)
        # Add the schedule to the list
        self.schedules.append(schedule)
        # Insert the schedule's metrics into all sorters
        self.sorters[Metric.ACTIVE_DAYS].insert(item, schedule.active_days)
        self.sorters[Metric.GAP_COUNT].insert(item, schedule.gap_count)
        self.sorters[Metric.TOTAL_GAP_TIME].insert(item, schedule.total_gap_time)
        self.sorters[Metric.AVG_START_TIME].insert(item, schedule.avg_start_time)
        self.sorters[Metric.AVG_END_TIME].insert(item, schedule.avg_end_time)

    def add_batch(self, batch: list[Schedule]):
        """
        Inserts a batch of schedules into the appropriate GradeSorter based on the current preference.
        :param batch: A list of Schedule objects to insert.
        """
        # If the batch is empty, do nothing
        if not batch:
            return
        # Extend the schedules list with the new batch
        self.schedules.extend(batch)
        # Insert each metric for all schedules in the batch into the corresponding sorter
        items_grades = [(len(self.schedules) - len(batch) + i, schedule.active_days) for i, schedule in enumerate(batch)]
        self.sorters[Metric.ACTIVE_DAYS].insert_chunk(items_grades)
        items_grades = [(len(self.schedules) - len(batch) + i, schedule.gap_count) for i, schedule in enumerate(batch)]
        self.sorters[Metric.GAP_COUNT].insert_chunk(items_grades)
        items_grades = [(len(self.schedules) - len(batch) + i, schedule.total_gap_time) for i, schedule in enumerate(batch)]
        self.sorters[Metric.TOTAL_GAP_TIME].insert_chunk(items_grades)
        items_grades = [(len(self.schedules) - len(batch) + i, schedule.avg_start_time) for i, schedule in enumerate(batch)]
        self.sorters[Metric.AVG_START_TIME].insert_chunk(items_grades)
        # Note: AVG_END_TIME is not inserted in batch mode

    def get_ranked_schedule(self, k: int = 0) -> Schedule:
        """
        Retrieves the top k schedule based on the current user preference.
        :param k: The number of top schedules to retrieve (default is 0 for all).
        :return: A list of Schedule objects sorted according to the current preference.
        """
        # Ensure k is non-negative
        if k < 0:
            raise ValueError("k must be non-negative")
        # If a preference is set, use the corresponding sorter to get the k-th item
        if self.current_preference:
            metric = self.current_preference.metric
            sorter = self.sorters[metric]
            return self.schedules[sorter.get_kth_item(k)]
        else:
            # If no preference, return the k-th schedule as is
            return self.schedules[k]