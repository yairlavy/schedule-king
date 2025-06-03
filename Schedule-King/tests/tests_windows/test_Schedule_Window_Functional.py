import pytest
from unittest.mock import MagicMock, call
from PyQt5.QtWidgets import QApplication, QWidget
import sys

from src.views.schedule_window import ScheduleWindow

# ---------------------- Fixtures ----------------------

@pytest.fixture(scope="module")
def qapp():
    """
    Create or reuse a QApplication instance for Qt GUI tests.
    This ensures PyQt widgets can be instantiated safely during tests.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

@pytest.fixture
def mock_schedule_controller():
    """Returns a mocked ScheduleController."""
    return MagicMock(name="ScheduleController")

@pytest.fixture
def mock_schedule():
    """Returns a mocked Schedule object with empty lecture_groups."""
    s = MagicMock(name="Schedule")
    s.lecture_groups = []
    return s

# ---------------------- Tests for displaySchedules ----------------------

class TestScheduleWindowDisplaySchedules:

    @pytest.fixture
    def window(qapp, qtbot, mock_schedule_controller, mock_schedule):
        """
        Provides a fully initialized ScheduleWindow instance
        for displaySchedules-related tests.
        """
        win = ScheduleWindow([mock_schedule], mock_schedule_controller)
        qtbot.addWidget(win)
        return win

    def test_update_with_non_empty_schedules(self, window):
        """
        Test displaySchedules with a valid non-empty schedule list.
        Ensures the schedules list is updated and navigator/table are refreshed.
        """
        window.navigator.set_schedules = MagicMock()
        window.on_schedule_changed = MagicMock()
        schedules = [MagicMock()]
        window.displaySchedules(schedules)

        assert window.schedules == schedules
        window.navigator.set_schedules.assert_called_once_with(schedules)
        window.on_schedule_changed.assert_called_once_with(0)

    def test_update_with_empty_list(self, window):
        """
        Test displaySchedules with an empty list. Ensures schedule_table is cleared.
        """
        window.navigator.set_schedules = MagicMock()
        window.on_schedule_changed = MagicMock()
        window.schedule_table.clearContents = MagicMock()

        window.displaySchedules([])

        assert window.schedules == []
        window.navigator.set_schedules.assert_called_once_with([])
        window.on_schedule_changed.assert_not_called()
        window.schedule_table.clearContents.assert_called_once()

# ---------------------- Tests for on_schedule_changed ----------------------

class TestScheduleWindowOnScheduleChanged:

    @pytest.fixture
    def window_with_table(qapp, qtbot, monkeypatch, mock_schedule_controller):
        """
        Provides a ScheduleWindow instance with a patched dummy ScheduleTable.
        This isolates the test from the real GUI rendering.
        """
        class DummyScheduleTable(QWidget):
            def __init__(self):
                super().__init__()
                self.display_schedule = MagicMock()

        # Create a list of mock schedules
        schedules = [MagicMock() for _ in range(3)]
        
        # Configure the mock controller to return the correct schedule
        mock_schedule_controller.get_kth_schedule.side_effect = lambda index: schedules[index]
        mock_schedule_controller.get_schedules.return_value = schedules

        monkeypatch.setattr("src.views.schedule_window.ScheduleTable", lambda: DummyScheduleTable())
        win = ScheduleWindow(schedules, mock_schedule_controller)
        qtbot.addWidget(win)
        return win

    def test_valid_index(self, window_with_table):
        """
        Ensure that selecting a valid index triggers display_schedule
        for the corresponding schedule.
        """
        window_with_table.on_schedule_changed(1)
        expected = call(window_with_table.schedules[1])
        assert expected in window_with_table.schedule_table.display_schedule.call_args_list

    def test_invalid_index(self, window_with_table):
        """
        Ensure that an invalid index (too high) does not trigger a new display call.
        """
        prev_calls = len(window_with_table.schedule_table.display_schedule.call_args_list)
        window_with_table.on_schedule_changed(10)
        assert len(window_with_table.schedule_table.display_schedule.call_args_list) == prev_calls

# ---------------------- Test for __init__ ----------------------

class TestScheduleWindowInit:
    def test_init_basic(self, qapp, qtbot, mock_schedule_controller, mock_schedule):
        """
        Basic test to verify ScheduleWindow initializes with all expected attributes.
        """
        win = ScheduleWindow([mock_schedule], mock_schedule_controller)
        qtbot.addWidget(win)

        assert win.windowTitle() == "Schedule King"
        assert callable(win.on_back)
        assert hasattr(win, "navigator")
        assert hasattr(win, "schedule_table")
