import pytest
from itertools import product
from unittest.mock import Mock
from src.core.all_strategy import AllStrategy
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup
from src.data.models.schedule import Schedule
from src.data.models.time_slot import TimeSlot


# ---------- Helpers ----------

def make_timeslot(label: str, day="1", start="12:00", end="13:00") -> TimeSlot:
    return TimeSlot(day=day, start_time=start, end_time=end, room="101", building="A")

def make_course(code, lecture_time, tirgul_time, maabada_time) -> Course:
    return Course(
        name=f"Course{code}",
        course_code=f"C{code}",
        instructor=f"Instructor{code}",
        lectures=[lecture_time],
        tirguls=[tirgul_time],
        maabadas=[maabada_time]
    )

# ---------- Fixtures ----------

@pytest.fixture
def non_conflicting_courses():
    t1 = make_timeslot("L1", start="08:00", end="09:00")
    t2 = make_timeslot("L2", start="10:00", end="11:00")
    return [
        make_course("1", t1, t1, t1),
        make_course("2", t2, t2, t2)
    ]

@pytest.fixture
def conflicting_courses():
    t1 = make_timeslot("L1", start="10:00", end="12:00")
    t2 = make_timeslot("L2", start="11:00", end="13:00")  # Overlaps with t1
    return [
        make_course("1", t1, t1, t1),
        make_course("2", t2, t2, t2)
    ]


# ---------- Tests ----------

def test_init_valid():
    strategy = AllStrategy([Mock()])
    assert isinstance(strategy._selected, list)

def test_init_too_many_courses_raises():
    with pytest.raises(ValueError):
        AllStrategy([Mock()] * 8)

def test_generate_all_combinations(non_conflicting_courses):
    strategy = AllStrategy(non_conflicting_courses)
    combos = strategy._generate_all_lecture_group_combinations(non_conflicting_courses)
    assert len(combos) == 1
    assert isinstance(combos[0][0], LectureGroup)

def test_generate_no_courses():
    strategy = AllStrategy([])
    result = strategy.generate()
    assert len(result) == 1
    assert isinstance(result[0], Schedule)
    assert result[0].lecture_groups == []

def test_generate_no_conflict(non_conflicting_courses):
    strategy = AllStrategy(non_conflicting_courses)
    schedules = strategy.generate()
    assert len(schedules) >= 1
    assert all(isinstance(schedule, Schedule) for schedule in schedules)

def test_generate_conflict_detected(conflicting_courses):
    strategy = AllStrategy(conflicting_courses)
    schedules = strategy.generate()
    assert schedules == []  # All combinations conflict

def test__has_conflict_with_real_checker_conflict():
    # Overlapping time slots
    slot1 = make_timeslot("A", start="12:00", end="14:00")
    slot2 = make_timeslot("B", start="13:00", end="15:00")
    group1 = LectureGroup("C1", "001", "Prof A", lecture=slot1, tirguls=None, maabadas=None)
    group2 = LectureGroup("C2", "002", "Prof B", lecture=slot2, tirguls=None, maabadas=None)

    strategy = AllStrategy([])
    assert strategy._has_conflict([group1, group2])

def test__has_conflict_with_real_checker_no_conflict():
    slot1 = make_timeslot("A", start="08:00", end="09:00")
    slot2 = make_timeslot("B", start="10:00", end="11:00")
    group1 = LectureGroup("C1", "001", "Prof A", lecture=slot1, tirguls=None, maabadas=None)
    group2 = LectureGroup("C2", "002", "Prof B", lecture=slot2, tirguls=None, maabadas=None)

    strategy = AllStrategy([])
    assert not strategy._has_conflict([group1, group2])
