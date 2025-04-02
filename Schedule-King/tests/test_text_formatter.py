import pytest
from src.data.models.schedule import Schedule
from src.data.formatters.formatter_interface import IFormatter
from src.data.formatters.text_formatter import TextFormatter
from src.data.models.lecture_group import LectureGroup
from src.data.models.time_slot import TimeSlot
from datetime import datetime, timedelta

@pytest.fixture
def time_slots():
    return [
        TimeSlot("2", "16:00", "17:00", "1100", "22"),
        TimeSlot("5", "10:00", "16:00", "605", "061"),
        TimeSlot("1", "14:00", "16:00", "1401", "4"),
    ]
@pytest.fixture
def lecture_groups(time_slots):
    calculus_1 = LectureGroup(
        course_name="Calculus 1",
        course_code="00001",
        instructor="Prof. O. Some",
        lecture=time_slots[0],
        tirguls=[],
        maabadas=[]
    )

    software_project = LectureGroup(
        course_name="Software Project",
        course_code="83533",
        instructor="Dr. Terry Bell",
        lecture=[],
        tirguls=time_slots[1],
        maabadas=[]
    )

    calculus_1_eng = LectureGroup(
        course_name="Calculus 1 (eng)",
        course_code="83112",
        instructor="Dr. Erez Scheiner",
        lecture=[2],
        tirguls=[],
        maabadas=[]
    )
    return [calculus_1, software_project, calculus_1_eng]

@pytest.fixture
def sample_schedule(lecture_groups):
    return Schedule(lecture_groups=lecture_groups)

@pytest.fixture
def text_formatter(sample_schedule):
    return TextFormatter([sample_schedule])


# TEXTFORMATTER_INIT_001
def test_text_formatter_init(text_formatter, sample_schedule):
    assert isinstance(text_formatter, IFormatter)
    assert text_formatter.schedules == [sample_schedule]
    


