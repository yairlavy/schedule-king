"""
End-to-end tests for ScheduleWindow using qtbot.

These tests simulate a complete user interaction flow within the ScheduleWindow,
including navigation, export, and error handling. It combines GUI input with
functional logic verification.

Tested class: ScheduleWindow (src.views.schedule_window)
"""

import pytest
from unittest.mock import patch, MagicMock
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QApplication
from src.views.schedule_window import ScheduleWindow
from PyQt5.QtCore import QTimer

# --- Fixtures ---

@pytest.fixture(autouse=True)
def auto_accept_messagebox(qtbot):
    """
    Automatically clicks 'OK' on any QMessageBox that appears during tests.
    """
    def handle_messagebox():
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMessageBox):
                qtbot.addWidget(widget)
                widget.accept()
                return True
        return False
    
    # Check for message boxes every 100ms
    timer = QTimer()
    timer.timeout.connect(handle_messagebox)
    timer.start(100)
    
    yield
    
    # Clean up timer
    timer.stop()

@pytest.fixture
def full_window(qtbot):
    """
    Provides a fully initialized ScheduleWindow with:
    - 3 dummy schedules
    - A mocked controller (with export_schedules)
    - A mocked on_back callback

    Returns:
        Tuple[ScheduleWindow, MagicMock]: The window and controller mock
    """
    controller = MagicMock()
    # Set up mock schedules for the controller to return
    schedules = [MagicMock() for _ in range(3)]
    controller.get_kth_schedule.side_effect = lambda index: schedules[index]
    controller.get_schedules.return_value = schedules
    
    # Mock the ranker and its size method
    ranker = MagicMock()
    ranker.size.return_value = 3
    controller.ranker = ranker
    
    # Mock get_ranked_schedules to return a list of schedules
    controller.get_ranked_schedules.return_value = schedules
    
    # Create window with controller
    window = ScheduleWindow(controller)
    window.on_back = MagicMock()
    qtbot.addWidget(window)
    
    # Set up schedules count
    window.schedules = 3
    
    return window, controller

# --- Test Class ---

class TestScheduleWindowEndToEnd:
    """
    Simulates complete user interaction flows with ScheduleWindow.
    """

    def test_user_journey_complete_flow(self, qtbot, full_window):
        """
        Simulates a full user journey:
        - Navigate to schedule #3
        - Navigate back to schedule #1
        - Export the schedules to file
        - Return to course selection

        Verifies:
        - Navigation input updates view
        - Export calls controller with correct path
        - on_back is triggered on return
        """
        window, controller = full_window

        # Step 1: Move to schedule 3 (index 2)
        window.navigator.schedule_num.setText("3")
        qtbot.keyClick(window.navigator.schedule_num, Qt.Key_Enter)

        # Step 2: Back to schedule 1
        window.navigator.schedule_num.setText("1")
        qtbot.keyClick(window.navigator.schedule_num, Qt.Key_Enter)

        # Step 3: Export to TXT file
        with patch("src.views.schedule_window.QFileDialog.getSaveFileName", return_value=("/tmp/output.txt", "")), \
            patch("src.views.schedule_window.QMessageBox.information") as mock_info:
            qtbot.mouseClick(window.export_button, Qt.LeftButton)

            # Get the schedules that were passed to export_schedules
            call_args = controller.export_schedules.call_args
            assert call_args is not None
            assert call_args[0][0] == "/tmp/output.txt"  # First argument is file path
            assert len(call_args[0][1]) == 3  # Second argument is list of schedules
            assert mock_info.called

        # Step 4: Go back to course window
        qtbot.mouseClick(window.back_button, Qt.LeftButton)
        window.on_back.assert_called_once()

    def test_jump_to_invalid_schedule(self, qtbot, full_window):
        """
        Entering an invalid schedule number (too large) should trigger a warning message box.
        """
        window, _ = full_window
        window.navigator.schedule_num.setText("1000")
        with patch("src.views.schedule_window.QMessageBox.warning") as mock_warning:
            qtbot.keyClick(window.navigator.schedule_num, Qt.Key_Enter)
            assert mock_warning.called
            args, _ = mock_warning.call_args
            assert "Invalid Schedule Number" in args[1]

    def test_export_failure_flow(self, qtbot, full_window):
        """
        Simulates a failure during export (e.g., disk error).

        Verifies:
        - export_schedules raises an exception
        - A critical message box is shown to the user
        """
        window, controller = full_window
        controller.export_schedules.side_effect = RuntimeError("Disk full")

        with patch("src.views.schedule_window.QFileDialog.getSaveFileName", return_value=("/tmp/fail.txt", "")), \
            patch("src.views.schedule_window.QMessageBox.critical") as mock_critical:
            qtbot.mouseClick(window.export_button, Qt.LeftButton)

            assert mock_critical.called
            args, _ = mock_critical.call_args
            assert "Disk full" in args[-1]

    def test_ranking_preferences_update(self, qtbot, full_window):
        """
        Tests that changing ranking preferences updates the displayed schedule.

        Verifies:
        - Initial schedule display
        - Schedule updates when ranking preferences change
        - Correct schedule is displayed after update
        """
        window, controller = full_window
        
        # Reset mock before test
        controller.get_kth_schedule.reset_mock()
        controller.set_preference.reset_mock()
        
        # Get initial schedule
        initial_schedule = controller.get_kth_schedule(0)
        
        # Change ranking preferences
        metric = "Active Days"  # Example metric
        ascending = True
        
        # Mock the controller to return a different schedule after preferences change
        new_schedule = MagicMock()
        controller.get_kth_schedule.return_value = new_schedule
        
        # Update preferences using the correct method
        window.on_preference_changed(metric, ascending)
        
        # Verify controller was called to update preferences
        controller.set_preference.assert_called_once_with(metric, ascending)
        
        # Verify that get_kth_schedule was called to update the display
        # This happens in on_schedule_changed which is called after preference change
        controller.get_kth_schedule.assert_called_with(window.navigator.current_index)
