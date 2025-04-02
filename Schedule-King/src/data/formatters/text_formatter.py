from typing import List
from .formatter_interface import IFormatter
from ..models.schedule import Schedule

class TextFormatter(IFormatter):
    
    def __init__(self, schedules: List[Schedule]):
        """
        Initialize the TextFormatter.
        :param schedules: A list of Schedule objects.
        """
        self.schedules = schedules

    
    def format(self, schedules: List[Schedule]) -> str:
        """
        Format the schedule data as a text string.
        """
        formatted_text = ""
        for schedule in schedules:
            formatted_text += f"Schedule ID: {schedule.id}\n"
            formatted_text += f"Date: {schedule.date}\n"
            formatted_text += f"Time: {schedule.time}\n"
            formatted_text += f"Location: {schedule.location}\n"
            formatted_text += "-" * 20 + "\n"
        return formatted_text.strip()

