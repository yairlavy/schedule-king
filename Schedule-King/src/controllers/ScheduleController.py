from src.services.schedule_api import ScheduleAPI
from src.models.schedule import Schedule
from src.models.course import Course
from typing import List, Optional
from PyQt5.QtCore import QTimer


class ScheduleController:
    def __init__(self, api: ScheduleAPI):
        """
        Initializes the ScheduleController with the given API.
        Sets up internal state for schedules, timers, and callbacks.
        """
        self.api = api
        self.schedules: List[Schedule] = []  # List to store generated schedules
        self.next = 1  # Used to determine when to notify about new schedules
        self.on_schedules_generated = lambda schedules: None  # Callback for when schedules are generated
        self.on_progress_updated = lambda current, estimated: None  # Callback for when progress is updated
        self.timer = None  # QTimer for periodic checking
        self.queue = None  # Queue for generated schedules
        self.generation_active = False  # Flag to indicate if generation is active
        self.estimated_total = -1  # Estimated total number of schedules (optional, if known)

    def generate_schedules(self, selected_courses: List[Course]) -> List[Schedule]:
        """
        Generates possible schedules using the API and saves them.
        Starts a timer to periodically check for new schedules and report progress.

        Args:
            selected_courses (List[Course]): The list of courses selected by the user.

        Returns:
            List[Schedule]: The current (initially empty) list of schedules.
        """
        self.stop_schedules_generation()  # Stop any ongoing generation
        self.schedules = []  # Reset schedules list
        self.next = 1  # Reset notification threshold

        # Start the schedule generation in parallel
        self.queue = self.api.generate_schedules_in_parallel(selected_courses)

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
        return self.schedules

    def check_for_schedules(self) -> None:
        """
        Checks if there are any schedules available in the queue.
        If available, it retrieves and stores them.
        Notifies via callbacks if new schedules are found and updates progress.
        """
        if not self.generation_active or not self.queue:
            return

        updated = False

        # Retrieve all available schedules from the queue
        while not self.queue.empty():
            try:
                schedule = self.queue.get(block=False)
                if schedule is None:
                    # None signals the generation is complete
                    self.generation_active = False
                    break
                self.schedules.append(schedule)
                updated = True
            except:
                break

        # Always notify progress update
        self.on_progress_updated(len(self.schedules), self.estimated_total)

        # Notify if enough new schedules have been added or generation is complete
        if updated and (len(self.schedules) >= self.next or not self.generation_active):
            if len(self.schedules) >= self.next:
                self.next *= 10
            self.on_schedules_generated(self.schedules)

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
        self.generation_active = False
        if self.timer and self.timer.isActive():
            self.timer.stop()
            self.timer = None

        # Clear the queue if it exists
        if self.queue:
            while not self.queue.empty():
                try:
                    self.queue.get(block=False)
                except:
                    pass

    def get_schedules(self) -> List[Schedule]:
        """
        Returns the generated schedules.

        Returns:
            List[Schedule]: The list of generated schedules.
        """
        return self.schedules

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
        schedules = schedules_to_export if schedules_to_export is not None else self.schedules
        self.api.export(schedules, file_path)
