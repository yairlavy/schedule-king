import pytest
from src.core.scheduler import Scheduler
from src.core.all_strategy import AllStrategy
from src.core.conflict_checker import ConflictChecker
from src.data.models.course import Course
from src.data.models.time_slot import TimeSlot

@pytest.fixture
def sample_courses():
    ts1 = TimeSlot("1", "08:00", "09:00", "101", "A")
    ts2 = TimeSlot("2", "09:00", "10:00", "102", "A")

    course1 = Course("Math", "M101", "Prof. A", [ts1], [ts2], [ts1])
    course2 = Course("CS", "C102", "Prof. B", [ts2], [ts1], [ts2])

    return [course1, course2]

@pytest.fixture
def strategy(sample_courses):
    return AllStrategy(sample_courses, ConflictChecker())

def test_SCHEDULER_INIT_001(sample_courses, strategy):
    """Ensure Scheduler object is created properly with valid input."""
    scheduler = Scheduler(sample_courses, strategy)
    assert isinstance(scheduler, Scheduler)

def test_SCHEDULER_FUNC_GEN_001(sample_courses, strategy):
    """Ensure generate() returns a non-empty list of schedules."""
    scheduler = Scheduler(sample_courses, strategy)
    schedules = scheduler.generate()
    assert isinstance(schedules, list)
    assert len(schedules) >= 1

def test_SCHEDULER_INTEG_001(sample_courses, strategy):
    """Ensure Scheduler + ConflictChecker avoid overlapping time slots."""
    scheduler = Scheduler(sample_courses, strategy)
    schedules = scheduler.generate()

    for schedule in schedules:
        all_slots = []
        for group in schedule.lecture_groups:
            all_slots.extend([group.lecture, group.tirguls, group.maabadas])
        for i in range(len(all_slots)):
            for j in range(i + 1, len(all_slots)):
                slot_a = all_slots[i]
                slot_b = all_slots[j]
                if slot_a is slot_b:
                    continue
                assert not slot_a.conflicts_with(slot_b), f"Conflict found between {slot_a} and {slot_b}"

def test_SCHEDULER_COMP_001(sample_courses, strategy):
    """Ensure generate() returns only conflict-free schedules."""
    scheduler = Scheduler(sample_courses, strategy)
    schedules = scheduler.generate()
    checker = ConflictChecker()

    for schedule in schedules:
        slots = []
        for group in schedule.lecture_groups:
            slots += [group.lecture, group.tirguls, group.maabadas]
        for i in range(len(slots)):
            for j in range(i + 1, len(slots)):
                slot_a = slots[i]
                slot_b = slots[j]
                if slot_a is slot_b:
                    continue
                assert not checker.check_time_conflict(slot_a, slot_b), f"Time conflict between {slot_a} and {slot_b}"

def test_SCHEDULER_INVALID_001():
    """Raise ValueError when more than 7 courses are passed."""
    ts = TimeSlot("1", "08:00", "09:00", "101", "A")
    course = lambda i: Course(f"Course{i}", f"C{i}", "Prof", [ts], [ts], [ts])
    courses = [course(i) for i in range(8)]

    with pytest.raises(ValueError):
        AllStrategy(courses, ConflictChecker())
