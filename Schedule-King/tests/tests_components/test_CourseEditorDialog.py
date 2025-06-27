import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMessageBox
from unittest.mock import patch, MagicMock
from src.components.CourseEditorDialog import CourseEditorDialog
from src.models.course import Course
from src.models.time_slot import TimeSlot
import os

# ——— Fixtures ——————————————————————————————————————————————
@pytest.fixture
def dialog(qtbot):
    courses = [
        Course("Math", "101", "Deni", lectures=[[TimeSlot("1", "08:00", "10:00", "R1", "B1")]]),
        Course("Physics", "102", "Beni", tirguls=[[TimeSlot("2", "10:00", "12:00", "R2", "B2")]])
    ]
    dialog = CourseEditorDialog(all_courses=courses)
    qtbot.addWidget(dialog)
    dialog.show()
    yield dialog
    dialog.close()

def get_wait_time():
    return int(os.environ.get("WAIT_TIME", 0))

def make_slot(day="1", start="08:00", end="10:00", room="R1", building="B1"):
    return TimeSlot(day=day, start_time=start, end_time=end, room=room, building=building)

# ——— Tests ——————————————————————————————————————————————

def test___init__(dialog):
    # Test that the dialog initializes correctly with default UI elements
    assert dialog.windowTitle() == "Add / Edit Course"
    assert dialog.course_combo.count() == 3  # "Create New" + 2 courses
    assert dialog.course_combo.itemText(0) == "--- Select Course to Edit or Create New ---"
    assert dialog.course_combo.itemText(1) == "Math (101)"
    assert dialog.schedule_options_tab_widget.count() == 1  # One empty tab
    assert dialog.name_input.text() == ""
    assert dialog.available_block_templates_list_widget.count() == 0

def test_clear_all_fields(dialog, qtbot):
    # Test clearing all fields and resetting the form
    dialog.name_input.setText("Some Name")
    dialog.code_input.setText("Some Code")
    dialog.instructor_input.setText("Some Instructor")

    # Add an additional schedule option and a block template to ensure they are cleared
    qtbot.mouseClick(dialog.add_schedule_option_button, Qt.LeftButton)
    # Patch the CreateTimeSlotDialog class so that when the code tries to open it,
    # we return our mock data instead of the real dialog
    with patch("src.components.CourseEditorDialog.CreateTimeSlotDialog") as mock_dialog:
        mock_instance = mock_dialog.return_value
        mock_instance.exec_.return_value = QDialog.Accepted
        mock_instance.get_time_slot_data.return_value = ("Room", "Building", "lecture")
        qtbot.mouseClick(dialog.add_new_slot_block_button, Qt.LeftButton)
    qtbot.wait(get_wait_time())

    assert dialog.name_input.text() != ""
    assert dialog.schedule_options_tab_widget.count() > 1
    assert dialog.available_block_templates_list_widget.count() > 0

    dialog.clear_all_fields()
    qtbot.wait(get_wait_time())

    assert dialog.name_input.text() == ""
    assert dialog.code_input.text() == ""
    assert dialog.instructor_input.text() == ""
    assert dialog.schedule_options_tab_widget.count() == 1 # Should reset to one empty tab
    assert dialog.available_block_templates_list_widget.count() == 0
    assert dialog.current_course is None
    assert dialog.course_combo.currentIndex() == 0 # Should reset to "Create New"

def test_on_course_selected(dialog, qtbot):
    # Test selecting an existing course from the dropdown
    dialog.course_combo.setCurrentIndex(1)  # Select "Math (101)"
    qtbot.wait(get_wait_time())
    assert dialog.name_input.text() == "Math"
    assert dialog.code_input.text() == "101"
    assert dialog.instructor_input.text() == "Deni"
    assert dialog.schedule_options_tab_widget.count() == 1 # Math has one lecture option
    table = dialog.schedule_options_tab_widget.widget(0)
    slot_data = table.get_slot_data_at_coords(0, 0)  # Day 1, 08:00-09:00
    assert slot_data is not None
    assert slot_data[0].room == "R1"
    assert slot_data[1] == "lecture"
    assert dialog.current_course.name == "Math"
    assert dialog.available_block_templates_list_widget.count() == 1 # Should populate with existing templates

    # Test selecting "Create New Course"
    dialog.course_combo.setCurrentIndex(0)
    qtbot.wait(get_wait_time())
    assert dialog.name_input.text() == ""
    assert dialog.current_course is None
    assert dialog.schedule_options_tab_widget.count() == 1 # Resets to one empty tab
    assert dialog.available_block_templates_list_widget.count() == 0

