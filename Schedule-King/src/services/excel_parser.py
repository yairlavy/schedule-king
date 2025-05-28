from typing import List
from src.interfaces.parser_interface import IParser
from src.models.course import Course
from src.models.time_slot import TimeSlot

import os
import pandas as pd
from datetime import datetime, timedelta

# Mapping for Hebrew day names to day numbers used in TimeSlot
day_mapping = {
    'א': '1', # Sunday
    'ב': '2', # Monday
    'ג': '3', # Tuesday
    'ד': '4', # Wednesday
    'ה': '5', # Thursday
    'ו': '6', # Friday
    'ש': '7'  # Saturday, although unlikely in a schedule, include for completeness
}

class ExcelParser(IParser):
    """
    ExcelParser implements the IParser interface to parse course schedules from an Excel file.
    """

    def __init__(self, path: str):
        """
        Initializes the ExcelParser with the path to the Excel file.
        Raises FileNotFoundError if the file does not exist.
        """
        self.path = path
        if not os.path.exists(path):
            raise FileNotFoundError(f"Excel file '{path}' does not exist.")
        
    def parse(self) -> List[Course]:
        """
        Parses the Excel file and returns a list of Course objects.
        Reads all sheets in the Excel file and processes each one.
        Only sheets containing a 'מועד' column are considered.
        """
        df = pd.read_excel(self.path, sheet_name=None)  # Read all sheets into a dict of DataFrames
        courses_dict = {}  # Dictionary to store courses by course code

        for sheet_name,sheet_data in df.items():
            if 'מועד' not in sheet_data.columns:
                continue  # Skip sheets without the required column
            for index, row in sheet_data.iterrows():
                parsed = self._parse_row(index, row)  # Parse each row
                if not parsed:
                    continue  # Skip rows that couldn't be parsed
                course_code, course_name, instructor, meeting_type, time_slot = parsed
                if course_code not in courses_dict:
                    # Create a new Course object if not already present
                    courses_dict[course_code] = Course(course_name=course_name, course_code=course_code, instructor=instructor)
                course = courses_dict[course_code]
                # Add the parsed time slot to the course
                self._add_time_slot_to_course(course, meeting_type, time_slot, row.get('קוד מלא', ''))
        return list(courses_dict.values())  # Return all parsed courses

    def _parse_row(self, index, row):
        """
        Parses a single row from the Excel sheet and extracts course and time slot information.
        Returns a tuple with course details and a TimeSlot object, or None if parsing fails.
        """
        full_code = str(row['קוד מלא'])  # Full course code (may include section)
        course_code = full_code.split('-')[0]  # Extract base course code
        course_name = row['שם']  # Course name
        meeting_type = row['סוג מפגש']  # Type of meeting (lecture, lab, etc.)
        time_str = row['מועד']  # Time string (e.g., ג' 10:00-12:00)
        instructor = row['מרצים']  # Instructor name(s)
        room_building_str = str(row['חדר'])  # Room and building string

        # Parse time string (e.g., ג' 10:00-12:00)
        parts = time_str.split(' ')
        if len(parts) != 2:
            print(f"Skipping row {index} due to unexpected time format: {time_str}")
            return None

        day_hebrew = parts[0].replace("'", "")  # Remove apostrophe from day
        time_range = parts[1]

        if day_hebrew not in day_mapping:
            print(f"Skipping row {index} due to unhandled Hebrew day: {day_hebrew}")
            return None

        day_num = day_mapping[day_hebrew]  # Convert Hebrew day to number

        time_parts = time_range.split('-')
        if len(time_parts) != 2:
            print(f"Skipping row {index} due to unexpected time range format: {time_range}")
            return None
        start_time_str = time_parts[0]  # Start time 
        end_time_str = time_parts[1]    # End time

        building, room = self._parse_room_building(index, room_building_str)
        if building is None and room is None:
            return None

        try:
            # Create a TimeSlot object with the parsed data
            time_slot = TimeSlot(day=day_num, start_time=start_time_str, end_time=end_time_str, room=room, building=building)
        except ValueError as e:
            print(f"Skipping row {index} due to invalid TimeSlot data: {e}")
            return None

        return course_code, course_name, instructor, meeting_type, time_slot

    def _parse_room_building(self, index, room_building_str):
        """
        Parses the room and building information from a string.
        Returns a tuple (building, room), or (None, None) if parsing fails.
        """
        room_building_parts = room_building_str.split('-')
        if len(room_building_parts) != 2:
            # If format is unexpected, treat the whole string as room
            print(f"Skipping row {index} due to unexpected room/building format: {room_building_str}")
            building = ""
            room = room_building_str.strip()
            if not room or not room.replace('-', '').isalnum():
                print(f"Skipping row {index} as room is invalid: {room}")
                return None, None
        else:
            building = room_building_parts[0].strip()
            room = room_building_parts[1].strip()
            if not building.isalnum() or not room.isalnum():
                print(f"Skipping row {index} as building or room is not alphanumeric: Building='{building}', Room='{room}'")
                return None, None
        return building, room

    def _add_time_slot_to_course(self, course, meeting_type, time_slot, full_code):
        """
        Adds a TimeSlot to the appropriate list in the Course object based on meeting type.
        """
        if meeting_type == 'הרצאה':
            course.add_lecture(time_slot)
        elif meeting_type == 'תרגול':
            course.add_tirgul(time_slot)
        elif meeting_type == 'מעבדה':
            course.add_maabada(time_slot)
        else:
            print(f"Unknown meeting type '{meeting_type}' for course {full_code}. Skipping time slot.")
