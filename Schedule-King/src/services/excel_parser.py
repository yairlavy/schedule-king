from typing import List
from src.interfaces.parser_interface import IParser
from src.models.course import Course
from src.models.time_slot import TimeSlot
from src.services.logger import Logger
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
        # Dictionary to store room information: (room, building) -> list of (TimeSlot, course_code)
        self.times_rooms: dict[tuple[str, str], list[tuple[TimeSlot, str]]] = {}
        if not os.path.exists(path):
            raise FileNotFoundError(f"Excel file '{path}' does not exist.")
        
    def parse(self) -> List[Course]:
        """
        Parses the Excel file and returns a list of Course objects.
        Reads all sheets in the Excel file and processes each one.
        Only sheets containing a 'מועד' column are considered.
        """

        # Load all sheets from the Excel file
        df = pd.read_excel(self.path, sheet_name=None)
        # Dictionary to store courses indexed by course code
        courses_dict = {}

        # Iterate over each sheet in the Excel file
        for sheet_name, sheet_data in df.items():
            # Skip sheets without the required 'מועד' (time) column
            if 'מועד' not in sheet_data.columns:
                continue

            # Iterate over each row in the sheet
            for index, row in sheet_data.iterrows():
                # Parse each row into list of course and time data
                parsed_list = self._parse_row(index, row)
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

        # Extract base course code
        course_code = full_code.split('-')[0]
        # Extract semester part
        course_semester = row.get('תקופה','')
        # Course name
        course_name = str(row.get('שם', ''))
        # Meeting type ('הרצאה', 'תרגול', 'מעבדה')
        meeting_type = str(row.get('סוג מפגש', '')).strip()
        # Time string (e.g., ג'10:00-12:00)
        time_str = str(row.get('מועד', ''))
        # Instructor(s)
        instructor = str(row.get('מרצים', ''))
        # Room and building information
        room_building_str = str(row.get('חדר', '')).strip()

        # Only process known meeting types
        if meeting_type not in ['הרצאה', 'תרגול', 'תרגיל', 'מעבדה']:
            return []
        
        # Only process courses in the first semester
        if 'א' not in str(course_semester):
            return []

        # Split time string by newlines to handle multiple separate meetings
        time_lines = [line.strip() for line in time_str.split('\n') if line.strip()]
        room_lines = [line.strip() for line in room_building_str.split('\n') if line.strip()]
        
        # If no time slots found, return empty list
        if not time_lines:
            return []

        parsed_results = []
        
        # Process each time line (each line represents a separate meeting/lecture)
        for line_idx, time_line in enumerate(time_lines):
            # Look for multiple day-time patterns in the same line
            time_patterns = re.findall(r"([א-ת])'?(\d{1,2}:\d{2})-(\d{1,2}:\d{2})", time_line)
            
            if not time_patterns:
                continue  # Skip if no patterns found
            
            # Get corresponding room info for this line
            # If there are fewer room lines than time lines, use the last available room
            if line_idx < len(room_lines):
                current_room_str = room_lines[line_idx]
            elif room_lines:
                current_room_str = room_lines[-1]  # Use last room if not enough room lines
            else:
                current_room_str = ''
            
            # Parse building and room information
            building, room = self._parse_room_building(index, current_room_str)
            # Skip only if both building and room are None (completely invalid)
            if building is None and room is None:
                continue  # Skip if room/building info is completely invalid
            
            # Create TimeSlots for all patterns in this line
            time_slots_for_this_line = []
            for day_hebrew, start_time_str, end_time_str in time_patterns:
                # Convert Hebrew day to number
                if day_hebrew not in day_mapping:
                    continue
                
                day_num = day_mapping[day_hebrew]
                
                try:
                    # Create TimeSlot object
                    time_slot = TimeSlot(
                        day=day_num,
                        start_time=start_time_str,
                        end_time=end_time_str,
                        room=room if room else "Unknown",  # Provide default if room is None
                        building=building if building else "Unknown"  # Provide default if building is None
                    )
                    time_slots_for_this_line.append(time_slot)
                except ValueError:
                    continue
               
            # Check room validity for all time slots (only if both room and building exist)
            if room and building:
                for slot in time_slots_for_this_line:
                        self.check_room_validity(room, building, slot, course_code)

            # Each line creates a separate entry - this handles multiple lectures for the same course
            if time_slots_for_this_line:
                parsed_results.append((course_code, course_name, instructor, meeting_type, time_slots_for_this_line))

        return parsed_results

    def _parse_room_building(self, index, room_building_str):
        """
        Parses the room and building information from a string.
        Handles different formats:
        - "הנדסה-1104-4" -> building: "הנדסה-1104", room: "4"
        - "וואהל-11" -> building: "וואהל", room: "11"
        - "בניין - חדר" -> building: "בניין", room: "חדר"
        Returns a tuple (building, room), or (None, None) if parsing fails.
        """
        if not room_building_str:
            return None, None

        room_building_str = room_building_str.strip()
        try:
            # First try the format with spaces around dash: "בניין - חדר"
            if " - " in room_building_str:
                parts = room_building_str.split(" - ")
                if len(parts) == 2:
                    building = parts[0].strip()
                    room = parts[1].strip()
                    return building, room
                elif len(parts) > 2:
                    parts = [part.strip() for part in parts]
                    # Assume last part is room, everything before is building
                    room = parts[-1]
                    building = " - ".join(parts[:-1]).strip()
                    return building, room
                else:
                    return room_building_str, None  # Invalid format, return as is
            # If only one part is present, assume it's the room with unknown building
            if room_building_str:
                return None, room_building_str
                
        except Exception as e:
            print(f"Error parsing room/building at index {index}: {e}")
            return None, None
        return None, None
        
    def _add_time_slot_to_course(self, course, meeting_type, time_slot_or_list, full_code):
        """
        Adds a TimeSlot or list of TimeSlots to the appropriate list in the Course object based on meeting type.
        Checks for internal conflicts within the same course.
        """
        # Get the appropriate list based on meeting type
        if meeting_type == 'הרצאה':
            course.add_lecture(time_slot_or_list)
        elif meeting_type in ['תרגיל', 'תרגול']:
            course.add_tirgul(time_slot_or_list)
        elif meeting_type == 'מעבדה':
            course.add_maabada(time_slot_or_list)
        else:
            # Unknown meeting type; do not add the time slot
            pass

    def check_room_validity(self, room: str, building: str, time: TimeSlot, course_code: str = None) -> bool:
        """
        Checks if the given room and building are available for the specified time slot.
        Prevents scheduling conflicts for the same room and building.
        Returns True if the room is available, False if there is a conflict.
        """
        key = (room, building)
        # If this room-building combination has not been used, add it and return True
        if key not in self.times_rooms:
            self.times_rooms[key] = [(time, course_code)]
            return True

        # Check for conflicts with existing time slots for this room-building
        for existing_time, existing_code in self.times_rooms[key]:
            if existing_time.conflicts_with_room(time):
                    Logger.inner_conflict+=f"Conflict detected for room {room} in building {building} at {time}. Existing course: {existing_code}, New course: {course_code}"
                    return False

        # No conflicts found, add the new time slot and return True
        self.times_rooms[key].append((time, course_code))
        return True
    

        