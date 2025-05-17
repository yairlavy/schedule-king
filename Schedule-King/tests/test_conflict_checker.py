import pytest
from src.services.conflict_checker import ConflictChecker
from src.models.time_slot import TimeSlot
from src.models.lecture_group import LectureGroup

# Helper function to create TimeSlot for tests
def make_timeslot(day, start, end):
    return TimeSlot(day, start, end, "101", "A")

@pytest.fixture
def checker():
    """Provides a fresh instance of ConflictChecker for each test."""
    return ConflictChecker()

def test_has_conflict_with_real_checker_conflict(checker):
    """
    Test Case ID: CONFLICTCHECKER_FUNC_002
    Purpose: Verify that ConflictChecker correctly detects conflicts between LectureGroups 
    that have overlapping TimeSlots on the same day.
    """
    slot1 = make_timeslot("1", start="12:00", end="14:00")
    slot2 = make_timeslot("1", start="13:00", end="15:00")  # Overlapping times on same day

    group1 = LectureGroup("Course1", "C1", "Instructor A", lecture=slot1, tirguls=None, maabadas=None)
    group2 = LectureGroup("Course2", "C2", "Instructor B", lecture=slot2, tirguls=None, maabadas=None)

    assert checker.has_conflict_groups([group1, group2]), "Expected conflict but none was detected."


def test_has_conflict_with_real_checker_no_conflict(checker):
    """
    Test Case ID: CONFLICTCHECKER_FUNC_003
    Purpose: Verify that ConflictChecker identifies no conflicts when LectureGroups 
    have non-overlapping TimeSlots on the same or different days.
    """
    slot1 = make_timeslot("1", start="08:00", end="09:00")
    slot2 = make_timeslot("1", start="10:00", end="11:00")

    group1 = LectureGroup("Course1", "C1", "Instructor A", lecture=slot1, tirguls=None, maabadas=None)
    group2 = LectureGroup("Course2", "C2", "Instructor B", lecture=slot2, tirguls=None, maabadas=None)

    assert not checker.has_conflict_groups([group1, group2]), "Expected no conflict but a conflict was detected."


def test_conflictchecker_func_list_001(checker):
    """
    Test Case ID: CONFLICTCHECKER_FUNC_LIST_001
    Purpose: Verify that ConflictChecker detects conflicts in a list of LectureGroups
    with overlapping TimeSlots, and returns no conflict when slots are on different days.
    """
    ts1 = TimeSlot("1", "08:00", "09:00", "201", "X")
    ts2 = TimeSlot("1", "08:30", "09:30", "202", "X")  # Overlaps with ts1
    ts3 = TimeSlot("2", "10:00", "11:00", "203", "Y")  # No overlap (different day)

    group1 = LectureGroup("Algorithms", "123", "Dr. A", lecture=ts1, tirguls=None, maabadas=None)
    group2 = LectureGroup("Data Structures", "124", "Dr. B", lecture=ts2, tirguls=None, maabadas=None)
    group3 = LectureGroup("Databases", "125", "Dr. C", lecture=ts3, tirguls=None, maabadas=None)

    # Expect conflict between group1 and group2 (overlapping on same day)
    assert checker.has_conflict_groups([group1, group2]), "Expected conflict between overlapping groups."

    # Expect no conflict between group1 and group3 (different days)
    assert not checker.has_conflict_groups([group1, group3]), "Expected no conflict between groups on different days."
