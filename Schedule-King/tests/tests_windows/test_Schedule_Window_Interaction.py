"""
Integration tests for ScheduleWindow interaction using qtbot.

Covers:
- Clicking export button triggers file dialog and calls controller.
- Clicking back button triggers navigation callback.
- Entering invalid schedule index shows a warning.
- Entering valid schedule index updates schedule via signal.
- Performance and UI response with large schedule files.
- Ranking controls interaction and preference changes.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from PyQt5.QtCore import Qt
from src.views.schedule_window import ScheduleWindow
from src.models.schedule import Schedule

# --- Fixtures ---

@pytest.fixture
def mock_controller():
    """
    Create a mock controller with necessary methods.
    """
    ctrl = MagicMock()
    ctrl.export_schedules = MagicMock()
    ctrl.get_kth_schedule = MagicMock(return_value=Schedule([]))
    ctrl.set_preference = MagicMock()
    ctrl.clear_preference = MagicMock()
    ctrl.schedules = 3  # Add schedules attribute
    
    # Mock the ranker
    ctrl.ranker = MagicMock()
    ctrl.ranker.size = MagicMock(return_value=3)
    ctrl.ranker.get_ranked_schedules = MagicMock(return_value=[Schedule([])])
    
    return ctrl

@pytest.fixture
def window_with_qtbot(qtbot, mock_controller):
    """
    Create a ScheduleWindow with mock controller and attach it to qtbot.
    """
    window = ScheduleWindow(mock_controller)
    qtbot.addWidget(window)
    # Set up some dummy schedules
    window.displaySchedules(3)
    # Reset mock call counts after setup
    mock_controller.get_kth_schedule.reset_mock()
    mock_controller.export_schedules.reset_mock()
    return window

# --- Tests ---

class TestScheduleWindowQtBot:
    """
    Qt interaction tests for ScheduleWindow using qtbot.
    """

    def test_click_export_success(self, qtbot, window_with_qtbot):
        """
        Clicking export triggers file dialog and calls controller.
        """
        # Set up the current schedule and export controls state
        window_with_qtbot.current_schedule = Schedule([])
        window_with_qtbot.schedules = 3
        window_with_qtbot.navigator.current_index = 0
        
        # Update export controls with current state
        window_with_qtbot.header.export_controls.update_data(0)
        window_with_qtbot.header.export_controls.current_index = 0
        window_with_qtbot.header.export_controls.size = 3
        
        with patch("src.views.schedule_window.QFileDialog.getSaveFileName", return_value=("/tmp/test.txt", "")):
            # Reset mock before test
            window_with_qtbot.controller.export_schedules.reset_mock()
            # Click export button
            qtbot.mouseClick(window_with_qtbot.export_button, Qt.LeftButton)
            # Verify controller was called
            window_with_qtbot.controller.export_schedules.assert_called_once()

    def test_click_back_triggers_callback(self, qtbot, window_with_qtbot):
        """
        Clicking back should invoke the on_back callback.
        """
        window_with_qtbot.on_back = MagicMock()
        qtbot.mouseClick(window_with_qtbot.back_button, Qt.LeftButton)
        window_with_qtbot.on_back.assert_called_once()

    def test_invalid_schedule_index_handling(self, qtbot, window_with_qtbot):
        """
        Test handling of invalid schedule indices.
        """
        # Reset mock before test
        window_with_qtbot.controller.get_kth_schedule.reset_mock()
        # Test with index out of bounds
        window_with_qtbot.schedules = 3  # Set valid schedule count
        window_with_qtbot.on_schedule_changed(999)
        window_with_qtbot.controller.get_kth_schedule.assert_not_called()

    def test_valid_schedule_index_updates_display(self, qtbot, window_with_qtbot):
        """
        Test that valid schedule index updates the display correctly.
        """
        # Reset mock before test
        window_with_qtbot.controller.get_kth_schedule.reset_mock()
        # Set valid schedule count
        window_with_qtbot.schedules = 3
        window_with_qtbot.on_schedule_changed(0)
        window_with_qtbot.controller.get_kth_schedule.assert_called_once_with(0)

    def test_ranking_controls_preference_change(self, qtbot, window_with_qtbot):
        """
        Test that changing ranking preferences updates the controller.
        """
        # Reset mocks before test
        window_with_qtbot.controller.set_preference.reset_mock()
        window_with_qtbot.controller.clear_preference.reset_mock()
        
        # Test setting a preference
        window_with_qtbot.ranking_controls.preference_changed.emit("conflicts", True)
        window_with_qtbot.controller.set_preference.assert_called_once_with("conflicts", True)

        # Test clearing a preference - use False instead of None for boolean parameter
        window_with_qtbot.ranking_controls.preference_changed.emit(None, False)
        window_with_qtbot.controller.clear_preference.assert_called_once()

    def test_ranking_controls_refresh_schedule(self, qtbot, window_with_qtbot):
        """
        Test that changing preferences refreshes the current schedule display.
        """
        # Set up initial state
        window_with_qtbot.navigator.current_index = 0
        window_with_qtbot.schedules = 3
        window_with_qtbot.controller.get_kth_schedule.reset_mock()

        # Change preference
        window_with_qtbot.ranking_controls.preference_changed.emit("conflicts", True)
        
        # Verify schedule was refreshed
        window_with_qtbot.controller.get_kth_schedule.assert_called_once_with(0)

    # --- Performance / Large data tests ---

    def test_large_schedule_list_response_time(self, qtbot, mock_controller):
        """
        Load large number of schedules and measure UI update time.
        """
        start = time.perf_counter()
        window = ScheduleWindow(mock_controller)
        qtbot.addWidget(window)
        window.displaySchedules(10000)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000
        print(f"Loaded 10,000 schedules in {elapsed_ms:.2f} ms")
        assert elapsed_ms < 1500, "UI initialization took too long for large schedule list"

    def test_navigation_performance_on_large_input(self, qtbot, mock_controller):
        """
        Measure the response time of jumping to a late schedule in a large list.
        """
        window = ScheduleWindow(mock_controller)
        qtbot.addWidget(window)
        window.displaySchedules(10000)
        
        start = time.perf_counter()
        window.on_schedule_changed(9000)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 500, "Navigation took too long on large input"
