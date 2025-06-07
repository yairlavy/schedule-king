from typing import List
from src.interfaces.parser_interface import IParser
from src.models.course import Course
from src.models.time_slot import TimeSlot

import os
import pandas as pd
import re

# Mapping for Hebrew day names to day numbers used in TimeSlot
day_mapping = {
    'א': '1',  # Sunday
    'ב': '2',  # Monday
    'ג': '3',  # Tuesday
    'ד': '4',  # Wednesday
    'ה': '5',  # Thursday
    'ו': '6',  # Friday
    'ש': '7'   # Saturday
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
        df = pd.read_excel(self.path, sheet_name=None)  # Load all sheets from the Excel file
        courses_dict = {}  # Dictionary to store courses indexed by course code

        # Iterate over each sheet in the Excel file
        for sheet_name, sheet_data in df.items():
            # Skip sheets without the required 'מועד' (time) column
            if 'מועד' not in sheet_data.columns:
                continue

            # Iterate over each row in the sheet
            for index, row in sheet_data.iterrows():
                parsed_list = self._parse_row(index, row)  # Parse each row into list of course and time data
                if not parsed_list:
                    continue  # Skip if row could not be parsed

                # Process each parsed time slot from the row
                for parsed in parsed_list:
                    course_code, course_name, instructor, meeting_type, time_slot = parsed

                    # If course not already in dictionary, create a new Course object
                    if course_code not in courses_dict:
                        courses_dict[course_code] = Course(
                            course_name=course_name,
                            course_code=course_code,
                            instructor=instructor
                        )

                    course = courses_dict[course_code]
                    # Add the parsed time slot to the course
                    self._add_time_slot_to_course(course, meeting_type, time_slot, row.get('קוד מלא', ''))

        # Return all parsed courses as a list
        return list(courses_dict.values())

    def _parse_row(self, index, row):
        """
        Parses a single row and returns a list of tuples, each containing:
        course_code, course_name, instructor, meeting_type, and TimeSlot.
        Returns empty list if the row is invalid.
        """
        # Extract the full course code, or empty string if missing
        full_code = str(row['קוד מלא']) if pd.notna(row['קוד מלא']) else ''
        if '-' not in full_code:
            return []  # Skip if course code format is invalid

        course_code = full_code.split('-')[0]  # Extract base course code
        course_semester = row.get('תקופה','') # Extract semester part
        course_name = str(row.get('שם', ''))  # Course name
        meeting_type = str(row.get('סוג מפגש', '')).strip()  # Meeting type ('הרצאה', 'תרגול', 'מעבדה')
        time_str = str(row.get('מועד', ''))  # Time string (e.g., ג'10:00-12:00)
        instructor = str(row.get('מרצים', ''))  # Instructor(s)
        room_building_str = str(row.get('חדר', '')).strip()  # Room and building information

        # Only process courses in the first semester
        # If the course semester is not 'סמסטר א', skip this course
        if  'א' not in str(course_semester):
            return []

        # Split time string by newlines to handle multiple separate meetings
        time_lines = [line.strip() for line in time_str.split('\n') if line.strip()]
        room_lines = [line.strip() for line in room_building_str.split('\n') if line.strip()]
        
        # If no time slots found, return empty list
        if not time_lines:
            return []

        parsed_results = []
        
        # Process each time line (each line represents one meeting that might have multiple time slots)
        for line_idx, time_line in enumerate(time_lines):
            # Look for multiple day-time patterns in the same line
            time_patterns = re.findall(r"([א-ת])'?(\d{1,2}:\d{2})-(\d{1,2}:\d{2})", time_line)
            
            if not time_patterns:
                continue  # Skip if no patterns found
            
            # Get corresponding room info for this line
            current_room_str = room_lines[line_idx] if line_idx < len(room_lines) else (room_lines[0] if room_lines else '')
            
            # Parse building and room information
            building, room = self._parse_room_building(index, current_room_str)
            if building is None and room is None:
                continue  # Skip if room/building info is invalid
            
            # Create TimeSlots for all patterns in this line
            time_slots_for_this_line = []
            for day_hebrew, start_time_str, end_time_str in time_patterns:
                # Convert Hebrew day to number
                if day_hebrew not in day_mapping:
                    continue
                
                day_num = day_mapping[day_hebrew]
                
                try:
                    time_slot = TimeSlot(
                        day=day_num,
                        start_time=start_time_str,
                        end_time=end_time_str,
                        room=room,
                        building=building
                    )
                    time_slots_for_this_line.append(time_slot)
                except ValueError:
                    continue
            
            # Add all time slots from this line as one entry
            if time_slots_for_this_line:
                parsed_results.append((course_code, course_name, instructor, meeting_type, time_slots_for_this_line))

        return parsed_results

    def _parse_room_building(self, index, room_building_str):
        """
        Parses the room and building information from a string.
        Returns a tuple (building, room), or (None, None) if parsing fails.
        """
        if not room_building_str:
            return None, None
        
        # Expect format like 'הנדסה-1104'
        parts = room_building_str.split('-')

        if len(parts) < 2:
            # If only room is present, return empty building and the room
            return "", room_building_str.strip()
        
        building= '-'.join(parts[:-1]).strip()
        room = parts[-1].strip().split()[0]  # Take the first part in case of multiple hyphens  

        return building, room

    def _add_time_slot_to_course(self, course, meeting_type, time_slot_or_list, full_code):
        """
        Adds a TimeSlot or list of TimeSlots to the appropriate list in the Course object based on meeting type.
        """
        # Add time slot to the correct type (lecture, tirgul, or lab)
        if meeting_type == 'הרצאה':
            course.add_lecture(time_slot_or_list)
        elif meeting_type == 'תרגיל' or meeting_type == 'תרגול':
            course.add_tirgul(time_slot_or_list)
        elif meeting_type == 'מעבדה':
            course.add_maabada(time_slot_or_list)
        else:
            # Unknown meeting type like 'הדרכה'; do not add the time slot
            pass