def test_on_schedule_option_tab_changed(dialog, qtbot):
    # Test that selecting a different schedule option tab updates the state
    # Add a second schedule option
    qtbot.mouseClick(dialog.add_schedule_option_button, Qt.LeftButton)
    qtbot.wait(get_wait_time())
    
    assert dialog.schedule_options_tab_widget.count() == 2
    
    # Simulate selecting the first tab (index 0)
    dialog.schedule_options_tab_widget.setCurrentIndex(0)
    qtbot.wait(get_wait_time())
    assert dialog.current_schedule_option_index == 0
    
    # Simulate selecting the second tab (index 1)
    dialog.schedule_options_tab_widget.setCurrentIndex(1)
    qtbot.wait(get_wait_time())
    assert dialog.current_schedule_option_index == 1

def test_add_new_schedule_option(dialog, qtbot):
    # Test adding a new schedule option
    initial_tab_count = dialog.schedule_options_tab_widget.count()
    
    # Click the button to add a new schedule option
    qtbot.mouseClick(dialog.add_schedule_option_button, Qt.LeftButton)
    qtbot.wait(get_wait_time())
    
    # Verify a new tab was added
    assert dialog.schedule_options_tab_widget.count() == initial_tab_count + 1
    new_table = dialog.schedule_options_tab_widget.widget(initial_tab_count)
    assert len(new_table.displayed_slots_start_cells) == 0  # Empty table
    assert dialog.current_schedule_option_index == initial_tab_count # New tab should be active

def test_remove_current_schedule_option(dialog, qtbot):
    # Test removing a schedule option and preventing removal of the last one
    # Add a second option
    qtbot.mouseClick(dialog.add_schedule_option_button, Qt.LeftButton)
    qtbot.wait(get_wait_time())
    assert dialog.schedule_options_tab_widget.count() == 2
    
    # Remove the first option
    dialog.schedule_options_tab_widget.setCurrentIndex(0)
    # Mock the remove question popup to simulate pressing it
    with patch.object(QMessageBox, "question", return_value=QMessageBox.Yes):
        with patch.object(QMessageBox, "information") as mock_info:
            mock_info.return_value = QMessageBox.Ok
            qtbot.mouseClick(dialog.remove_schedule_option_button, Qt.LeftButton)
            qtbot.wait(get_wait_time())
            mock_info.assert_called_once()
            assert dialog.schedule_options_tab_widget.count() == 1
    
    # Try removing the last option
    # Mock the remove warning popup to simulate pressing it
    with patch.object(QMessageBox, "warning") as mock_warning:
        qtbot.mouseClick(dialog.remove_schedule_option_button, Qt.LeftButton)
        qtbot.wait(get_wait_time())
        mock_warning.assert_called_once()
        assert dialog.schedule_options_tab_widget.count() == 1

def test_populate_available_block_list(dialog, qtbot):
    # Test populating the available block templates list
    dialog.clear_all_fields() # Start with a clean slate
    qtbot.wait(get_wait_time())
    assert dialog.available_block_templates_list_widget.count() == 0

    # Add some time slots to current option to ensure templates are generated
    current_option_data = dialog.all_schedule_options[0]
    current_option_data["lecture"].append(make_slot(room="L1", building="B1"))
    current_option_data["tirgul"].append(make_slot(room="T1", building="B1"))
    current_option_data["maabada"].append(make_slot(room="M1", building="B1"))
    
    dialog.populate_available_block_list()
    qtbot.wait(get_wait_time())
    
    assert dialog.available_block_templates_list_widget.count() == 3
    items_text = [dialog.available_block_templates_list_widget.item(i).text() for i in range(3)]
    assert "Room: L1 | Building: B1 (lecture)" in items_text
    assert "Room: T1 | Building: B1 (tirgul)" in items_text
    assert "Room: M1 | Building: B1 (maabada)" in items_text

    # Test adding duplicate (should not add new item)
    current_option_data["lecture"].append(make_slot(room="L1", building="B1"))
    dialog.populate_available_block_list()
    qtbot.wait(get_wait_time())
    assert dialog.available_block_templates_list_widget.count() == 3 # Still 3 unique items

