import pytest
from src.services.scheduler import Scheduler
from src.services.all_strategy import AllStrategy
from src.services.conflict_checker import ConflictChecker
from src.models.course import Course
from src.models.time_slot import TimeSlot

@pytest.fixture
def sample_courses():
    ts1 = TimeSlot("1", "08:00", "09:00", "101", "A")
    ts2 = TimeSlot("2", "09:00", "10:00", "101", "A")  
    ts3 = TimeSlot("3", "10:00", "11:00", "101", "A")  

    ts4 = TimeSlot("4", "11:00", "12:00", "102", "A")  
    ts5 = TimeSlot("5", "12:00", "13:00", "102", "A")  
    ts6 = TimeSlot("6", "13:00", "14:00", "102", "A") 

    course1 = Course("Math", "M101", "Prof. A", [ts1], [ts2], [ts3])
    course2 = Course("CS", "C102", "Prof. B", [ts4], [ts5], [ts6])

    return [course1, course2]

@pytest.fixture
def strategy(sample_courses):
    return AllStrategy(sample_courses)

def test_SCHEDULER_INIT_001(sample_courses, strategy):
    """Ensure Scheduler object is created properly with valid input."""
    scheduler = Scheduler(sample_courses, strategy)
    assert isinstance(scheduler, Scheduler)

def test_SCHEDULER_FUNC_GEN_001(sample_courses, strategy):
    """Ensure generate() returns a non-empty list of schedules."""
    scheduler = Scheduler(sample_courses, strategy)
    schedules = scheduler.generate()

    # Debugging: print the generated schedules
    print(f"Generated {len(schedules)} schedules.")
    if schedules:
        for idx, schedule in enumerate(schedules):
            print(f"Schedule {idx + 1}:")
            for group in schedule.lecture_groups:
                print(f"  Course: {group.course_name}")
                print(f"    Lecture: {group.lecture.start_time} - {group.lecture.end_time}")
                if group.tirguls:
                    print(f"    Tirgul: {group.tirguls.start_time} - {group.tirguls.end_time}")
                if group.maabadas:
                    print(f"    Maabada: {group.maabadas.start_time} - {group.maabadas.end_time}")

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

def test_SCHEDULER_VALID_001(sample_courses, strategy):
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