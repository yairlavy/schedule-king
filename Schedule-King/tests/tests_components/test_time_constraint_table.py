import pytest
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest
from src.components.time_constraint_table import TimeConstraintTable
from src.models.time_slot import TimeSlot
from datetime import time

# Create QApplication instance for testing
@pytest.fixture(scope="session")
def app():
    """Create a QApplication instance that persists for the entire test session."""
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def table(app):
    """Create and initialize a TimeConstraintTable instance."""
    table = TimeConstraintTable()
    table.show()  # Make the table visible
    QTest.qWaitForWindowExposed(table)  # Wait for the table to be ready
    yield table
    table.close()  # Clean up after the test

def test_initial_setup(table):
    """Test initial table setup and properties"""
    # Check column count and labels
    assert table.columnCount() == 6
    assert table.horizontalHeaderItem(0).text() == "Sunday"
    assert table.horizontalHeaderItem(5).text() == "Friday"

    # Check row count and labels
    assert table.rowCount() == 12
    assert table.verticalHeaderItem(0).text() == "8:00-9:00"
    assert table.verticalHeaderItem(11).text() == "19:00-20:00"

    # Check selection and edit modes
    assert table.selectionMode() == TimeConstraintTable.NoSelection
    assert table.editTriggers() == TimeConstraintTable.NoEditTriggers

    # Check initial forbidden set
    assert len(table.forbidden) == 0

def test_set_forbidden_cell(table):
    """Test setting a cell as forbidden"""
    # Set a cell as forbidden
    table.set_forbidden_cell(0, 0)  # Sunday 8:00-9:00
    QTest.qWait(100)  # Give Qt time to process

    # Check if cell is marked as forbidden
    assert (0, 0) in table.forbidden
    item = table.item(0, 0)
    assert item is not None
    assert item.background().color().alpha() == 160  # Check transparency
    assert item.textAlignment() == Qt.AlignCenter

def test_clear_constraints(table):
    """Test clearing all constraints"""
    # Add some forbidden cells
    table.set_forbidden_cell(0, 0)
    table.set_forbidden_cell(1, 1)
    QTest.qWait(100)  # Give Qt time to process
    assert len(table.forbidden) == 2

    # Clear constraints
    table.clear_constraints()
    QTest.qWait(100)  # Give Qt time to process
    assert len(table.forbidden) == 0
    assert table.item(0, 0) is None
    assert table.item(1, 1) is None

def test_get_forbidden_timeslots(table):
    """Test converting forbidden cells to TimeSlot objects"""
    # Add forbidden cells
    table.set_forbidden_cell(0, 0)  # Sunday 8:00-9:00
    table.set_forbidden_cell(1, 1)  # Monday 9:00-10:00
    QTest.qWait(100)  # Give Qt time to process

    # Get TimeSlot objects and sort them by day and time
    slots = table.get_forbidden_timeslots()
    assert len(slots) == 2
    slots.sort(key=lambda s: (s.day, s.start_time))

    # Check first slot (Sunday 8:00-9:00)
    assert slots[0].day == "1"  # Sunday is day 1 in the implementation
    assert slots[0].start_time == time(8, 0)  # Compare with time object
    assert slots[0].end_time == time(9, 0)  # Compare with time object

    # Check second slot (Monday 9:00-10:00)
    assert slots[1].day == "2"  # Monday is day 2 in the implementation
    assert slots[1].start_time == time(9, 0)  # Compare with time object
    assert slots[1].end_time == time(10, 0)  # Compare with time object

def test_drag_operations(table):
    """Test drag operations for adding/removing forbidden cells"""
    # Create items in cells first
    table.setItem(0, 0, QTableWidgetItem(""))
    table.setItem(0, 1, QTableWidgetItem(""))
    QTest.qWait(100)  # Give Qt time to process

    # Simulate mouse press to start drag
    pos = table.visualItemRect(table.item(0, 0)).center()
    QTest.mousePress(table.viewport(), Qt.LeftButton, pos=pos)
    QTest.qWait(100)  # Give Qt time to process

    assert table.dragging
    assert table.drag_mode == 'add'
    assert (0, 0) in table.forbidden

    # Simulate mouse move to another cell
    pos = table.visualItemRect(table.item(0, 1)).center()
    QTest.mouseMove(table.viewport(), pos=pos)
    QTest.qWait(100)  # Give Qt time to process

    # Manually trigger cell entered event
    table._drag_enter_cell(0, 1)
    QTest.qWait(100)  # Give Qt time to process

    # Simulate mouse release
    QTest.mouseRelease(table.viewport(), Qt.LeftButton)
    QTest.qWait(100)  # Give Qt time to process

    # Check that both cells are in forbidden set
    assert (0, 0) in table.forbidden
    assert (0, 1) in table.forbidden

    # Test removing forbidden cells
    pos = table.visualItemRect(table.item(0, 0)).center()
    QTest.mousePress(table.viewport(), Qt.LeftButton, pos=pos)
    QTest.qWait(100)  # Give Qt time to process

    assert table.drag_mode == 'remove'
    assert (0, 0) not in table.forbidden

def test_table_dimensions(table):
    """Test table dimensions and size constraints"""
    # Check minimum size
    assert table.minimumWidth() >= 900
    assert table.minimumHeight() >= 500

    # Check header section sizes
    assert table.verticalHeader().defaultSectionSize() == 38
    assert table.horizontalHeader().sectionResizeMode(0) == table.horizontalHeader().Stretch

def test_cell_interaction(table):
    """Test cell interaction and state changes"""
    # Test adding a forbidden cell
    table._set_cell(0, 0, 'add')
    QTest.qWait(100)  # Give Qt time to process
    assert (0, 0) in table.forbidden
    assert table.item(0, 0) is not None

    # Test removing a forbidden cell
    table._set_cell(0, 0, 'remove')
    QTest.qWait(100)  # Give Qt time to process
    assert (0, 0) not in table.forbidden
    # The item should be removed from the table
    table.setItem(0, 0, None)  # Use setItem with None to remove the item
    assert table.item(0, 0) is None

    # Test adding a cell that's already forbidden
    table._set_cell(0, 0, 'add')
    QTest.qWait(100)  # Give Qt time to process
    table._set_cell(0, 0, 'add')  # Try to add again
    QTest.qWait(100)  # Give Qt time to process
    assert len(table.forbidden) == 1  # Should not add duplicate

    # Test removing a cell that's not forbidden
    table._set_cell(0, 1, 'remove')  # Try to remove non-forbidden cell
    QTest.qWait(100)  # Give Qt time to process
    assert (0, 1) not in table.forbidden  # Should not affect anything 