def test_open_new_time_slot_block_dialog(dialog, qtbot):
    # Test adding a new time slot block
    # mock the CreateTimeSlotDialog class 
    with patch("src.components.CourseEditorDialog.CreateTimeSlotDialog") as mock_dialog:
        mock_instance = mock_dialog.return_value
        mock_instance.exec_.return_value = QDialog.Accepted
        mock_instance.get_time_slot_data.return_value = ("R3", "B3", "tirgul")

        qtbot.mouseClick(dialog.add_new_slot_block_button, Qt.LeftButton)
        qtbot.wait(get_wait_time())
        
        assert dialog.available_block_templates_list_widget.count() == 1
        item = dialog.available_block_templates_list_widget.item(0)
        assert item.text() == "Room: R3 | Building: B3 (tirgul)"
        assert dialog.active_block_template == ("R3", "B3", "tirgul") # Should be selected

    # Test adding an existing template, which should trigger a popup
    # mock the CreateTimeSlotDialog class 
    with patch("src.components.CourseEditorDialog.CreateTimeSlotDialog") as mock_dialog:
        mock_instance = mock_dialog.return_value
        mock_instance.exec_.return_value = QDialog.Accepted
        mock_instance.get_time_slot_data.return_value = ("R3", "B3", "tirgul") # Same as before
        with patch.object(QMessageBox, "information") as mock_info:
            qtbot.mouseClick(dialog.add_new_slot_block_button, Qt.LeftButton)
            qtbot.wait(get_wait_time())
            mock_info.assert_called_with(dialog, "Template Exists", "This block template already exists.")
            assert dialog.available_block_templates_list_widget.count() == 1 # Still 1 item

def test_remove_selected_block(dialog, qtbot):
    # Test removing a time slot block
    # Add a block
    with patch("src.components.CourseEditorDialog.CreateTimeSlotDialog") as mock_dialog:
        mock_instance = mock_dialog.return_value
        mock_instance.exec_.return_value = QDialog.Accepted
        mock_instance.get_time_slot_data.return_value = ("R4", "B4", "lecture")
        qtbot.mouseClick(dialog.add_new_slot_block_button, Qt.LeftButton)
        qtbot.wait(get_wait_time())
    
    assert dialog.available_block_templates_list_widget.count() == 1
    
    # Remove the block
    dialog.available_block_templates_list_widget.setCurrentRow(0)
    with patch.object(QMessageBox, "question", return_value=QMessageBox.Yes):
        with patch.object(QMessageBox, "information") as mock_info:
            mock_info.return_value = QMessageBox.Ok
            qtbot.mouseClick(dialog.remove_block_template_button, Qt.LeftButton)
            qtbot.wait(get_wait_time())
            mock_info.assert_called_once()
            assert dialog.available_block_templates_list_widget.count() == 0
            assert dialog.active_block_template is None # Should be cleared if it was active

    # Test removing when no block is selected
    with patch.object(QMessageBox, "warning") as mock_warning:
        qtbot.mouseClick(dialog.remove_block_template_button, Qt.LeftButton)
        qtbot.wait(get_wait_time())
        mock_warning.assert_called_once()
        assert "Please select a template block to remove." in mock_warning.call_args[0][2]

    # Test that removing a block also removes associated slots from current schedule option
    dialog.clear_all_fields()
    with patch("src.components.CourseEditorDialog.CreateTimeSlotDialog") as mock_dialog:
        mock_instance = mock_dialog.return_value
        mock_instance.exec_.return_value = QDialog.Accepted
        mock_instance.get_time_slot_data.return_value = ("R_del", "B_del", "lecture")
        qtbot.mouseClick(dialog.add_new_slot_block_button, Qt.LeftButton)
        qtbot.wait(get_wait_time())
    
    dialog.available_block_templates_list_widget.setCurrentRow(0)
    dialog.handle_table_cell_action(0, 0, "add")
    qtbot.wait(get_wait_time())
    
    current_option_data = dialog.all_schedule_options[0]
    assert len(current_option_data["lecture"]) == 1
    assert current_option_data["lecture"][0].room == "R_del"

    with patch.object(QMessageBox, "question", return_value=QMessageBox.Yes):
        with patch.object(QMessageBox, "information", return_value=QMessageBox.Ok):
            qtbot.mouseClick(dialog.remove_block_template_button, Qt.LeftButton)
            qtbot.wait(get_wait_time())
    
    assert len(current_option_data["lecture"]) == 0 # Slot should be removed

