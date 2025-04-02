import unittest
from src.core.conflict_checker import ConflictChecker
from src.data.models.time_slot import TimeSlot
from src.data.models.course import Course

class TestConflictCheckerSpec(unittest.TestCase):

    def setUp(self):
        self.checker = ConflictChecker()

    def test_CONFLICTCHECKER_FUNC_TIME_001(self):
        """
        Test Case ID: CONFLICTCHECKER_FUNC_TIME_001
        Type: Functional

        Verifies that check_time_conflict returns True for two TimeSlot
        objects that overlap in time on the same day (even if the room is different),
        and False otherwise.
        """
        ts1 = TimeSlot("3", "10:00", "11:00", "100", "A")
        ts2 = TimeSlot("3", "10:30", "11:30", "200", "B")  # same day, overlapping time
        ts3 = TimeSlot("4", "10:30", "11:30", "200", "B")  # different day

        self.assertTrue(self.checker.check_time_conflict(ts1, ts2))
        self.assertFalse(self.checker.check_time_conflict(ts1, ts3))

    def test_CONFLICTCHECKER_FUNC_ROOM_001(self):
        """
        Test Case ID: CONFLICTCHECKER_FUNC_ROOM_001
        Type: Functional

        Verifies that check_room_conflict returns True for two TimeSlot
        objects that overlap in time, day, and are in the same room and building,
        and False otherwise.
        """
        ts1 = TimeSlot("2", "09:00", "10:00", "101", "C")
        ts2 = TimeSlot("2", "09:30", "10:30", "101", "C")  # same room and time overlap
        ts3 = TimeSlot("2", "09:30", "10:30", "102", "C")  # different room
        ts4 = TimeSlot("2", "09:30", "10:30", "101", "D")  # different building

        self.assertTrue(self.checker.check_room_conflict(ts1, ts2))
        self.assertFalse(self.checker.check_room_conflict(ts1, ts3))
        self.assertFalse(self.checker.check_room_conflict(ts1, ts4))

    def test_CONFLICTCHECKER_FUNC_LIST_001(self):
        """
        Test Case ID: CONFLICTCHECKER_FUNC_LIST_001
        Type: Functional

        Verifies that find_conflicting_courses returns True when at least two
        courses contain overlapping time slots, and False when all are conflict-free.
        """
        ts1 = TimeSlot("1", "08:00", "09:00", "201", "X")
        ts2 = TimeSlot("1", "08:30", "09:30", "202", "X")  # overlaps with ts1
        ts3 = TimeSlot("2", "10:00", "11:00", "203", "Y")  # no overlap

        course1 = Course("Algorithms", "123", "Dr. A", [ts1], [], [])
        course2 = Course("Data Structures", "124", "Dr. B", [ts2], [], [])
        course3 = Course("Databases", "125", "Dr. C", [ts3], [], [])

        self.assertTrue(self.checker.find_conflicting_courses([course1, course2]))
        self.assertFalse(self.checker.find_conflicting_courses([course1, course3]))

if __name__ == '__main__':
    unittest.main()
