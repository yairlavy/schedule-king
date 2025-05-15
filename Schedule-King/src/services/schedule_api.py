import os
from typing import List
from .file_handler import FileHandler
from .scheduler import Scheduler
from .all_strategy import AllStrategy
from src.models.course import Course
from src.models.schedule import Schedule
import multiprocessing as mp

class ScheduleAPI:
    def __init__(self):
        """
        Initialize ScheduleAPI with a format/parse handler.
        """
        self.file_handler = FileHandler()

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
    def _worker_generate(selected_courses: List[Course], queue: mp.Queue) -> None:
        """
        Worker function to process courses in a separate process.
        """
        scheduler = Scheduler(selected_courses, AllStrategy(selected_courses))
        for schedule in scheduler.generate():
            queue.put(schedule)
        queue.put(None)  # Signal that this worker is done

    def generate_schedules_in_parallel(self, selected_courses: List[Course]) -> List[Schedule]:
        """
        Generate schedules in parallel using multiple processes.
        """
        queue = mp.Queue()
        # Split the courses among the processes
        process = mp.Process(target=self._worker_generate, args=(selected_courses, queue) , daemon=True)
        process.start()

        return queue
    
    def get_estimated_schedules_count(self, selected_courses: List[Course]) -> int:
        """
        Estimate the theoretical number of combinations (without considering conflicts).
        Returns:
            int: Estimated number of possible combinations, or -1 if unknown.
        """
        try:
            total = 1
            for course in selected_courses:
                lectures = len(course.lectures)
                tirguls = len(course.tirguls) if course.tirguls else 1
                maabadas = len(course.maabadas) if course.maabadas else 1
                total *= lectures * tirguls * maabadas
            return total if total > 0 else -1
        except Exception as e:
            print(f"Error estimating combinations: {e}")
            return -1