def test_on_block_selected(dialog, qtbot):
    # Add a block
    with patch("src.components.CourseEditorDialog.CreateTimeSlotDialog") as mock_dialog:
        mock_instance = mock_dialog.return_value
        mock_instance.exec_.return_value = QDialog.Accepted
        mock_instance.get_time_slot_data.return_value = ("R_select", "B_select", "lecture")
        qtbot.mouseClick(dialog.add_new_slot_block_button, Qt.LeftButton)
        qtbot.wait(get_wait_time())

    # Simulate item click
    item = dialog.available_block_templates_list_widget.item(0)
    dialog.on_block_selected(item)
    qtbot.wait(get_wait_time())

    assert dialog.active_block_template == ("R_select", "B_select", "lecture")

    # Verify the table uses the active block by adding a slot
    dialog.handle_table_cell_action(0, 0, "add")
    qtbot.wait(get_wait_time())
    current_table = dialog.schedule_options_tab_widget.currentWidget()
    slot_data = current_table.get_slot_data_at_coords(0, 0)
    assert slot_data is not None
    assert slot_data[0].room == "R_select"
    assert slot_data[1] == "lecture"

def test_handle_table_cell_action_add(dialog, qtbot):
    # Test adding a time slot via table cell action
    # Add a block
    with patch("src.components.CourseEditorDialog.CreateTimeSlotDialog") as mock_dialog:
        mock_instance = mock_dialog.return_value
        mock_instance.exec_.return_value = QDialog.Accepted
        mock_instance.get_time_slot_data.return_value = ("R5", "B5", "maabada")
        qtbot.mouseClick(dialog.add_new_slot_block_button, Qt.LeftButton)
        qtbot.wait(get_wait_time())
    
    # Select the block (it's auto-selected on creation)
    dialog.available_block_templates_list_widget.setCurrentRow(0)
    
    # Add a slot via table action
    dialog.handle_table_cell_action(0, 0, "add") # Day 1 (index 0), 08:00 (index 0)
    qtbot.wait(get_wait_time())
    table = dialog.schedule_options_tab_widget.widget(0)
    slot_data = table.get_slot_data_at_coords(0, 0)
    assert slot_data is not None
    assert slot_data[0].room == "R5"
    assert slot_data[1] == "maabada"
    
    # Verify the internal data model is updated
    current_option_data = dialog.all_schedule_options[dialog.current_schedule_option_index]
    assert len(current_option_data["maabada"]) == 1
    assert current_option_data["maabada"][0].room == "R5"
    assert current_option_data["maabada"][0].day == "1"
    assert current_option_data["maabada"][0].start_time.strftime("%H:%M") == "08:00"
    assert current_option_data["maabada"][0].end_time.strftime("%H:%M") == "09:00"

    # Try adding without active block template
    dialog.active_block_template = None
    dialog.handle_table_cell_action(1, 0, "add") # Should not add
    qtbot.wait(get_wait_time())
    slot_data_new = table.get_slot_data_at_coords(1, 0)
    assert slot_data_new is None
    assert len(current_option_data["maabada"]) == 1 # Still one slot

