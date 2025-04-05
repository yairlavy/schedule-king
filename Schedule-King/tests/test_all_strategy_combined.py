import pytest
from itertools import product
from unittest.mock import Mock, MagicMock
from src.core.all_strategy import AllStrategy
from src.data.models.course import Course
from src.data.models.lecture_group import LectureGroup
from src.data.models.schedule import Schedule
from src.data.models.time_slot import TimeSlot
from src.core.conflict_checker import ConflictChecker

# ---------- Fixtures ----------
@pytest.fixture
def sample_courses():
    return [
        Course("Course1", "C1", "Instructor1", [make_timeslot("L1")], [make_timeslot("T1")], [make_timeslot("M1")]),
        Course("Course2", "C2", "Instructor2", [make_timeslot("L2")], [make_timeslot("T2")], [make_timeslot("M2")])
    ]

def make_timeslot(label: str) -> TimeSlot:
    day = str((ord(label[0]) % 5) + 1)
    start_hour = (ord(label[1]) % 6) + 8
    end_hour = start_hour + 1
    return TimeSlot(day, f"{start_hour:02d}:00", f"{end_hour:02d}:00", room="101", building="A")

# ---------- __init__ Tests ----------

def test_init_valid():
    courses = [Mock(spec=Course) for _ in range(3)]
    checker = Mock()
    strategy = AllStrategy(courses, checker)
    assert strategy._selected == courses
    assert strategy._checker == checker

def test_init_max():
    courses = [Mock(spec=Course) for _ in range(7)]
    checker = Mock()
    strategy = AllStrategy(courses, checker)
    assert strategy._selected == courses


def test_init_too_many():
    courses = [Mock(spec=Course) for _ in range(8)]
    checker = Mock()
    with pytest.raises(ValueError):
        AllStrategy(courses, checker)

# ---------- _generate_all_lecture_group_combinations ----------

def test_generate_combinations(sample_courses):
    strategy = AllStrategy(sample_courses)
    combos = strategy._generate_all_lecture_group_combinations(sample_courses)
    assert len(combos) > 0
    assert all(isinstance(combo, list) for combo in combos)
    assert all(isinstance(group, LectureGroup) for combo in combos for group in combo)

def test_generate_combinations_empty():
    strategy = AllStrategy([], )
    combos = strategy._generate_all_lecture_group_combinations([])
    assert combos == [] or combos == [[]]

def test_generate_combinations_no_options():
    empty = Course("Empty", "C3", "None", [], [], [])
    strategy = AllStrategy([empty], )
    combos = strategy._generate_all_lecture_group_combinations([empty])
    assert combos == []

# ---------- _has_conflict ----------

def test_has_conflict_no_conflict():
    checker = Mock()
    checker.check_time_conflict.return_value = False
    checker.check_room_conflict.return_value = False
    groups = [Mock(spec=LectureGroup) for _ in range(3)]
    strategy = AllStrategy(groups, checker)
    assert not strategy._has_conflict(groups)

def test_has_conflict_time_conflict():
    checker = Mock()
    groups = [Mock(spec=LectureGroup) for _ in range(2)]
    checker.check_time_conflict.side_effect = lambda a, b: True
    checker.check_room_conflict.return_value = False
    strategy = AllStrategy(groups, checker)
    assert strategy._has_conflict(groups)

def test_has_conflict_room_conflict():
    checker = Mock()
    groups = [Mock(spec=LectureGroup) for _ in range(2)]
    checker.check_time_conflict.return_value = False
    checker.check_room_conflict.side_effect = lambda a, b: True
    strategy = AllStrategy(groups, checker)
    assert strategy._has_conflict(groups)

def test_has_conflict_empty():
    checker = Mock()
    strategy = AllStrategy([], checker)
    assert not strategy._has_conflict([])

def test_has_conflict_single():
    checker = Mock()
    groups = [Mock(spec=LectureGroup)]
    strategy = AllStrategy(groups, checker)
    assert not strategy._has_conflict(groups)

# ---------- generate ----------

def test_generate_valid_schedules(sample_courses):
    strategy = AllStrategy(sample_courses)
    schedules = strategy.generate()
    assert all(isinstance(s, Schedule) for s in schedules)


def test_generate_conflicting_schedules():
    checker = Mock()
    checker.check_time_conflict.return_value = True
    checker.check_room_conflict.return_value = True
    course1 = Course("C1", "001", "Prof X", ["L1"], ["T1"], ["M1"])
    course2 = Course("C2", "002", "Prof Y", ["L2"], ["T2"], ["M2"])
    strategy = AllStrategy([course1, course2], checker)
    assert strategy.generate() == []

def test_generate_no_courses():
    checker = Mock()
    strategy = AllStrategy([], checker)
    result = strategy.generate()
    assert len(result) == 1
    assert all(isinstance(schedule, Schedule) for schedule in result)
    assert all(len(schedule.lecture_groups) == 0 for schedule in result)
