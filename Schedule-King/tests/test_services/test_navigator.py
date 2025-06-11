# -*- coding: utf-8 -*-
"""
Test cases for the Navigator class in the Schedule-King application.
This module contains unit tests for the Navigator class, which is responsible
for navigating through a list of schedules in the application.
The tests cover various functionalities of the Navigator class, including
initialization, navigation between schedules, and user input handling.
"""
import pytest
import sys
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtTest import QSignalSpy
from PyQt5.QtCore import Qt

# Import the class under test
from src.components.navigator import Navigator

# --- Resetting Navigator State ---
Navigator.available_count = 0

# --- Global QApplication Fixture ---
@pytest.fixture(scope="session", autouse=True)
def qapp():
    """
    Fixture to ensure a single QApplication instance for all tests.

    This fixture is applied automatically to all tests in the session,
    ensuring that a QApplication instance is available for any test
    that requires it. This is essential for tests involving PyQt
    components, as QApplication is required for any GUI operations.
    """

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

# --- Fixtures ---
@pytest.fixture
def navigator_with_schedules():
    nav = Navigator(5)
    nav.set_schedules(5)
    return nav

@pytest.fixture
def navigator_with_no_schedules():
    nav = Navigator(0)
    nav.set_schedules(0)
    return nav

@pytest.fixture
def navigator_factory():
    def _factory(schedules):
        return Navigator(schedules)
    return _factory

@pytest.fixture
def patch_warning(monkeypatch):
    mock_warning = MagicMock()
    monkeypatch.setattr(QMessageBox, "warning", mock_warning)
    return mock_warning

class TestNavigator:
    def test_init_with_positive_count(self):
        count = 5
        nav = Navigator(count)
        nav.set_schedules(count)
        assert nav.available_count == count
        assert nav.current_index == 0
        assert nav.prev_btn.toolTip() == "Previous Schedule"
        assert nav.next_btn.toolTip() == "Next Schedule"
        assert nav.schedule_num.placeholderText() == "Jump to..."
        validator = nav.schedule_num.validator()
        assert validator.bottom() == 1
        assert validator.top() == count

    def test_init_with_zero_count(self):
        nav = Navigator(0)
        nav.set_schedules(0)
        assert nav.available_count == 0
        assert nav.current_index == 0

    def test_valid_index_returns_index(self, navigator_with_schedules):
        nav = navigator_with_schedules
        nav.current_index = 3
        assert nav.get_current_schedule() == 3

    def test_index_out_of_bounds_returns_none(self, navigator_with_schedules):
        nav = navigator_with_schedules
        nav.current_index = nav.available_count + 1
        assert nav.get_current_schedule() is None

    def test_negative_index_returns_none(self, navigator_with_schedules):
        nav = navigator_with_schedules
        nav.current_index = -1
        assert nav.get_current_schedule() is None

    def test_none_index_raises(self, navigator_with_schedules):
        nav = navigator_with_schedules
        nav.current_index = None
        with pytest.raises(TypeError):
            nav.get_current_schedule()

    def test_increment_index_and_emit(self):
        nav = Navigator(3)
        nav.set_schedules(3)
        nav.current_index = 0
        nav.update_display = MagicMock()
        emitted = []
        nav.schedule_changed.connect(lambda i: emitted.append(i))
        nav.go_to_next()
        assert nav.current_index == 1
        assert emitted == [1]
        nav.update_display.assert_called_once()

    def test_no_op_at_end(self, navigator_with_schedules):
        nav = navigator_with_schedules
        nav.update_display = MagicMock()
        nav.current_index = nav.available_count - 1
        emitted = []
        nav.schedule_changed.connect(lambda i: emitted.append(i))
        nav.go_to_next()
        assert emitted == []
        nav.update_display.assert_not_called()

    def test_decrement_index_and_emit(self, navigator_with_schedules, qtbot):
        nav = navigator_with_schedules
        nav.current_index = 2
        with qtbot.waitSignal(nav.schedule_changed, timeout=100) as sig:
            nav.go_to_previous()
        assert nav.current_index == 1
        assert sig.args == [1]

    def test_no_op_at_start(self, navigator_with_schedules, qtbot):
        nav = navigator_with_schedules
        nav.current_index = 0
        nav.update_display = MagicMock()
        spy = QSignalSpy(nav.schedule_changed)
        nav.go_to_previous()
        assert not spy
        nav.update_display.assert_not_called()

    def test_valid_input_emits(self, navigator_with_schedules, patch_warning):
        nav = navigator_with_schedules
        nav.update_display = MagicMock()
        nav.schedule_num.setText("2")
        spy = MagicMock()
        nav.schedule_changed.connect(spy)
        nav.on_schedule_num_entered()
        assert nav.current_index == 1
        spy.assert_called_once_with(1)
        nav.update_display.assert_called_once()
        patch_warning.assert_not_called()

    def test_out_of_range_input_warns(self, navigator_with_schedules, patch_warning):
        nav = navigator_with_schedules
        nav.schedule_num.setText(str(nav.available_count + 1))
        nav.current_index = 1
        nav.on_schedule_num_entered()
        patch_warning.assert_called_once()
        assert nav.schedule_num.text() == "2"

    def test_invalid_input_warns(self, navigator_with_schedules, patch_warning):
        nav = navigator_with_schedules
        nav.schedule_num.setText("abc")
        nav.current_index = 1
        nav.on_schedule_num_entered()
        patch_warning.assert_called_once()
        assert nav.schedule_num.text() == "2"

    def test_set_new_count_emits_signal(self, navigator_factory):
        nav = navigator_factory(0)
        nav.update_display = MagicMock()
        spy = QSignalSpy(nav.schedule_changed)
        nav.set_schedules(4)
        assert nav.available_count == 4
        assert nav.current_index == 0
        assert len(spy) == 0

    def test_set_zero_count(self, navigator_factory):
        nav = navigator_factory(2)
        nav.update_display = MagicMock()
        spy = QSignalSpy(nav.schedule_changed)
        nav.set_schedules(0)
        assert nav.available_count == 0
        assert nav.current_index == 0
        assert len(spy) == 0

    def test_first_schedule_ui(self, navigator_with_schedules):
        nav = navigator_with_schedules
        nav.current_index = 0
        nav.update_display()
        assert nav.info_label.text() == f"Schedule 1 of {nav.available_count}"
        assert not nav.prev_btn.isEnabled()
        assert nav.next_btn.isEnabled()

    def test_last_schedule_ui(self, navigator_with_schedules):
        nav = navigator_with_schedules
        nav.current_index = nav.available_count - 1
        nav.update_display()
        assert nav.info_label.text() == f"Schedule {nav.available_count} of {nav.available_count}"
        assert nav.prev_btn.isEnabled()
        assert not nav.next_btn.isEnabled()

    def test_no_schedules_ui(self, navigator_with_no_schedules):
        nav = navigator_with_no_schedules
        nav.update_display()
        assert nav.info_label.text() == "No schedules available"
        assert nav.schedule_num.text() == ""
        assert not nav.prev_btn.isEnabled()
        assert not nav.next_btn.isEnabled()
