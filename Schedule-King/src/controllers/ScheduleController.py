from src.services.schedule_api import ScheduleAPI
from src.models.schedule import Schedule
from src.models.course import Course
from typing import List, Optional
from PyQt5.QtCore import QTimer

class ScheduleController:
    def __init__(self,api: ScheduleAPI):
        self.api = api
        self.schedules: List[Schedule] = []
        self.next = 1
        self.on_schedules_generated = lambda schedules: None
        self.timer = None
        self.queue = None
        self.generation_active = False


    def generate_schedules(self, selected_courses: List[Course]) -> List[Schedule]:
        """
        Generates possible schedules using the API and saves them.
        """
        self.stop_schedules_generation()
        self.schedules = []
        self.next = 1
        # Start the schedule generation
        self.queue = self.api.generate_schedules_in_parallel(selected_courses)
        self.generation_active = True
        # Check for schedules every 100ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_schedules)
        self.timer.start(100)

        return self.schedules
        

    def check_for_schedules(self) -> None:
        """
        Checks if there are any schedules available in the queue.
        If available, it retrieves and stores them.
        """
        if not self.generation_active or not self.queue:
            return
            
        updated = False
        while not self.queue.empty():
            schedule = self.queue.get()
            if schedule is None:
                break
            self.schedules.append(schedule)
            updated = True

        if updated and (len(self.schedules) > self.next or not self.generation_active):
            if len(self.schedules) >= self.next:
                self.next *= 10
            self.on_schedules_generated(self.schedules)

    def stop_schedules_generation(self) -> None:
        """
        Stops the schedule generation process if it's running.
        """
        self.generation_active = False
        if self.timer and self.timer.isActive():
            self.timer.stop()
            self.timer = None
        
        # Clear the queue if it exists
        if self.queue:
            while not self.queue.empty():
                try:
                    # Attempt to get items from the queue to clear it
                    self.queue.get(block=False)
                except:
                    pass


    def get_schedules(self) -> List[Schedule]:
        """
        Returns the generated schedules.
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

