import pytest
from unittest.mock import Mock
from src.services.all_strategy import AllStrategy
from src.models.course import Course
from src.models.lecture_group import LectureGroup
from src.models.schedule import Schedule
from src.models.time_slot import TimeSlot
from src.services.MatrixConflicChecker import MatrixConflictChecker

# ---------- Helpers ----------

def make_timeslot(label: str, day="1", start="12:00", end="13:00") -> TimeSlot:
    return TimeSlot(day=day, start_time=start, end_time=end, room="101", building="A")

def make_course(code, lecture_time, tirgul_time=None, maabada_time=None) -> Course:
    return Course(
        course_name=f"Course{code}",
        course_code=f"C{code}",
        instructor=f"Instructor{code}",
        lectures=[[lecture_time]],
        tirguls=[[tirgul_time]] if tirgul_time else [],
        maabadas=[[maabada_time]] if maabada_time else []
    )

# ---------- Fixtures ----------

@pytest.fixture
def non_conflicting_courses():
    t1 = make_timeslot("L1", start="08:00", end="09:00")
    t2  = make_timeslot("T1", start="09:00", end="10:00")
    t3 = make_timeslot("M1", start="10:00", end="11:00")
    
    t4 = make_timeslot("L2", start="12:00", end="13:00")
    t5  = make_timeslot("T2", start="13:00", end="14:00")
    t6 = make_timeslot("M2", start="14:00", end="15:00")
    
    return [
        make_course("1", t1, t2, t3),
        make_course("2", t4, t5, t6)
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
#STRATEGYALL_INIT_001
def test_init_valid():
    strategy = AllStrategy([Mock()])
    assert isinstance(strategy._selected, list)

#STRATEGYALL_VALID_001
def test_init_too_many_courses_raises():
    with pytest.raises(ValueError):
        AllStrategy([Mock()] * 8)

#STRATEGYALL_VALID_002
def test_generate_no_courses():
    strategy = AllStrategy([])
    result = list(strategy.generate())
    assert result == []

#STRATEGYALL_VALID_003
def test_generate_no_conflict(non_conflicting_courses):
    strategy = AllStrategy(non_conflicting_courses)
    schedules = list(strategy.generate())
    assert len(schedules) >= 1
    assert all(isinstance(schedule, Schedule) for schedule in schedules)

#STRATEGYALL_VALID_004
def test_generate_conflict_detected(conflicting_courses):
    strategy = AllStrategy(conflicting_courses)
    schedules = list(strategy.generate())
    assert schedules == []  # All combinations should conflict

# STRATEGYALL_VALID_005
def test_generate_with_forbidden_timeslot_excludes_schedules():
    # Create a time slot that will be forbidden
    forbidden_slot = make_timeslot("Forbidden", day="1", start="08:00", end="09:00")

    # Create a course that includes this forbidden time
    course_with_forbidden = make_course("1", forbidden_slot)

    # Initialize strategy with one course and one forbidden time
    strategy = AllStrategy([course_with_forbidden], forbidden=[forbidden_slot])

    # The generator should yield no schedules since the only available one is forbidden
    schedules = list(strategy.generate())
    assert schedules == []

#STRATEGYALL_FUNC_001
def test_generate_all_combinations(non_conflicting_courses):
    strategy = AllStrategy(non_conflicting_courses)
    schedules = list(strategy.generate())
    assert schedules  # not empty
    assert all(isinstance(schedule, Schedule) for schedule in schedules)
    assert all(isinstance(g, LectureGroup) for s in schedules for g in s.lecture_groups)

#STRATEGYALL_FUNC_002
def test_matrix_checker_conflict():
    checker = MatrixConflictChecker()
    # Overlapping time slots
    slot1 = make_timeslot("A", start="12:00", end="14:00")
    slot2 = make_timeslot("B", start="13:00", end="15:00")

    assert checker.can_place(slot1)  # slot1 should fit
    checker.place(slot1)
    assert not checker.can_place(slot2)  # slot2 overlaps with slot1

#STRATEGYALL_FUNC_003
def test_matrix_checker_no_conflict():
    checker = MatrixConflictChecker()
    slot1 = make_timeslot("A", start="08:00", end="09:00")
    slot2 = make_timeslot("B", start="10:00", end="11:00")

    assert checker.can_place(slot1)
    checker.place(slot1)
    assert checker.can_place(slot2)