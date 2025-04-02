from typing import List
from .formatter_interface import IFormatter
from ..models.schedule import Schedule
import os

class TextFormatter(IFormatter):
    
    def __init__(self, schedules: List[Schedule]):
        """
        Initialize the TextFormatter.
        :param schedules: A list of Schedule objects.
        """
        self.schedules = schedules
        
        
    def __repr__(self):
        return f"<TextFormatter with {len(self.schedules)} schedules>"
        
    def format(self, schedules: List[Schedule]):
        """
        Format the schedule data and export it to a text file.
        :param schedules: A list of Schedule objects.
        """
        schedules = schedules or self.schedules
        if not schedules:
            raise ValueError("No schedules available to format.")
        # TODO: Add error handling for file operations
        self.export(schedules, "schedules.txt")
        
    def scheduleToText(self, schedule: Schedule) -> str:
        formatted_text = ""
        for lecture_group in schedule.lecture_groups:
            formatted_text += f"Course Code: {lecture_group.course_code}\n"
            formatted_text += f"Course Name: {lecture_group.course_name}\n"
            
            # Properly format time slots by calling str() on each TimeSlot
            for time_slot in lecture_group.lecture:
                formatted_text += f"Lecture: {str(time_slot)}\n"
            
            if lecture_group.tirguls:
                formatted_text += f"Tirgul: {', '.join(str(t) for t in lecture_group.tirguls)}\n"
            if lecture_group.maabadas:
                formatted_text += f"Maabada: {', '.join(str(m) for m in lecture_group.maabadas)}\n"
        
        return formatted_text.strip()


    def formatText(self, schedules: List[Schedule]) -> str:
        """
        Format the schedule data as a text string.
        """
        formatted_text = ""
        count = 1
        # Iterate through each schedule and its lecture groups
        for schedule in schedules:
            formatted_text += "----------------------------------------\n"
            formatted_text += f"Schedule {count}:\n"
            formatted_text += self.scheduleToText(schedule) + "\n"
            count += 1
        # Remove the last separator line
        return formatted_text.strip()
    
    
    def export(self, schedules: List[Schedule], file_path: str) -> None:
        """
        Export the formatted schedules to a text file.
        :param schedules: A list of Schedule objects.
        :param file_path: The path to the output text file.
        """
        try:
            # Ensure the directory exists before writing the file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.formatText(schedules))
        except (IOError, OSError) as e:
            print(f"Error exporting schedules: {e}")
        


