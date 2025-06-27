import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QTableWidgetItem
from src.components.course_time_slot_table import CourseTimeSlotTable
from src.models.time_slot import TimeSlot
import os
from PyQt5.QtTest import QTest

# ——— Fixtures ———
@pytest.fixture
def table(qtbot):
    table = CourseTimeSlotTable()
    qtbot.addWidget(table)
    table.show()
    yield table
    table.close()

def get_wait_time():
    return int(os.environ.get("WAIT_TIME", 0))

def make_slot(day="1", start="08:00", end="10:00", room="R1", building="B1"):
    return TimeSlot(day=day, start_time=start, end_time=end, room=room, building=building)

# ——— Tests ———

def test_set_item_visual_state(table, qtbot):
    # Test setting visual state of a table item
    qtbot.wait(get_wait_time())
    brush = QBrush(QColor("yellow"))
    # Set visual state for item at (2, 2)
    table.set_item_visual_state(2, 2, brush, text="TEST", slot_data=("data", "example"))
    item = table.item(2, 2) # Get the item at (2, 2)
    qtbot.wait(get_wait_time())
    
    assert item.text() == "TEST"
    assert item.background().color().rgba() == brush.color().rgba()
    assert item.data(Qt.UserRole) == ("data", "example")

def test_get_slot_data_at_coords(table):
    # Test retrieving slot data at specific coordinates
    slot = make_slot()
    assert table.add_course_time_slot(slot, "lecture") is True
    
    # Get slot data at (0, 0) cause day = "1" (which is 0), start = "08:00" (which is 0 (8-9)), end = "10:00"
    slot = table.get_slot_data_at_coords(0, 0) 
    
    print("Result at (0, 0):")
    for i in slot: print(i)
    assert slot is not None
    assert isinstance(slot[0], TimeSlot)
    assert slot[1] == "lecture"
    assert table.get_slot_data_at_coords(1, 0) is not None # 9:00 - 10:00 is the next slot
    assert table.get_slot_data_at_coords(2, 0) is None # 11:00 -12:00 is the next slot so its None

def test_set_active_time_slot_block(table):
    # Test setting and getting active time slot block
    assert table.active_time_slot_block_for_drag is None
    table.set_active_time_slot_block(("R1", "B1", "tirgul"))
    assert table.active_time_slot_block_for_drag == ("R1", "B1", "tirgul")

def test_add_course_time_slot_success(table, qtbot):
    # Test adding a course time slot successfully
    slot = make_slot(day="3")

    # Add the slot to the table
    ok = table.add_course_time_slot(slot, "tirgul")
    assert ok is True
    assert table.rowSpan(0, 2) == 2 # 08:00 - 10:00 is 2 hours

    # Check the item in the table is a QTableWidgetItem
    item = table.item(0, 2)
    assert isinstance(item, QTableWidgetItem)
    
    # Check the text and background color of the item
    expected_color = table.COLOR_MAP["tirgul"]
    assert item.background().color().rgba() == QBrush(expected_color).color().rgba()
    stored = item.data(Qt.UserRole)
    assert isinstance(stored, tuple) and stored[1] == "tirgul"
    qtbot.wait(get_wait_time())

def test_add_course_time_slot_overlap(table, qtbot):
    # Test adding a course time slot that overlaps with an existing one
    slot1 = make_slot()
    assert table.add_course_time_slot(slot1, "lecture") is True
    slot2 = make_slot()
    assert table.add_course_time_slot(slot2, "lecture") is False

def test_remove_course_time_slot_at_coords(table, qtbot):
    slot = make_slot()
    # Add a course time slot to the table
    assert table.add_course_time_slot(slot, "tirgul") is True
    qtbot.wait(get_wait_time())
    
    # Remove the slot at (0, 0) which corresponds to day "1" and time "08:00 - 10:00"
    # And check if the slot that was removed is the same as the one added
    removed = table.remove_course_time_slot_at_coords(0, 0)
    assert removed is not None
    removed_slot, removed_type = removed
    assert removed_slot == slot
    assert removed_type == "tirgul"
    
    # Check if the item at (0, 0) is cleared
    item = table.item(0, 0)
    assert item.text() == ""
    assert item.data(Qt.UserRole) is None
    assert item.background().color().rgba() == QColor(255, 255, 255).rgba()
    qtbot.wait(get_wait_time())

def test_clear_all_slots(table, qtbot):
    # Test clearing all slots in the table
    slot = make_slot(day="2", start="09:00", end="15:00")
    slot2 = make_slot(day="3", start="10:00", end="12:00")
    slot3 = make_slot(day="4", start="11:00", end="13:00")
    table.add_course_time_slot(slot, "maabada")
    table.add_course_time_slot(slot2, "tirgul")
    table.add_course_time_slot(slot3, "lecture")
    assert table.displayed_slots_start_cells
    qtbot.wait(get_wait_time())
    
    # Clear all slots
    table.clear_all_slots()
    assert table.displayed_slots_start_cells == {}
    for r in range(table.rowCount()):
        for c in range(table.columnCount()):
            item = table.item(r, c)
            assert item.text() == ""
            assert item.background().color().rgba() == QColor(255, 255, 255).rgba()
            assert item.data(Qt.UserRole) is None
    qtbot.wait(get_wait_time())

def test_populate_with_course_slots(table, qtbot):
    # Test populating the table with course slots
    lectures = [make_slot(start="08:00", end="09:00"), make_slot(day="2", start="10:00", end="11:00")]
    tirguls = [make_slot(day="3", start="12:00", end="13:00")]
    maabadas = []
    table.populate_with_course_slots(lectures, tirguls, maabadas)
    qtbot.wait(get_wait_time())
    assert len(table.displayed_slots_start_cells) == 3
    row_12 = 12 - 8
    col_3 = 2
    slot_data = table.get_slot_data_at_coords(row_12, col_3)
    assert slot_data is not None
    assert slot_data[1] == "tirgul"

def test_convert_cell_coords_to_timeslot(table):
    # Test converting cell coordinates to a TimeSlot object
    # given valid cell coordinates (0, 0) corresponds to day "1" and time "08:00 - 09:00"
    slot = table.convert_cell_coords_to_timeslot(0, 0, "X", "Y")
    assert slot is not None
    assert slot.day == "1"
    assert slot.start_time.hour == 8 and slot.end_time.hour == 9
    assert slot.room == "X" and slot.building == "Y"
    assert table.convert_cell_coords_to_timeslot(-1, 0, "X", "Y") is None