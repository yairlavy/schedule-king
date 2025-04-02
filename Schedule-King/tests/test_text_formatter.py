import pytest
import os
from src.data.formatters.text_formatter import TextFormatter
from src.data.models.schedule import Schedule
from src.data.models.lecture_group import LectureGroup
from src.data.models.time_slot import TimeSlot

@pytest.fixture
def time_slots():
    return [
        TimeSlot("2", "16:00", "17:00", "1100", "22"),
        TimeSlot("5", "10:00", "16:00", "605", "061"),
        TimeSlot("1", "14:00", "16:00", "1401", "4"),
    ]

@pytest.fixture
def lecture_groups(time_slots):
    return [
        LectureGroup("Calculus 1", "00001", "Prof. O. Some", time_slots[0], [], []),
        LectureGroup("Software Project", "83533", "Dr. Terry Bell", None, [time_slots[1]], []),
        LectureGroup("Calculus 1 (eng)", "83112", "Dr. Erez Scheiner", None, [], [time_slots[2]])
    ]

@pytest.fixture
def sample_schedule(lecture_groups):
    return Schedule(lecture_groups=lecture_groups)

@pytest.fixture
def formatter(sample_schedule):
    return TextFormatter([sample_schedule])

# TEXTFORMATTER_INIT_001 - Initialization
def test_textformatter_init(formatter):
    assert isinstance(formatter, TextFormatter)
    assert isinstance(formatter.schedules, list)
    assert len(formatter.schedules) > 0

# TEXTFORMATTER_FUNC_001 - Functional test for format()
def test_textformatter_format(formatter, sample_schedule):
    formatter.format([sample_schedule])
    assert os.path.exists("schedules.txt")
    with open("schedules.txt", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Schedule 1:" in content
    assert "Course Code: 00001" in content
    os.remove("schedules.txt")

# TEXTFORMATTER_FUNC_002 - Functional test for scheduleToText()
def test_textformatter_schedule_to_text(formatter, sample_schedule):
    formatted_text = formatter.scheduleToText(sample_schedule)
    assert isinstance(formatted_text, str)
    assert "Course Code: 00001" in formatted_text
    assert "Course Name: Calculus 1" in formatted_text

# TEXTFORMATTER_FILE_IO_001 - File IO test for export()
def test_textformatter_export(formatter, sample_schedule):
    file_path = "test_schedule_output.txt"
    formatter.export([sample_schedule], file_path)
    assert os.path.exists(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Schedule 1:" in content
    assert "Course Code: 00001" in content
    assert "Course Name: Calculus 1" in content
    assert "Instructor: Prof. O. Some" in content
    os.remove(file_path)  # Clean up after test

# TEXTFORMATTER_REPR_001 - Representation test
def test_textformatter_repr(formatter):
    expected_repr = f"<TextFormatter with {len(formatter.schedules)} schedules>"
    assert repr(formatter) == expected_repr