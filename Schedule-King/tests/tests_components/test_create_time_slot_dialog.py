from unittest.mock import patch
import pytest
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QMessageBox
from PyQt5.QtCore import Qt
from src.components.create_time_slot_dialog import CreateTimeSlotDialog
import os

# ——— Fixtures ——————————————————————————————————————————————
@pytest.fixture
def dialog(qtbot):
    """Create and expose the CreateTimeSlotDialog for tests."""
    dialog = CreateTimeSlotDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    yield dialog
    dialog.close()

def get_wait_time():
    return int(os.environ.get("WAIT_TIME", 0))

# ——— Tests ——————————————————————————————————————————————

def test_initial_state_has_no_data(dialog):
    # Assert dialog starts with empty fields and no data
    assert dialog.get_time_slot_data() is None
    assert dialog.result() == 0

def test_default_combo_contains_expected_items(dialog):
    # Check initial state of combo box
    assert dialog.type_combo.count() == 3
    labels = [dialog.type_combo.itemText(i) for i in range(dialog.type_combo.count())]
    data   = [dialog.type_combo.itemData(i) for i in range(dialog.type_combo.count())]
    
    # Expected labels and data
    assert labels == ["Lecture", "Tirgul", "Maabada"]
    assert data   == ["lecture", "tirgul", "maabada"]

def test_get_time_slot_data(dialog):
    # Simulate geting time slot data after filling fields
    dialog.time_slot_data = ("Room", "Building", "lecture")
    
    # check if get_time_slot_data returns the correct tuple
    assert dialog.get_time_slot_data() == ("Room", "Building", "lecture")

def test_accept_with_all_fields_filled(dialog, qtbot):
    # Fill fields, then show populated dialog for visual debug
    dialog.room_input.setText("Room")
    dialog.building_input.setText("Building")
    dialog.type_combo.setCurrentIndex(2) # Maabada
    qtbot.wait(get_wait_time())

    ok_btn = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok)
    qtbot.mouseClick(ok_btn, Qt.LeftButton)
    qtbot.wait(get_wait_time())

    # Assert dialog was accepted and data is correct
    assert dialog.result() == QDialog.Accepted
    assert dialog.get_time_slot_data() == ("Room", "Building", "maabada")

def test_warning_shown_and_not_accepted_on_empty_fields(dialog, qtbot):
    # Patch QMessageBox.warning to prevent actual dialog and allow assertions
    with patch.object(QMessageBox, "warning") as mock_warning:

        # Click OK to trigger validation (with empty fields)
        ok_btn = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok)
        qtbot.mouseClick(ok_btn, Qt.LeftButton)

        # Assert that QMessageBox.warning was called once
        mock_warning.assert_called_once()

        # Check warning message content
        _, title, text, *_ = mock_warning.call_args[0]
        assert title == "Input Error"
        assert text == "Please fill in all fields."

        # Confirm dialog was not accepted
        assert dialog.result() != QDialog.Accepted
        assert dialog.get_time_slot_data() is None

def test_cancel_button_rejects(dialog, qtbot):
    # Fill some fields, then click cancel
    dialog.room_input.setText("room")
    dialog.building_input.setText("building")
    dialog.type_combo.setCurrentIndex(1) # Tirgul
    qtbot.wait(get_wait_time())

    cancel_btn = dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Cancel)
    qtbot.mouseClick(cancel_btn, Qt.LeftButton)

    # Assert dialog was rejected and no data returned
    assert dialog.result() == QDialog.Rejected
    assert dialog.get_time_slot_data() is None