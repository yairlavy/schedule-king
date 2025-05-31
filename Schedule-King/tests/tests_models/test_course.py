import pytest
from src.models.course import Course
from src.models.time_slot import TimeSlot

@pytest.fixture
def time_slots():
    return [
        TimeSlot("5", "10:00", "16:00", "605", "061"),
        TimeSlot("5", "16:00", "17:00", "605", "061"),
        TimeSlot("1", "09:00", "10:00", "101", "22")
    ]

@pytest.fixture
def sample_course(time_slots):
    lectures = time_slots
    tirguls = [time_slots[1]]
    maabadas = []  # Empty labs
    return Course(
        course_name="Software Project",
        course_code="83533",
        instructor="Dr. Terry Bell",
        lectures=lectures,
        tirguls=tirguls,
        maabadas=maabadas
    )

def test_course_init(sample_course, time_slots):
    #COURSE_INIT_001
    assert sample_course.name == "Software Project"
    assert sample_course.course_code == "83533"
    assert sample_course.instructor == "Dr. Terry Bell"
    assert sample_course.lectures == time_slots
    print("\nsample_course.lectures:", [str(slot) for slot in sample_course.lectures])
    assert sample_course.tirguls == [time_slots[1]]
    assert not sample_course.tirguls == [time_slots[2]]
    print("sample_course.tirguls:", [str(slot) for slot in sample_course.tirguls])
    assert sample_course.maabadas == [] 
    print("sample_course.maabadas:", [str(slot) for slot in sample_course.maabadas])
    
    #COURSE_FUNC_001
    assert len(sample_course.lectures) == 3
    assert len(sample_course.tirguls) == 1
    assert len(sample_course.maabadas) == 0

def test_course_str_representation(sample_course):
    #COURSE_REPR_001
    expected = "Course(83533, Software Project, Dr. Terry Bell)"
    assert str(sample_course) == expected

def test_course_change_info(sample_course, time_slots):
    #COURSE_NEG_ATTR_001
    with pytest.raises(AttributeError):
        sample_course.name = "Calculus 1"
    with pytest.raises(AttributeError):
        sample_course.course_code = "83112"
    with pytest.raises(AttributeError):
        sample_course.instructor = "Dr. Erez Scheiner"
    with pytest.raises(AttributeError):
        sample_course.lectures = [time_slots[0]]
    with pytest.raises(AttributeError):
        sample_course.tirguls = []

    # COURSE_FUNC_LIST_001
    #Add time slots cannot change them (currectly i can add the same time slot i already have)
    sample_course.lectures.append(time_slots[0])
    sample_course.tirguls.append(time_slots[0]) 
    sample_course.maabadas.append(time_slots[2])

    assert len(sample_course.lectures) == 4
    assert len(sample_course.tirguls) == 2
    assert len(sample_course.maabadas) == 1

    sample_course.lectures.append(time_slots[0])
    assert len(sample_course.lectures) == 5

    print("\nsample_course.lectures:", [str(slot) for slot in sample_course.lectures])
    print("sample_course.tirguls:", [str(slot) for slot in sample_course.tirguls])
    print("sample_course.maabadas:", [str(slot) for slot in sample_course.maabadas])


