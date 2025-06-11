from src.models.schedule import Schedule
from src.models.grade_sorter import GradeSorter
from src.models.Preference import Preference, Metric
from typing import List, Optional, Iterator

class ScheduleRanker:
    """
    This class is responsible for ranking schedules based on user-defined preferences.  
    It uses a GradeSorter to efficiently manage and retrieve schedules based on their grades.
    """
    def __init__(self):
        # List of schedules to be ranked
        self.schedules: List[Schedule] = []
        # Dictionary mapping each metric to its corresponding GradeSorter
        self.sorters: dict[Metric, GradeSorter] = {
            Metric.ACTIVE_DAYS: GradeSorter(7),        # Upper bound for active days is 7
            Metric.GAP_COUNT: GradeSorter(20),         # Upper bound for gap count is 20
            Metric.TOTAL_GAP_TIME: GradeSorter(64),    # Upper bound for total gap time in helf of hours
            Metric.AVG_START_TIME: GradeSorter(1440),  # Upper bound for average start time in minutes (24*60)
            Metric.AVG_END_TIME: GradeSorter(1440)     # Upper bound for average end time in minutes (24*60)
        }
        # Current user preference for sorting - None means insertion order
        self.current_preference: Optional[Preference] = None

    def set_preference(self, preference: Optional[Preference]):
        """
        Sets the current user preference for sorting schedules.
        :param preference: A Preference object defining the sorting metric and order, or None for insertion order.
        """
        if preference is not None and preference.metric not in self.sorters:
            raise ValueError(f"Unsupported metric: {preference.metric}")
        self.current_preference = preference
        
    def insert_schedule(self, schedule: Schedule):
        """
        Inserts a schedule into all GradeSorters.
        :param schedule: The Schedule object to insert.
        """
        # Use the index of the schedule as the item
        item = len(self.schedules)
        # Add the schedule to the list
        self.schedules.append(schedule)
        
        # Insert the schedule's metrics into all sorters
        # Each metric is converted to an integer grade for sorting
        self.sorters[Metric.ACTIVE_DAYS].insert(item, int(schedule.active_days))
        self.sorters[Metric.GAP_COUNT].insert(item, int(schedule.gap_count))
        # Total gap time is in hours, store as half-hours for grading
        self.sorters[Metric.TOTAL_GAP_TIME].insert(item, int(schedule.total_gap_time * 2))
        # Average times are in 700 format float, convert to minutes for grading
        self.sorters[Metric.AVG_START_TIME].insert(item, Schedule.time_format_to_minutes(int(schedule.avg_start_time)))
        self.sorters[Metric.AVG_END_TIME].insert(item, Schedule.time_format_to_minutes(int(schedule.avg_end_time)))


    def add_batch(self, batch: List[Schedule]):
        """
        Adds a batch of schedules to the ranker and updates all GradeSorters efficiently.
        :param batch: List of Schedule objects to add.
        """
        start_index = len(self.schedules)
        # Extend the schedules list with the new batch
        self.schedules.extend(batch)
        # Map each metric to its index in the Schedule.metric_tuple based on enum order
        metric_to_index = {metric: idx for idx, metric in enumerate(Metric)}
        # For each metric, insert the corresponding grades for the batch into the sorter
        for metric, idx in metric_to_index.items():
            # Prepare (item_index, grade) pairs for the batch
            self.sorters[metric].insert_chunk(
                ((start_index + i, schedule.metric_tuple[idx]) for i, schedule in enumerate(batch))
            )


    def get_ranked_schedule(self, k: int) -> Schedule:
        """
        Retrieves the k-th schedule based on the current user preference.
        :param k: The index of the schedule to retrieve (0-based).
        :return: The k-th Schedule object according to the current preference.
        """
        if k < 0 or k >= len(self.schedules):
            raise IndexError(f"k={k} is out of bounds for {len(self.schedules)} schedules")
            
        # If no preference is set, return in insertion order
        if self.current_preference is None:
            return self.schedules[k]
            
        # Get the sorter and handle ascending/descending order
        metric = self.current_preference.metric
        sorter = self.sorters[metric]
        
        if self.current_preference.ascending:
            # Normal order: k-th smallest
            schedule_index = sorter.get_kth_item(k)
        else:
            # Reverse order: k-th largest = (total-1-k)-th smallest
            reverse_k = len(self.schedules) - 1 - k
            schedule_index = sorter.get_kth_item(reverse_k)
            
        return self.schedules[schedule_index]
    
    def get_ranked_schedules(self, start: int = 0, count: Optional[int] = None) -> List[Schedule]:
        """
        Retrieves a range of schedules based on the current preference.
        :param start: Starting index (0-based).
        :param count: Number of schedules to retrieve. If None, retrieves all from start.
        :return: List of Schedule objects in the requested range.
        """
        if count is None:
            count = len(self.schedules) - start
            
        if start < 0 or start >= len(self.schedules):
            raise IndexError(f"start={start} is out of bounds")
            
        end = min(start + count, len(self.schedules))
        # Collect the schedules in ranked order
        return [self.get_ranked_schedule(i) for i in range(start, end)]
    
    def iter_ranked_schedules(self) -> Iterator[Schedule]:
        """
        Returns an iterator over all schedules in ranked order.
        :return: Iterator yielding Schedule objects in ranked order.
        """
        for i in range(len(self.schedules)):
            yield self.get_ranked_schedule(i)
    
    def size(self) -> int:
        """
        Returns the total number of schedules.
        :return: Total number of schedules.
        """
        return len(self.schedules)
    
    def clear(self):
        """
        Clears all schedules and resets the ranker.
        """
        self.schedules.clear()
        # Reset all sorters
        for metric in Metric:
            self.sorters[metric] = GradeSorter(self.sorters[metric].upper_bound)
        
    def get_schedules(self) -> List[Schedule]:
        """
        Returns the list of all schedules.
        :return: List of Schedule objects.
        """
        return self.schedules.copy()