import pytest
from unittest.mock import mock_open, patch
from src.services.text_parser import TextParser
from src.models.course import Course
from src.models.time_slot import TimeSlot

# Raw data simulating the text file content
RAW_DATA = """
$$$$
Calculus 1
00001
Prof. O. Some
L S,2,16:00,17:00,1100,22 S,3,17:00,18:00,1100,42
T S,2,18:00,19:00,1100,22
T S,3,19:00,20:00,1100,42
$$$$
Software Project
83533
Dr. Terry Bell
L S,5,10:00,16:00,605,061
T S,5,16:00,17:00,605,061
""".strip()

#TEXTPARSER_FUNC_PARSE_001
@patch("builtins.open", new_callable=mock_open, read_data=RAW_DATA)
def test_parse_returns_courses(mock_file):
    """
    TEXTPARSER_FUNC_PARSE_RETURNS_COURSES:
    Ensures that `parse()` returns a list of Course objects.
    """
    parser = TextParser("fake_path.txt")
    courses = parser.parse()

    assert isinstance(courses, list)
    assert len(courses) == 2
    assert all(isinstance(c, Course) for c in courses)

    assert courses[0].name == "Calculus 1"
    assert courses[0].course_code == "00001"
    assert courses[1].name == "Software Project"
    assert courses[1].instructor == "Dr. Terry Bell"

#TEXTPARSER_FUNC_PARSE_002
@patch("builtins.open", new_callable=mock_open, read_data=RAW_DATA)
def test_parse_creates_valid_timeslots(mock_file):
    """
    TEXTPARSER_FUNC_TIMESLOTS_VALIDITY:
    Ensures TimeSlots are correctly parsed and attached to courses.
    """
    parser = TextParser("fake_path.txt")
    courses = parser.parse()
    calc1 = courses[0]

    # Check lectures
    assert isinstance(calc1.lectures, list)
    assert len(calc1.lectures) == 1
    # The first element is a list of TimeSlot objects
    first_lecture_list = calc1.lectures[0]
    assert isinstance(first_lecture_list, list)
    assert len(first_lecture_list) == 2
    assert all(isinstance(slot, TimeSlot) for slot in first_lecture_list)
    
    # Check first lecture slot details
    first_slot = first_lecture_list[0]
    assert first_slot.day == "2"
    assert first_slot.start_time.strftime("%H:%M") == "16:00"
    assert first_slot.end_time.strftime("%H:%M") == "17:00"
    assert first_slot.room == "1100"
    assert first_slot.building == "22"

    # Check tirguls
    assert len(calc1.tirguls) == 2
    assert calc1.tirguls[0][0].day == "2"
    assert calc1.tirguls[1][0].day == "3"

#TEXTPARSER_FILE_IO_001
@patch("builtins.open", new_callable=mock_open, read_data=RAW_DATA)
def test_read_file_reads_text_from_file(mock_file):
    """
    TEXTPARSER_FILE_IO_READS_FILE:
    Ensures read_file() correctly reads the file content.
    """
    parser = TextParser("dummy.txt")
    content = parser.read_file()
    assert RAW_DATA.startswith(content[:20])
    mock_file.assert_called_once_with("dummy.txt", 'r', encoding='utf-8')