def test_handle_table_cell_action_remove(dialog, qtbot):
    # Test removing a time slot via table cell action
    # Add a slot to ensure there's something to remove
    current_option_data = dialog.all_schedule_options[0]
    slot_to_remove = make_slot(day="1", start="08:00", end="09:00", room="Room", building="Building")
    current_option_data["lecture"].append(slot_to_remove)
    dialog.refresh_all_schedule_tables() # Make sure UI reflects it
    qtbot.wait(get_wait_time())

    table = dialog.schedule_options_tab_widget.widget(0)
    slot_data_before = table.get_slot_data_at_coords(0, 0)
    assert slot_data_before is not None
    assert slot_data_before[0].room == "Room"
    
    # Remove the slot
    dialog.handle_table_cell_action(0, 0, "remove") # Day 1 (index 0), 08:00 (index 0)
    qtbot.wait(get_wait_time())
    slot_data_after = table.get_slot_data_at_coords(0, 0)
    assert slot_data_after is None

    # Verify the internal data model is updated
    assert len(current_option_data["lecture"]) == 0

    # Test removing a non-existent slot (should not crash)
    dialog.handle_table_cell_action(1, 1, "remove")
    qtbot.wait(get_wait_time()) # No crash, no change

def test_merge_time_slots(dialog):
    # Test merging consecutive time slots
    option_data = {
        "lecture": [
            make_slot(start="08:00", end="09:00", room="R1", building="B1", day="1"),
            make_slot(start="09:00", end="10:00", room="R1", building="B1", day="1"),
            make_slot(start="11:00", end="12:00", room="R1", building="B1", day="1"),
            make_slot(start="13:00", end="14:00", room="R2", building="B1", day="1"), # Different room
            make_slot(start="14:00", end="15:00", room="R2", building="B1", day="1"),
            make_slot(start="08:00", end="09:00", room="R1", building="B1", day="2") # Different day
        ],
        "tirgul": [],
        "maabada": []
    }
    dialog.merge_time_slots(option_data)
    
    assert len(option_data["lecture"]) == 4
    # Expected merged slots:
    # 08:00-10:00 R1 B1 Day 1
    # 11:00-12:00 R1 B1 Day 1
    # 13:00-15:00 R2 B1 Day 1
    # 08:00-09:00 R1 B1 Day 2

    # Sort for consistent assertion order
    merged_lectures = sorted(option_data["lecture"], key=lambda s: (s.day, s.start_time, s.room))

    assert merged_lectures[0].start_time.strftime("%H:%M") == "08:00"
    assert merged_lectures[0].end_time.strftime("%H:%M") == "10:00"
    assert merged_lectures[0].room == "R1"
    assert merged_lectures[0].day == "1"

    assert merged_lectures[1].start_time.strftime("%H:%M") == "11:00"
    assert merged_lectures[1].end_time.strftime("%H:%M") == "12:00"
    assert merged_lectures[1].room == "R1"
    assert merged_lectures[1].day == "1"

    assert merged_lectures[2].start_time.strftime("%H:%M") == "13:00"
    assert merged_lectures[2].end_time.strftime("%H:%M") == "15:00"
    assert merged_lectures[2].room == "R2"
    assert merged_lectures[2].day == "1"
    
    assert merged_lectures[3].start_time.strftime("%H:%M") == "08:00"
    assert merged_lectures[3].end_time.strftime("%H:%M") == "09:00"
    assert merged_lectures[3].room == "R1"
    assert merged_lectures[3].day == "2"

    # Test with empty list
    empty_option_data = {"lecture": [], "tirgul": [], "maabada": []}
    dialog.merge_time_slots(empty_option_data)
    assert len(empty_option_data["lecture"]) == 0

def test_refresh_all_schedule_tables(dialog, qtbot):
    # Test refreshing all schedule option tables
    # Ensure current state is as expected (one tab, Math course loaded)
    dialog.course_combo.setCurrentIndex(1)  # Select "Math (101)"
    qtbot.wait(get_wait_time())
    table_0 = dialog.schedule_options_tab_widget.widget(0)
    assert len(table_0.displayed_slots_start_cells) > 0 # Math course has a slot

    # Add a new, empty schedule option
    qtbot.mouseClick(dialog.add_schedule_option_button, Qt.LeftButton)
    qtbot.wait(get_wait_time())
    assert dialog.schedule_options_tab_widget.count() == 2
    table_1 = dialog.schedule_options_tab_widget.widget(1)
    assert len(table_1.displayed_slots_start_cells) == 0 # New tab is empty

    # Manually modify the data for the second option (without updating UI)
    dialog.all_schedule_options[1]["tirgul"].append(make_slot(day="3", start="09:00", end="10:00", room="T_new", building="B_new"))
    
    # The UI for table_1 should still be empty until refresh is called
    assert table_1.get_slot_data_at_coords(1, 2) is None # 09:00 (index 1), Day 3 (index 2),

    dialog.refresh_all_schedule_tables()
    qtbot.wait(get_wait_time())

    # Now the UI for table_1 should reflect the change
    slot_data_on_table = table_1.get_slot_data_at_coords(1, 2)
    assert slot_data_on_table is not None
    assert slot_data_on_table[0].room == "T_new"
    assert slot_data_on_table[1] == "tirgul"
    
    # Ensure the first table is still correct
    slot_data_table0 = table_0.get_slot_data_at_coords(0, 0)
    assert slot_data_table0 is not None
    assert slot_data_table0[0].room == "R1"
    assert slot_data_table0[1] == "lecture"

