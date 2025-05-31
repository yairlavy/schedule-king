"""
Integration tests for ScheduleWindow interaction using qtbot.

Covers:
- Clicking export button triggers file dialog and calls controller.
- Clicking back button triggers navigation callback.
- Entering invalid schedule index shows a warning.
- Entering valid schedule index updates schedule via signal.
- Performance and UI response with large schedule files.
"""

import pytest
import time
from unittest.mock import patch, MagicMock
from PyQt5.QtCore import Qt
from src.views.schedule_window import ScheduleWindow

# --- Fixtures ---

@pytest.fixture
def mock_controller():
    """
    Create a mock controller with export_schedules method.
    """
    ctrl = MagicMock()
    ctrl.export_schedules = MagicMock()
    return ctrl

@pytest.fixture
def window_with_qtbot(qtbot, mock_controller):
    """
    Create a ScheduleWindow with 3 dummy schedules and attach it to qtbot.
    """
    schedules = [MagicMock() for _ in range(3)]
    window = ScheduleWindow(schedules, mock_controller)
    qtbot.addWidget(window)
    return window

# --- Tests ---

class TestScheduleWindowQtBot:
    """
    Qt interaction tests for ScheduleWindow using qtbot.
    """

    def test_click_export_success(self, qtbot, window_with_qtbot):
        """
        Clicking export triggers file dialog and success message.
        """
        with patch("src.views.schedule_window.QFileDialog.getSaveFileName", return_value=("/tmp/test.txt", "")), \
             patch("src.views.schedule_window.QMessageBox.information") as mock_info:
            qtbot.mouseClick(window_with_qtbot.export_button, Qt.LeftButton)
            window_with_qtbot.controller.export_schedules.assert_called_once()
            assert mock_info.called

    def test_click_back_triggers_callback(self, qtbot, window_with_qtbot):
        """
        Clicking back should invoke the on_back callback.
        """
        window_with_qtbot.on_back = MagicMock()
        qtbot.mouseClick(window_with_qtbot.back_button, Qt.LeftButton)
        window_with_qtbot.on_back.assert_called_once()

    def test_invalid_schedule_index_raises_warning_box(self, qtbot, window_with_qtbot):
        """
        Simulate entering a too-high index and pressing Enter.
        Should trigger a warning.
        """
        window_with_qtbot.navigator.schedule_num.setText("999")
        with patch("src.views.schedule_window.QMessageBox.warning") as mock_warn:
            qtbot.keyClick(window_with_qtbot.navigator.schedule_num, Qt.Key_Enter)
            assert mock_warn.called

    def test_valid_schedule_index_emits_signal(self, qtbot, window_with_qtbot):
        """
        Simulate entering a valid schedule number and check signal emission.
        """
        window_with_qtbot.navigator.schedule_num.setText("1")  # 1-based index
        received = []

        def handle_change(index):
            received.append(index)

        window_with_qtbot.navigator.schedule_changed.connect(handle_change)
        qtbot.keyClick(window_with_qtbot.navigator.schedule_num, Qt.Key_Enter)

        assert received == [0]

    # --- Performance / Large data tests ---

    def test_large_schedule_list_response_time(self, qtbot, mock_controller):
        """
        Load 10,000 schedules and measure UI update time.
        This test ensures acceptable response time when handling large inputs.
        """
        large_schedules = [MagicMock() for _ in range(10_000)]
        start = time.perf_counter()
        window = ScheduleWindow(large_schedules, mock_controller)
        qtbot.addWidget(window)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000
        print(f"Loaded 10,000 schedules in {elapsed_ms:.2f} ms")
        assert elapsed_ms < 1500, "UI initialization took too long for large schedule list"

    def test_navigation_performance_on_large_input(self, qtbot, mock_controller):
        """
        Measure the response time of jumping to schedule 9000 in a large list.
        """
        schedules = [MagicMock() for _ in range(10000)]
        window = ScheduleWindow(schedules, mock_controller)
        qtbot.addWidget(window)
        window.navigator.schedule_num.setText("9000")
        start = time.perf_counter()
        qtbot.keyClick(window.navigator.schedule_num, Qt.Key_Enter)
        end = time.perf_counter()
        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 500, "Navigation took too long on large input"
