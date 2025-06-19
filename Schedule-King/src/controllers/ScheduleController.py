from src.services.schedule_api import ScheduleAPI
from src.models.schedule import Schedule
from src.models.course import Course
from typing import List, Optional
from PyQt5.QtCore import QTimer
from src.models.schedule_ranker import ScheduleRanker
from src.models.time_slot import TimeSlot
from src.models.Preference import Preference, Metric
from datetime import datetime, timedelta
from src.services.GoogleCalenderManager import GoogleCalendarManager

class ScheduleController:
    def __init__(self, api: ScheduleAPI):
        """
        Initializes the ScheduleController with the given API.
        Sets up internal state for schedules, timers, and callbacks.
        """
        self.api = api
        self.ranker = ScheduleRanker() 
        self.next = 1  # Used to determine when to notify about new schedules
        self.on_schedules_generated = lambda schedules: None  # Callback for when schedules are generated
        self.on_progress_updated = lambda current, estimated: None  # Callback for when progress is updated
        self.timer = None  # QTimer for periodic checking
        self.queue = None  # Queue for generated schedules
        self.generation_active = False  # Flag to indicate if generation is active
        self.estimated_total = -1  # Estimated total number of schedules (optional, if known)
        self.google_calendar_manager = None  # Google Calendar manager for exporting schedules

    def generate_schedules(self, selected_courses: List[Course], forbidden_slots: Optional[List[TimeSlot]] = None) -> List[Schedule]:
        """
        Generates possible schedules using the API and saves them.
        Starts a timer to periodically check for new schedules and report progress.

        Args:
            selected_courses (List[Course]): The list of courses selected by the user.

        Returns:
            List[Schedule]: The current (initially empty) list of schedules.
        """
        self.stop_schedules_generation()  # Stop any ongoing generation
        self.ranker.clear()  # Reset the ranker state
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

        # Notify immediately with no schedule to show generation has started
        self.on_schedules_generated(0)
        # Notify progress start
        self.on_progress_updated(0, self.estimated_total)
        return self.ranker.get_schedules()

    def check_for_schedules(self) -> None:   
        """
        Checks for new schedule batches in the queue.
        If new schedules are found, it appends them to the list and notifies the UI.
        """
        if not self.generation_active or not self.queue:
            return

        updated = False
        max_batch_per_loop = 100 # Number of batches to process per loop
        
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
                    self.on_progress_updated(len(self.ranker.get_schedules()), len(self.ranker.get_schedules()))
                    break
                self.ranker.add_batch(schedule)  # Append the batch to the schedules list
                updated = True
            except:
                break

        # Always notify progress update during active generation
        if self.generation_active:
            self.on_progress_updated(self.ranker.size(), self.estimated_total)

        # Notify UI if new schedules are added or if generation is complete
        if updated or not self.generation_active:
            self.on_schedules_generated(self.ranker.size())

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
            if self.ranker.get_schedules() and self.ranker.size() > 0:
                final_count = self.ranker.size()
                self.on_progress_updated(final_count, final_count)
            
            if self.timer and self.timer.isActive():
                self.timer.stop()
                self.timer = None

            # Terminate the process if it's still running
            self.api.stop_schedules_generation()
            # Clear the schedules list
            self.ranker.clear()

            # Clear the queue if it exists
            if self.queue:
                while not self.queue.empty():
                    try:
                        self.queue.get(block=False)
                    except:
                        pass
        
    def clear_preference(self) -> None:
        """
        Clears the current preference, returning schedules to insertion order.
        """
        self.ranker.set_preference(None)
        # Notify the UI that the schedules have been updated
        self.on_schedules_generated(self.ranker.size())

    def set_preference(self, metric: Metric, ascending: bool) -> None:
        """
        Sets the user's preference for sorting schedules.
        If metric is None, clears the preference (insertion order).

        Args:
            metric: The metric to sort by (e.g., Metric.COST, Metric.TIME), or None for insertion order.
            ascending (bool): True for ascending order, False for descending.

        Raises:
            ValueError: If the metric is not recognized.
        """
        if metric is None:
            self.clear_preference()
        else:
            self.ranker.set_preference(Preference(metric, ascending))
            # Notify the UI that the schedules have been updated
            self.on_schedules_generated(self.ranker.size())
    
    def get_current_preference(self) -> Optional[Preference]:
        """
        Returns the current user preference for sorting schedules.

        Returns:
            Optional[Preference]: The current preference, or None if no preference is set.
        """
        return self.ranker.current_preference

    def get_kth_schedule(self, k: int) -> Schedule:
        """
        Retrieves the k-th schedule based on the current user preference.

        Args:
            k (int): The index of the schedule to retrieve (0-based).

        Returns:
            Schedule: The k-th Schedule object according to the current preference.

        Raises:
            IndexError: If k is out of bounds for the number of schedules.
        """
        if k < 0 or k >= self.ranker.size():
            raise IndexError(f"k={k} is out of bounds for {self.ranker.size()} schedules")
        # Use the ranker to get the k-th schedule based on the current preference
        return self.ranker.get_ranked_schedule(k)
    
    def get_ranked_schedules(self, count: int, start: int = 0):
        """
        Returns a slice of ranked schedules.

        Args:
            count (int): Number of schedules to return.
            start (int): Starting index.

        Returns:
            List[Schedule]: The list of ranked schedules.
        """
        return self.ranker.get_ranked_schedules(start,count)

    def get_schedules(self) -> List[Schedule]:
        """
        Returns the generated schedules.

        Returns:
            List[Schedule]: The list of generated schedules.
        """
        return self.ranker.get_schedules()

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
        if not file_path:
            raise ValueError("File path must be specified for export")
        if schedules_to_export is None or len(schedules_to_export) == 0:
            # If no specific schedules are provided, export all schedules
            raise ValueError("No schedules provided for export. Please specify schedules to export.")
        # Use the API's export method to save the schedules to the specified file
        self.api.export(schedules_to_export, file_path)

    def export_to_calendar(self, schedule: Schedule) -> None:
            """
            Exports a given schedule as events to the user's Google Calendar.
            :param schedule: The Schedule object to export.
            """
            # Ensure the GoogleCalendarManager is initialized
            if self.google_calendar_manager is None:
                try:
                    self.google_calendar_manager = GoogleCalendarManager()
                except Exception as e:
                    print(f"Error initializing Google Calendar Manager: {e}")
                    # Raise the error to the UI to display a message to the user
                    raise

            # Use the existing method in the Schedule model to extract lessons by day
            daily_slots = schedule.extract_by_day()

            # Start date for export (e.g., the current week). Can be adjusted as needed.
            # Start from the upcoming Sunday.
            today = datetime.now()
            # Find the upcoming Sunday (weekday 6)
            start_date_for_export = today - timedelta(days=today.weekday()) + timedelta(days=6)
            if today.weekday() == 6:  # If today is Saturday
                start_date_for_export = today  # Start from today

            # Export events for 12 weeks ahead to create recurring events
            num_weeks_to_export = 12

            for week_offset in range(num_weeks_to_export):
                current_week_start_date = start_date_for_export + timedelta(weeks=week_offset)

                # Map day numbers (1-7) to English weekday numbers.
                # Adjust this to match datetime.weekday() (0=Monday) and your day numbers (1=Sunday).
                # Conversion: 1 (Sunday) -> 6 (Sunday), 2 (Monday) -> 0 (Monday), ..., 7 (Saturday) -> 5 (Saturday)
                day_mapping_for_weekday = {
                    "1": 6,  # Sunday
                    "2": 0,  # Monday
                    "3": 1,  # Tuesday
                    "4": 2,  # Wednesday
                    "5": 3,  # Thursday
                    "6": 4,  # Friday
                    "7": 5   # Saturday
                }

                for day_num_str, slots in daily_slots.items():
                    # Calculate the specific date for the lesson day in the current week
                    day_of_week_int = day_mapping_for_weekday.get(day_num_str)
                    if day_of_week_int is None:
                        print(f"Warning: Unknown day: {day_num_str}. Skipping.")
                        continue

                    # Find the start date of the week (Monday)
                    week_start = current_week_start_date - timedelta(days=current_week_start_date.weekday())

                    # Calculate the exact date for the lesson day in this week
                    lesson_date = week_start + timedelta(days=day_of_week_int)

                    for slot_type, course_name, course_code, slot_obj in slots:
                        # Use the start and end time from slot_obj
                        # slot_obj.start_time and slot_obj.end_time are likely datetime.time objects
                        # Combine them with lesson_date to create full datetime objects

                        start_datetime = datetime.combine(lesson_date, slot_obj.start_time)
                        end_datetime = datetime.combine(lesson_date, slot_obj.end_time)

                        # ISO 8601 format for Google API
                        start_time_iso = start_datetime.isoformat()
                        end_time_iso = end_datetime.isoformat()

                        title = f"{course_name} - {slot_type}"
                        description = f"Course: {course_name} ({course_code})\nType: {slot_type}"
                        
                        # Safely add location if it exists
                        location = getattr(slot_obj, 'location', None) or getattr(slot_obj, 'room', None)
                        if location:
                            description += f"\nLocation: {location}"
                        
                        # Safely add lecturer if it exists
                        lecturer = getattr(slot_obj, 'lecturer', None) or getattr(slot_obj, 'instructor', None)
                        if lecturer:
                            description += f"\nLecturer: {lecturer}"
                        
                        # Create the event in Google Calendar
                        self.google_calendar_manager.create_event(
                            summary=title,
                            description=description,
                            start_time=start_time_iso,
                            end_time=end_time_iso
                        )
            print("Export to calendar completed successfully.")