def test_accept_successful(dialog, qtbot):
    # Test saving a new course with details and time slots
    # Fill course details
    dialog.name_input.setText("Chemistry")
    dialog.code_input.setText("103")
    dialog.instructor_input.setText("Dr. C")
    
    # Add a time slot block
    with patch("src.components.CourseEditorDialog.CreateTimeSlotDialog") as mock_dialog:
        mock_instance = mock_dialog.return_value
        mock_instance.exec_.return_value = QDialog.Accepted
        mock_instance.get_time_slot_data.return_value = ("R6", "B6", "tirgul")
        qtbot.mouseClick(dialog.add_new_slot_block_button, Qt.LeftButton)
        qtbot.wait(get_wait_time())
        
    # Select the block and add a slot
    dialog.available_block_templates_list_widget.setCurrentRow(0)
    dialog.handle_table_cell_action(0, 0, "add") # Day 1, 08:00
    qtbot.wait(get_wait_time())
    
    # Mock the courseEdited signal
    mock = MagicMock()
    dialog.courseEdited.connect(mock)
    
    # Save the course
    qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
    qtbot.wait(get_wait_time())
    
    # Verify the dialog result
    assert dialog.result() == QDialog.Accepted

    # Verify the emitted course data
    mock.assert_called_once()
    course = mock.call_args[0][0]
    assert course.name == "Chemistry"
    assert course.course_code == "103"
    assert course.instructor == "Dr. C"
    # Ensure tirguls list is correctly populated
    assert len(course.tirguls) == 1
    assert len(course.tirguls[0]) == 1 # A list of lists, expecting one inner list with one slot
    assert course.tirguls[0][0].room == "R6"
    assert course.tirguls[0][0].day == "1"
    assert course.tirguls[0][0].start_time.strftime("%H:%M") == "08:00"
    assert course.tirguls[0][0].end_time.strftime("%H:%M") == "09:00"

    assert len(course.lectures) == 0 # No lectures added
    assert len(course.maabadas) == 0 # No maabadas added

    # Test editing an existing course
    dialog.course_combo.setCurrentIndex(1) # Select Math course
    qtbot.wait(get_wait_time())
    dialog.instructor_input.setText("New Instructor A")
    
    mock_edit = MagicMock()
    dialog.courseEdited.connect(mock_edit)
    qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
    qtbot.wait(get_wait_time())
    assert dialog.result() == QDialog.Accepted
    mock_edit.assert_called_once()
    edited_course = mock_edit.call_args[0][0]
    assert edited_course.name == "Math"
    assert edited_course.instructor == "New Instructor A"


def test_accept_empty_fields(dialog, qtbot):
    # Test that saving with empty fields shows a warning
    # Ensure fields are empty
    dialog.name_input.clear()
    dialog.code_input.clear()
    dialog.instructor_input.clear()

    with patch.object(QMessageBox, "warning") as mock_warning:
        qtbot.mouseClick(dialog.save_button, Qt.LeftButton)
        qtbot.wait(get_wait_time())
        mock_warning.assert_called_once()
        assert "Please fill in all course details." in mock_warning.call_args[0][2]
        assert dialog.result() != QDialog.Accepted

def test_cancel_button(dialog, qtbot):
    # Test the cancel button closes the dialog with reject
    qtbot.mouseClick(dialog.cancel_button, Qt.LeftButton)
    qtbot.wait(get_wait_time())
    assert dialog.result() == QDialog.Rejected