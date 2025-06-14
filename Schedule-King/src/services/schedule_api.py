import os
from typing import List, Optional
from .file_handler import FileHandler
from .scheduler import Scheduler
from .all_strategy import AllStrategy
from src.models.course import Course
from src.models.schedule import Schedule
import multiprocessing as mp
from src.models.time_slot import TimeSlot

class ScheduleAPI:
    def __init__(self):
        """
        Initialize ScheduleAPI with a format/parse handler.
        """
        self.file_handler = FileHandler()
        self._process_worker = None
        # No shared state needed here anymore

    def get_courses(self, source: str) -> List[Course]:
        """
        Parse and return all courses from the given source file.
        """
        if not os.path.exists(source):
            raise FileNotFoundError(f"The source file '{source}' does not exist.")
        try:
            return self.file_handler.parse(source)
        except ValueError as e:
            print(f"Error parsing courses: {e}. Please check the input format.")
            return []

    def process(self, selected_courses: List[Course]) -> List[Schedule]:
        """
        Generate schedules based on selected courses.
        """
        scheduler = Scheduler(selected_courses, AllStrategy(selected_courses))
        return list(scheduler.generate())

    def export(self, schedules: List[Schedule], destination: str) -> None:
        """
        Export the given schedules to the destination file.
        """
        try:
            self.file_handler.format(schedules, destination)
            print(f"Schedules successfully exported to {destination}.")
        except ValueError as e:
            print(f"Error exporting schedules: {e}.")

    @staticmethod
    def _worker_generate(selected_courses: List[Course], queue: mp.Queue, stop_event: mp.Event, forbidden: Optional[List[TimeSlot]] = None) -> None:
        """
        Worker function to process courses in a separate process, sending schedules in variable batch sizes.
        Checks stop_event to gracefully terminate when requested.
        """
        scheduler = Scheduler(selected_courses, AllStrategy(selected_courses, forbidden))
        
        batch_sizes = [1, 9, 90, 900]
        batch_index = 0
        current_batch_size = batch_sizes[batch_index] if batch_index < len(batch_sizes) else 1000
        batch = []
        total_sent = 0

        for schedule in scheduler.generate():
            if stop_event.is_set():
                break

            batch.append(schedule)
            if len(batch) >= current_batch_size:
                queue.put(batch)
                total_sent += len(batch)
                batch = []
                batch_index += 1
                current_batch_size = batch_sizes[batch_index] if batch_index < len(batch_sizes) else 1000

                if stop_event.is_set():
                    break

        if batch and not stop_event.is_set():
            queue.put(batch)

        if not stop_event.is_set():
            queue.put(None)

    def generate_schedules_in_parallel(self, selected_courses: List[Course], forbidden: Optional[List[TimeSlot]] = None) -> List[Schedule]:
        """
        Generate schedules in parallel using multiple processes.
        """
        queue = mp.Queue()
        # Create a proper Event object for signaling termination
        stop_event = mp.Event()
        
        # Split the courses among the processes
        # For simplicity, we are using a single process here.
        if self._process_worker and self._process_worker.is_alive():
            self.stop_schedules_generation()
            self._process_worker = None
            
        # Start a new process for schedule generation
        self._process_worker = mp.Process(target=self._worker_generate, 
                                  args=(selected_courses, queue, stop_event, forbidden),
                                  daemon=True)
        # Store the stop event with the process
        self._process_worker.stop_event = stop_event
        self._process_worker.start()

        return queue
    
    def get_estimated_schedules_count(self, selected_courses: List[Course]) -> int:
        """
        Estimate the theoretical number of combinations (without considering conflicts).
        Returns:
            int: Estimated number of possible combinations, or a very large number if overflow occurs.
        """
        try:
            total = 1

            for course in selected_courses:
                lectures = len(course.lectures)
                tirguls = len(course.tirguls) if course.tirguls else 1
                maabadas = len(course.maabadas) if course.maabadas else 1
                total *= lectures * tirguls * maabadas
                # Check for overflow
            return total if total < 10**7 and total > 0  else -1
        except Exception:
            return -1
        
    def stop_schedules_generation(self) -> None:
        """
        Stop the schedule generation process if it's running.
        Uses the process-specific Event object to signal termination.
        Does not block or join the process.
        """
        # Signal the worker to stop
        if self._process_worker and hasattr(self._process_worker, 'stop_event'):
            self._process_worker.stop_event.set()
            
        # Let the process terminate on its own - don't join
        # The daemon=True setting will ensure cleanup when the main app exits