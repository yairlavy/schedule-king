import pytest
from unittest.mock import MagicMock, call
from PyQt5.QtWidgets import QApplication, QWidget
import sys

from src.views.schedule_window import ScheduleWindow
from src.models.schedule import Schedule

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
    ctrl = MagicMock(name="ScheduleController")
    # Add necessary mock methods and attributes
    ctrl.on_schedules_generated = None
    ctrl.on_progress_updated = None
    ctrl.get_kth_schedule = MagicMock(return_value=Schedule([]))
    ctrl.set_preference = MagicMock()
    ctrl.clear_preference = MagicMock()
    ctrl.ranker = MagicMock()
    ctrl.ranker.size = MagicMock(return_value=3)
    ctrl.ranker.get_ranked_schedules = MagicMock(return_value=[Schedule([])])
    return ctrl

@pytest.fixture
def mock_schedule():
    """Returns a mocked Schedule object with empty lecture_groups."""
    s = MagicMock(name="Schedule")
    s.lecture_groups = []
    return s

# ---------------------- Tests for displaySchedules ----------------------

class TestScheduleWindowDisplaySchedules:

    @pytest.fixture
    def window(self, qapp, qtbot, mock_schedule_controller):
        """
        Provides a fully initialized ScheduleWindow instance
        for displaySchedules-related tests.
        """
        win = ScheduleWindow(mock_schedule_controller)
        qtbot.addWidget(win)
        # Mock export controls to handle update_data correctly
        win.header.export_controls.update_data = MagicMock()
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

        assert window.schedules == schedules  # Should be the actual list of schedules
        window.navigator.set_schedules.assert_called_once_with(schedules)
        window.on_schedule_changed.assert_called_once_with(0)

    def test_update_with_empty_list(self, window):
        """
        Test displaySchedules with an empty list. Ensures schedule_table is cleared.
        """
        window.navigator.set_schedules = MagicMock()
        window.on_schedule_changed = MagicMock()
        window.schedule_table.clearContents = MagicMock()
        window.header.export_controls.update_data = MagicMock()

        window.displaySchedules([])

        assert window.schedules == []  # Should be an empty list
        window.navigator.set_schedules.assert_called_once_with([])
        window.on_schedule_changed.assert_not_called()
        window.schedule_table.clearContents.assert_called_once()
        window.header.export_controls.update_data.assert_called_once_with([], 0)

# ---------------------- Tests for on_schedule_changed ----------------------

class TestScheduleWindowOnScheduleChanged:

    @pytest.fixture
    def window_with_table(self, qapp, qtbot, monkeypatch, mock_schedule_controller):
        """
        Provides a ScheduleWindow instance with a patched dummy ScheduleTable.
        This isolates the test from the real GUI rendering.
        """
        class DummyScheduleTable(QWidget):
            def __init__(self):
                super().__init__()
                self.display_schedule = MagicMock()

        # Create a list of mock schedules for the controller to return
        schedules = [MagicMock() for _ in range(3)]
        
        # Configure the mock controller to return the correct schedule
        mock_schedule_controller.get_kth_schedule.side_effect = lambda index: schedules[index]
        mock_schedule_controller.get_schedules.return_value = schedules

        monkeypatch.setattr("src.views.schedule_window.ScheduleTable", lambda: DummyScheduleTable())
        win = ScheduleWindow(mock_schedule_controller)
        qtbot.addWidget(win)
        # Set up schedules count
        win.schedules = 3  # Set the count of schedules
        return win

    def test_valid_index(self, window_with_table):
        """
        Ensure that selecting a valid index triggers display_schedule
        for the corresponding schedule.
        """
        window_with_table.on_schedule_changed(1)
        window_with_table.controller.get_kth_schedule.assert_called_once_with(1)

    def test_invalid_index(self, window_with_table):
        """
        Ensure that an invalid index (too high) does not trigger a new display call.
        """
        window_with_table.controller.get_kth_schedule.reset_mock()
        window_with_table.on_schedule_changed(10)
        window_with_table.controller.get_kth_schedule.assert_not_called()

# ---------------------- Tests for ranking controls ----------------------

class TestScheduleWindowRankingControls:

    @pytest.fixture
    def window_with_ranking(self, qapp, qtbot, mock_schedule_controller):
        """
        Provides a ScheduleWindow instance with ranking controls for testing.
        """
        win = ScheduleWindow(mock_schedule_controller)
        qtbot.addWidget(win)
        # Set up schedules count
        win.schedules = 3  # Set the count of schedules
        return win

    def test_set_preference(self, window_with_ranking):
        """
        Test that setting a ranking preference updates the controller.
        """
        # Reset mock before test
        window_with_ranking.controller.set_preference.reset_mock()

        # Set a preference
        window_with_ranking.on_preference_changed("conflicts", True)

        # Verify controller was called with correct arguments
        window_with_ranking.controller.set_preference.assert_called_once_with("conflicts", True)

    def test_clear_preference(self, window_with_ranking):
        """
        Test that clearing a preference calls the controller's clear_preference method.
        """
        # Reset mock before test
        window_with_ranking.controller.clear_preference.reset_mock()

        # Clear preference
        window_with_ranking.on_preference_changed(None, False)

        # Verify controller's clear_preference was called
        window_with_ranking.controller.clear_preference.assert_called_once()

    def test_preference_refreshes_schedule(self, window_with_ranking):
        """
        Test that changing preferences refreshes the current schedule display.
        """
        # Set up initial state
        window_with_ranking.navigator.current_index = 0
        window_with_ranking.schedules = 3  # Set the count of schedules
        window_with_ranking.controller.get_kth_schedule.reset_mock()

        # Change preference
        window_with_ranking.on_preference_changed("conflicts", True)

        # Verify that the schedule was refreshed
        window_with_ranking.controller.get_kth_schedule.assert_called_once_with(0)

# ---------------------- Test for __init__ ----------------------

class TestScheduleWindowInit:
    def test_init_basic(self, qapp, qtbot, mock_schedule_controller):
        """
        Basic test to verify ScheduleWindow initializes with all expected attributes.
        """
        win = ScheduleWindow(mock_schedule_controller)
        qtbot.addWidget(win)

        assert win.windowTitle() == "Schedule King"
        assert callable(win.on_back)
        assert hasattr(win, "navigator")
        assert hasattr(win, "schedule_table")
        assert hasattr(win, "ranking_controls")
        assert hasattr(win, "header")
        assert hasattr(win, "metrics_widget")
