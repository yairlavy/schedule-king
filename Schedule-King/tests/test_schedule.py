import pytest
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
        lecture=[],
        tirguls=[],
        maabadas=time_slots[2]
    )

    return [calculus_1, software_project, calculus_1_eng]

@pytest.fixture
def sample_schedule(lecture_groups):
    return Schedule(lecture_groups=lecture_groups)

#SCHEDULE_INIT_001
def test_schedule_init(sample_schedule, lecture_groups):
    assert sample_schedule.lecture_groups == lecture_groups
    print("")
    for lg in sample_schedule.lecture_groups:
        print(f"LectureGroup: {lg.course_name} ({lg.course_code}) - Instructor: {lg.instructor} "
            f"- Time Slot: {lg.lecture} - Tirguls: {lg.tirguls} - Maabadas: {lg.maabadas}")
    
    #SCHEDULE_FUNC_LEN_001
    assert len(sample_schedule.lecture_groups) == 3

#SCHEDULE_REPR_001
def test_schedule_str_representation(sample_schedule, lecture_groups):
    expected_str = f"Schedule({lecture_groups[0].course_code}, {lecture_groups[1].course_code}, {lecture_groups[2].course_code})"
    assert str(sample_schedule) == expected_str
    print("\nsample_schedule:", sample_schedule)