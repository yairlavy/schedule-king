from .parser_interface import IParser
from typing import List
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup 
from src.data.models.time_slot import TimeSlot

class TextParser(IParser):
    def __init__(self, file_path: str):
        """Initializes the TextParser with the given file path."""
        self.file_path = file_path

    def parse(self) -> List[Course]:
        """
        Parses the given raw text data and returns a list of Course objects.
        """
        raw_data = self.read_file()
        raw_courses = [block for block in raw_data.split("$$$$\n") if block.strip()]
        return [self._parse_raw_course(course_text) for course_text in raw_courses]

    def _parse_raw_course(self, raw_course: str) -> Course:
        """
        Parses a raw course string and returns a Course object.
        """
        lines = [line.strip() for line in raw_course.split("\n") if line.strip()]
        if len(lines) < 3:
            raise ValueError("Invalid course block: missing name/code/instructor")

        course = Course(lines[0], lines[1], lines[2])
        for line in lines[3:]:
            prefix = line[0]
            time_slots = self._parse_slots(line)
            if prefix == "L":
                for slot in time_slots:
                    course.add_lecture(slot)
            elif prefix == "T":
                for slot in time_slots:
                    course.add_tirgul(slot)
            elif prefix == "M":
                for slot in time_slots:
                    course.add_maabada(slot)
        # random maabada 
        return course

    def _parse_slots(self, line: str) -> List[TimeSlot]:
        """
        Parses a line starting with L/T/M and returns TimeSlot objects.
        """
        slot_data = line[2:].strip().split()
        return [self._parse_time_slot(slot) for slot in slot_data]

    def _parse_time_slot(self, slot: str) -> TimeSlot:
        """
        Parses a time slot string and returns a TimeSlot object.
        Format: S,5,14:00,16:00,1300,1
        """
        parts = slot.split(",")
        if len(parts) != 6:
            raise ValueError(f"Invalid time slot format: {slot}")
        return TimeSlot(parts[1], parts[2], parts[3], parts[4], parts[5])

    def read_file(self, file_path: str = None) -> str:
        """
        Reads the content of a text file and returns it as a string.
        """
        path = file_path or self.file_path
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
