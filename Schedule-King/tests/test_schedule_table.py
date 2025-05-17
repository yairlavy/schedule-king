import pytest
import os
import datetime
from unittest.mock import Mock
from src.components.schedule_table import ScheduleTable

def get_wait_time():
    return int(os.environ.get("WAIT_TIME", 0))

def setup_table(qtbot):
    table = ScheduleTable()
    qtbot.addWidget(table)
    table.resize(1024, 600)
    table.show()
    return table

def test_display_schedule_basic(qtbot):
    # mock time slots for the courses
    slot1 = Mock()
    slot1.start_time = datetime.time(9, 0)
    slot1.end_time = datetime.time(10, 0)
    slot1.room, slot1.building = "101", "22"

    slot2 = Mock()
    slot2.start_time = datetime.time(10, 0)
    slot2.end_time = datetime.time(11, 0)
    slot2.room, slot2.building = "101", "22"

    slot3 = Mock()
    slot3.start_time = datetime.time(8, 0)
    slot3.end_time = datetime.time(9, 0)
    slot3.room, slot3.building = "102", "061"

    slot4 = Mock()
    slot4.start_time = datetime.time(12, 0)
    slot4.end_time = datetime.time(13, 0)
    slot4.room, slot4.building = "301", "42"

    # Mock schedule with the courses
    schedule = Mock()
    schedule.extract_by_day.return_value = {
        "1": [("Lecture", "Calculus", "101", slot1),
              ("Tirgul", "Calculus", "101", slot2)],
        "2": [("Lecture", "Physics", "102", slot3)],
        "4": [("Mabada", "Physics", "301", slot4)],
    }

    # Set up the table and populate with data
    table = setup_table(qtbot)
    table.display_schedule(schedule)
    qtbot.wait(get_wait_time())

    # Sunday 09:00 - Lecture: "Calculus"
    w1 = table.cellWidget(1, 0)  # Row 1, Column 0
    assert w1 is not None
    text1 = w1.text()
    assert "Calculus" in text1
    assert "Room: 101" in text1
    assert "Building: 22" in text1

    # Sunday 10:00 - Tirgul: "Calculus"
    w2 = table.cellWidget(2, 0)  # Row 2, Column 0 
    assert w2 is not None
    text2 = w2.text()
    assert "Calculus" in text2
    assert "Room: 101" in text2
    assert "Building: 22" in text2

    # Tuesday 08:00 - Lecture: "Physics"
    w3 = table.cellWidget(0, 1)  # Row 0, Column 1
    assert w3 is not None
    text3 = w3.text()
    assert "Physics" in text3
    assert "Room: 102" in text3
    assert "Building: 061" in text3

    # Thursday 12:00 - Mabada: "Physics"
    w4 = table.cellWidget(4, 3)  # Row 4, Column 3
    assert w4 is not None
    text4 = w4.text()
    assert "Physics" in text4
    assert "Room: 301" in text4
    assert "Building: 42" in text4

def test_course_more_than_1_hour(qtbot):
    slot1 = Mock()
    slot1.start_time = datetime.time(9, 0)
    slot1.end_time = datetime.time(11, 0)  # 2-hour lecture
    slot1.room, slot1.building = "101", "A"

    # Return a list with one lecture tuple
    schedule = Mock()
    schedule.extract_by_day.return_value = {
        "1": [("Lecture", "Math", "101", slot1)]
    }

    table = setup_table(qtbot)
    table.display_schedule(schedule)
    qtbot.wait(get_wait_time())

    # The lecture spans 9:00–11:00, so it should fill rows for 9:00-10:00 and 10:00-11:00
    # First slot should have full details
    widget1 = table.cellWidget(1, 0)  # Sunday 9:00-10:00
    assert widget1 is not None
    txt1 = widget1.text()
    assert "Math (101)" in txt1
    assert "Room: 101" in txt1
    assert "Building: A" in txt1

    # Second slot should show continuation
    widget2 = table.cellWidget(2, 0)  # Sunday 10:00-11:00
    assert widget2 is not None
    txt2 = widget2.text()
    assert "Math" in txt2
    assert "(continued)" in txt2

    # It should not fill 11:00
    widget3 = table.cellWidget(3, 0)
    assert widget3 is None


def test_duplicate_same_slot(qtbot):
    slot = Mock(); slot.start_time = datetime.time(9, 0); slot.end_time = datetime.time(10, 0)
    slot.room, slot.building = "101", "A"

    schedule = Mock()
    schedule.extract_by_day.return_value = {
        "1": [("Lecture", "Math", "M101", slot),
              ("Lecture", "Math", "M101", slot)]
    }

    table = setup_table(qtbot)
    table.display_schedule(schedule)
    qtbot.wait(get_wait_time())

    # Same slot twice → only one widget in Sunday column
    widgets = table.cellWidget(1, 0)
    assert widgets is not None
    assert "Math (M101)" in widgets.text()

def test_display_schedule_empty(qtbot):
    """
    An empty schedule should leave all cells blank.
    """
    schedule = Mock()
    schedule.extract_by_day.return_value = {}

    table = setup_table(qtbot)
    table.display_schedule(schedule)
    qtbot.wait(get_wait_time())

    for r in range(table.rowCount()):
        for c in range(table.columnCount()):
            assert table.item(r, c) is None

def test_display_schedule_out_of_range_times(qtbot):
    #Slots outside 08:00–20:00 should be ignored.
    slot_before = Mock(); slot_before.start_time = datetime.time(7,0);  slot_before.end_time = datetime.time(8,0)
    slot_before.room, slot_before.building = "101","A"
    slot_after  = Mock(); slot_after.start_time  = datetime.time(20,0); slot_after.end_time  = datetime.time(21,0)
    slot_after.room, slot_after.building = "102","A"

    schedule = Mock()
    schedule.extract_by_day.return_value = {
        "1":[("Lecture","Math","101",slot_before),
             ("Tirgul","Math","101",slot_after)]
    }

    table = setup_table(qtbot)
    table.display_schedule(schedule)
    qtbot.wait(get_wait_time())

    for r in range(table.rowCount()):
        for c in range(table.columnCount()):
            assert table.item(r, c) is None


def test_fill_all_schedule_cells(qtbot):    
    #Generate a full schedule with 12 hours for each of the 7 days
    schedule = Mock()
    schedule.extract_by_day.return_value = {
        str(day): [
            (
                "Lecture",
                f"Course {day * 12 + hour}",
                f"M{day * 12 + hour}",
                Mock(
                    start_time=datetime.time(8 + hour),
                    end_time=datetime.time(9 + hour),
                    room="101",
                    building="A"
                )
            )
            for hour in range(12)
        ]
        for day in range(7)
    }

    table = setup_table(qtbot)
    table.display_schedule(schedule)
    qtbot.wait(get_wait_time())

    # Assert all 12×7 cells are filled
    for row in range(table.rowCount()):
        for col in range(table.columnCount()):
            assert table.item(row, col) is not None, f"Missing item at ({row}, {col})"