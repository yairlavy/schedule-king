import pytest
from src.models.lecture_group import LectureGroup
from src.models.time_slot import TimeSlot

@pytest.fixture
def time_slots():
    return [
        TimeSlot("5", "10:00", "16:00", "605", "061"),
        TimeSlot("5", "16:00", "17:00", "605", "061"),
        TimeSlot("1", "09:00", "10:00", "101", "22")
    ]

@pytest.fixture
def group(time_slots):
    return LectureGroup(
        course_name="Software Project",
        course_code="83533",
        instructor="Dr. Terry Bell",
        lecture = time_slots,
        tirguls = time_slots[1],
        maabadas = time_slots[2]
    )

#LECTUREGROUP_INIT_001
def test_lecture_group(group, time_slots):
    assert group.course_name == "Software Project"
    assert group.course_code == "83533"
    assert group.instructor == "Dr. Terry Bell"
    assert group.lecture == time_slots
    assert group.tirguls == time_slots[1]
    assert group.maabadas == time_slots[2]

#LECTUREGROUP_REPR_001
def test_course_str_representation(group):
    expected_str = f"LectureGroup({group.course_code}, {group.course_name}, {group.instructor}, {group.lecture}, {group.tirguls}, {group.maabadas})"
    assert str(group) == expected_str