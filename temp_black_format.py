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
        
    def scheduleToText(self , schedules : Schedule) -> str:
        formatted_text = ""
        # Iterate through each lecture group in the schedule and format the details
        for lecture_group in schedule.lecture_groups:
            formatted_text += f"Course Code: {lecture_group.course_code}\n"
            formatted_text += f"Course Name: {lecture_group.course_name}\n"
            formatted_text += f"Time: {lecture_group.lecture}\n"
            if lecture_group.tirguls:
                formatted_text += f"Tirgul: {lecture_group.tirguls}\n"
            if lecture_group.maabadas:
                formatted_text += f"Maabada: {lecture_group.maabadas}\n"
        return formatted_text.strip()

    
    def format(self, schedules: List[Schedule]) -> str:
        """
        Format the schedule data as a text string.
        """
        formatted_text = ""
        count = 1
        # Iterate through each schedule and its lecture groups
        for schedule in schedules:
            formatted_text += "----------------------------------------\n"
            formatted_text += f"Schedule {count}:\n"
            formatted_text += self.schedulesToText(schedule) + "\n"
            formatted_text += "----------------------------------------\n"
            count += 1
        # Remove the last separator line
        return formatted_text.strip()
    
    
    def export(self, schedules: List[Schedule], file_path: str) -> None:
        """
        Export the formatted schedule to a text file.
        :param schedules: A list of Schedule objects.
        :param file_path: The path to the output text file.
        """
        with open(file_path, 'w') as file: # TODO: Add error handling for file operations
            # Write the formatted text to the file
            file.write(self.format(schedules))
        print(f"Schedules exported to {file_path} successfully.")   
        

