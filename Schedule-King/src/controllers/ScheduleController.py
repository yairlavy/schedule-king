from src.services.schedule_api import ScheduleAPI
from src.models.schedule import Schedule
from src.models.course import Course
from typing import List, Optional
from PyQt5.QtCore import QTimer
from src.models.time_slot import TimeSlot
from src.models.schedule_ranker import ScheduleRanker
from src.models.Preference import Preference, Metric

class ScheduleController:
    def __init__(self, api: ScheduleAPI):
        """
        Initializes the ScheduleController with the given API.
        Sets up internal state for schedules, timers, and callbacks.
        """
        self.api = api
        self.ranker = ScheduleRanker()  # Ranker for sorting schedules
        self.next = 1  # Used to determine when to notify about new schedules
        self.on_schedules_generated = lambda schedules: None  # Callback for when schedules are generated
        self.on_progress_updated = lambda current, estimated: None  # Callback for when progress is updated
        self.timer = None  # QTimer for periodic checking
        self.queue = None  # Queue for generated schedules
        self.generation_active = False  # Flag to indicate if generation is active
        self.estimated_total = -1  # Estimated total number of schedules (optional, if known)
        self.current_preference = None  # Current sorting preference

    def generate_schedules(self, selected_courses: List[Course], forbidden_slots: Optional[List[TimeSlot]] = None) -> List[Schedule]:
        """
        Generates possible schedules using the API and saves them.
        Starts a timer to periodically check for new schedules and report progress.

        Args:
            selected_courses (List[Course]): The list of courses selected by the user.
            forbidden_slots (Optional[List[TimeSlot]]): List of time slots that should be avoided.

        Returns:
            List[Schedule]: The current (initially empty) list of schedules.
        """
        self.stop_schedules_generation()  # Stop any ongoing generation
        self.ranker.clear()  # Clear the ranker state
        self.next = 1  # Reset notification threshold

        # Start the schedule generation in parallel (returns a queue)
        self.queue = self.api.generate_schedules_in_parallel(selected_courses, forbidden_slots)

        # Attempt to get estimated schedules count if supported by the API
        self.estimated_total = self.api.get_estimated_schedules_count(selected_courses)
        self.generation_active = True

        # Set up a timer to check for new schedules every 100ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_schedules)
        self.timer.start(100)

        # Notify immediately with empty list to show generation has started
        self.on_schedules_generated([])
        # Notify progress start
        self.on_progress_updated(0, self.estimated_total)
        return self.ranker.get_schedules()

    def check_for_schedules(self) -> None:   
        """
        Checks for new schedule batches in the queue.
        If new schedules are found, it adds them to the ranker and notifies the UI.
        """
        if not self.generation_active or not self.queue:
            return

        updated = False
        max_batch_per_loop = 100  # Number of batches to process per loop
        
        # Retrieve up to max_batches_per_loop batches from the queue
        for _ in range(max_batch_per_loop):
            if self.queue.empty():
                break
            
            try:
                schedule = self.queue.get(block=False)
                if schedule is None:  # None signals generation is complete
                    self.generation_active = False
                    # When generation is complete, set current = estimated total
                    # If we didn't have an estimate, use the actual count as both current and total
                    self.on_progress_updated(self.ranker.get_total_count(), self.ranker.get_total_count())
                    break
                self.ranker.add_batch(schedule)  # Add to the ranker for sorting
                updated = True
            except:
                break

        # Always notify progress update during active generation
        if self.generation_active:
            self.on_progress_updated(self.ranker.get_total_count(), self.estimated_total)

        # Notify UI if new schedules are added or if generation is complete
        if updated or not self.generation_active:
            self.on_schedules_generated(self.ranker.get_schedules())

        # If generation is complete, stop the timer
        if not self.generation_active:
            if self.timer:
                self.timer.stop()
                self.timer = None

    def stop_schedules_generation(self) -> None:
        """
        Stops the schedule generation process if it's running.
        Stops the timer and clears the queue.
        """
        if self.generation_active:
            self.generation_active = False
            
            # If there are schedules, make sure the progress bar shows 100% completion
            final_count = self.ranker.get_total_count()
            if final_count > 0:
                self.on_progress_updated(final_count, final_count)
            
            if self.timer and self.timer.isActive():
                self.timer.stop()
                self.timer = None

            # Terminate the process if it's still running
            self.api.stop_schedules_generation()
            
            # Clear the ranker
            self.ranker.clear()

            # Clear the queue if it exists
            if self.queue:
                while not self.queue.empty():
                    try:
                        self.queue.get(block=False)
                    except:
                        pass

    def set_preference(self, preference: Optional[Preference]) -> None:
        """
        Sets the current sorting preference for schedules.
        
        Args:
            preference (Optional[Preference]): The preference to set, or None for insertion order.
        """
        self.current_preference = preference
        self.ranker.set_preference(preference)
        # Notify UI of the updated schedule order
        self.on_schedules_generated(self.ranker.get_schedules())

    def get_current_preference(self) -> Optional[Preference]:
        """
        Returns the current sorting preference.
        
        Returns:
            Optional[Preference]: The current preference or None if using insertion order.
        """
        return self.current_preference

    def get_schedules(self) -> List[Schedule]:
        """
        Returns the generated schedules according to the current preference.

        Returns:
            List[Schedule]: The list of generated schedules.
        """
        return self.ranker.get_schedules()

    def get_ranked_schedules(self, start: int = 0, count: Optional[int] = None) -> List[Schedule]:
        """
        Returns a range of schedules according to the current preference.

        Args:
            start (int): Starting index (0-based).
            count (Optional[int]): Number of schedules to retrieve. If None, retrieves all from start.

        Returns:
            List[Schedule]: List of Schedule objects in the requested range.
        """
        return self.ranker.get_ranked_schedules(start, count)

    def export_schedules(self, file_path: str, schedules_to_export: Optional[List[Schedule]] = None) -> None:
        """
        Exports the schedules to a file.

        Args:
            file_path (str): The path to save the file.
            schedules_to_export (Optional[List[Schedule]]): Specific schedules to export.
                If None, exports all schedules.

        Raises:
            Exception: If the export operation fails.
        """
        schedules = schedules_to_export if schedules_to_export is not None else self.ranker.get_schedules()
        # Use the API's export method to save the schedules to the specified file
        self.api.export(schedules, file_path)