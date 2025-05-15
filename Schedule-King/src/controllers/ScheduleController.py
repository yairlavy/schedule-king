from src.services.schedule_api import ScheduleAPI
from src.models.schedule import Schedule
from src.models.course import Course
from typing import List, Optional
from PyQt5.QtCore import QTimer

class ScheduleController:
    def __init__(self,api: ScheduleAPI):
        self.api = api
        self.schedules: List[Schedule] = []

    def generate_schedules(self, selected_courses: List[Course]) -> List[Schedule]:
        """
        Generates possible schedules using the API and saves them.
        """
        self.queue = self.api.generate_schedules_in_parallel(selected_courses)
        # Check for schedules every 100ms
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_schedules)
        self.timer.start(100)
        

    def check_for_schedules(self) -> None:
        """
        Checks if there are any schedules available in the queue.
        If available, it retrieves and stores them.
        """
        while not self.queue.empty():
            schedule = self.queue.get()
            if schedule is None:
                break
            self.schedules.append(schedule)

    

    
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

