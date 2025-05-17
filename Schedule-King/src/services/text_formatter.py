from typing import List
from src.interfaces.formatter_interface import IFormatter
from src.models.schedule import Schedule, DAY_NAMES
import os

class TextFormatter(IFormatter):
    """
    A class to format and export schedule data to a text file.
    """

    def __init__(self, path: str):
        """
        Initialize the TextFormatter.
        :param path: A path to the output text file.
        """
        self.path = path

    def __repr__(self):
        """
        Return a string representation of the TextFormatter object.
        Includes the count of schedules if available.
        """
        schedules = getattr(self, "schedules", None)
        count = len(schedules) if schedules else 0
        return f"<TextFormatter with {count} schedules>"

    def format(self, schedules: List[Schedule]):
        """
        Format the schedule data and export it to a text file.
        :param schedules: A list of Schedule objects.
        :raises ValueError: If no schedules are provided.
        """
        if not schedules:
            raise ValueError("No schedules available to format.")
        self.export(schedules, file_path=self.path)

    def scheduleToText(self, schedule: Schedule) -> str:
        """
        Convert a single schedule object into a formatted text string.
        :param schedule: A Schedule object.
        :return: A formatted string representation of the schedule.
        """
        day_map = schedule.extract_by_day()
        output = ""

        # Iterate through each day in the schedule
        for day_num in sorted(DAY_NAMES.keys(), key=int):
            if day_num not in day_map:
                continue

            output += f"{DAY_NAMES[day_num]}:\n"
            # Sort slots by start_time
            slots = sorted(day_map[day_num], key=lambda x: x[3].start_time)

            # Format each slot's details
            for type_name, course_name, course_code, slot in slots:
                time_str = f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"
                output += (
                    f"  [{type_name}] {course_name} ({course_code})\n"
                    f"    {time_str} |  Room {slot.room}, Building {slot.building}\n"
                )
            output += "\n"

        return output.strip()

    def formatText(self, schedules: List[Schedule]) -> str:
        """
        Format the schedule data as a single text string.
        :param schedules: A list of Schedule objects.
        :return: A formatted string representation of all schedules.
        """
        formatted_text = ""
        count = 1

        # Iterate through each schedule and format it
        for schedule in schedules:
            formatted_text += "------------------------------------------------------\n"
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
        :raises IOError, OSError: If there is an error writing to the file.
        """
        try:
            # Ensure the directory exists before writing the file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.formatText(schedules))
        except (IOError, OSError) as e:
            print(f"Error exporting schedules: {e}")
