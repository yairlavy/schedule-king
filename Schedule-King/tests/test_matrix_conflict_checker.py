from src.models.time_slot import TimeSlot
from src.services.MatrixConflicChecker import MatrixConflictChecker

def test_matrix_conflict_checker_time_conflict():
    checker = MatrixConflictChecker()

    # Slot 1: Monday 10:00–12:00 (day="2")
    slot1 = TimeSlot(day="2", start_time="10:00", end_time="12:00", building="A", room="101")

    # Slot 2: Monday 11:00–13:00 (overlaps with slot1)
    slot2 = TimeSlot(day="2", start_time="11:00", end_time="13:00", building="B", room="202")

    assert checker.can_place(slot1) is True
    checker.place(slot1)

    # Should conflict with slot1
    assert checker.can_place(slot2) is False

def test_matrix_conflict_checker_no_conflict():
    checker = MatrixConflictChecker()

    # Slot 1: Tuesday 08:00–10:00 (day="3")
    slot1 = TimeSlot(day="3", start_time="08:00", end_time="10:00", building="C", room="301")

    # Slot 2: Tuesday 10:00–12:00 (non-overlapping)
    slot2 = TimeSlot(day="3", start_time="10:00", end_time="12:00", building="C", room="301")

    assert checker.can_place(slot1) is True
    checker.place(slot1)

    assert checker.can_place(slot2) is True
    checker.place(slot2)

def test_matrix_conflict_checker_remove_slot():
    checker = MatrixConflictChecker()

    # Slot: Wednesday 09:00–11:00 (day="4")
    slot = TimeSlot(day="4", start_time="09:00", end_time="11:00", building="D", room="401")

    checker.place(slot)
    assert checker.can_place(slot) is False

    checker.remove(slot)
    assert checker.can_place(slot) is True